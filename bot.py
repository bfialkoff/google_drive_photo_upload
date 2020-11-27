""" todo
- something about storage root name
- something about updating photo root
- clear auth
"""

from pathlib import Path
import logging

from pydrive.auth import GoogleAuth

from telegram import ReplyKeyboardRemove, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext

from google_driver import GoogleDriver
from file_handler import FileHandler
from settings.telegram_credentials import *
from mongo_driver import MongoDriver

m_driver = MongoDriver()

mkdir = lambda p: p.mkdir(parents=True) if not p.exists() else None

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

project_root = Path(__file__).joinpath('..').resolve()
settings_file = project_root.joinpath('settings', 'dev_settings.yaml')

credentials_dir = project_root.joinpath('user_credentials').resolve()

logger = logging.getLogger(__name__)
ACCESS_CODE, PHOTO_STORE_ROOT = 0, 1

def restore_state(user_params: dict, context: CallbackContext) -> CallbackContext:
    g_login = GoogleAuth(settings_file)
    g_driver = GoogleDriver(g_login, credentials=user_params['credentials'])

    context.user_data['auth_object'] = g_login
    context.user_data['driver'] = g_driver
    context.user_data['photo_store_root'] = user_params['photo_store_root']
    context.user_data['user_dir'] = Path(user_params['user_dir'])
    return context

# todo search db for user info do re-auth unless necessary
def start(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    user_params = m_driver.get_user_params(user.id)
    if bool(user_params):
        return ConversationHandler.END

    g_login = GoogleAuth(settings_file)
    context.user_data['auth_object'] = g_login
    auth_url = g_login.GetAuthUrl()

    update.message.reply_text(
        'Follow the link to grant the bot access to your google. Return the code.\n'
        f'{auth_url}'
    )
    return ACCESS_CODE


def access_code(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    user_dir = credentials_dir.joinpath(f'{user.id}')
    mkdir(user_dir)
    user_credentials_file = user_dir.joinpath(f'{user.id}_credentials.json')
    auth_code = update.message.text

    g_driver = GoogleDriver(context.user_data['auth_object'], auth_code)

    context.user_data['driver'] = g_driver
    context.user_data['user_dir'] = user_dir
    context.user_data['credentials'] = user_credentials_file

    update.message.reply_text(
        'Send the ID of the google drive folder you want to upload to.\n'
        'to find the id, simply open the destination folder on your google drive, the url will be of the form:\n'
        'https://drive.google.com/drive/u/4/folders/<root-folder-id-here>'
    )

    return PHOTO_STORE_ROOT

def update_photo_root_entry(update: Update, context: CallbackContext):
    user = update.message.from_user
    if not bool(context.user_data):
        user_params = m_driver.get_user_params(user.id)
        if not bool(user_params):
            update.message.reply_text(
                'Auth failed, trying sending /start again.', reply_markup=ReplyKeyboardRemove()
            )
            return ConversationHandler.END
        context = restore_state(user_params, context)
    update.message.reply_text(
        'Send the ID of the google drive folder you want to upload to.\n'
        'to find the id, simply open the destination folder on your google drive, the url will be of the form:\n'
        'https://drive.google.com/drive/u/4/folders/<root-folder-id-here>'
    )
    return PHOTO_STORE_ROOT

def update_photo_root(update: Update, context: CallbackContext):
    user = update.message.from_user
    photo_store_root = update.message.text
    # validate that id exists, else return PHOTO_STORE_ROOT, maybe confirm using folder name

    context.user_data['photo_store_root'] = photo_store_root

    logger.info("User logged photo store %s.", photo_store_root)

    update.message.reply_text(
        f"Your photos will now be uploaded to {context.user_data['driver'].id2name(photo_store_root)}\n"
        , reply_markup=ReplyKeyboardRemove()
    )
    m_driver.update_photo_store_root(user.id, photo_store_root)
    return ConversationHandler.END


def photo_store_root(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    photo_store_root = update.message.text

    folder_name = context.user_data['driver'].id2name(photo_store_root)
    if folder_name is None:
        update.message.reply_text(f'cannot find folder with id {photo_store_root}\n'
                                  'try again')
        return PHOTO_STORE_ROOT
    # validate that id exists, else return PHOTO_STORE_ROOT, maybe confirm using folder name

    context.user_data['photo_store_root'] = photo_store_root

    logger.info("User logged photo store %s.", photo_store_root)

    update.message.reply_text(
        'Authorization granted.\n'
        f"Your photos will be uploaded to {folder_name}\n"
        'Note you must send your photos as a File attachment.\n'
        'This ensures the images wont be compressed and that\n'
        'The images can be archived correctly.', reply_markup=ReplyKeyboardRemove()
    )

    user_data = {'user_id': user.id,
                 'user_dir': str(context.user_data['user_dir']),
                 'photo_store_root': context.user_data['photo_store_root'],
                 'credentials': context.user_data['driver'].get_credentials()
                 }
    m_driver.store_user_data(user_data)
    return ConversationHandler.END


def upload_photo(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user

    # if context.user_data is {} try to load from db else user didnt auth properly
    if not bool(context.user_data):
        user_params = m_driver.get_user_params(user.id)
        if not bool(user_params):
            update.message.reply_text(
                'Auth failed, trying sending /start again.', reply_markup=ReplyKeyboardRemove()
            )
            return ConversationHandler.END
        context = restore_state(user_params, context)

    g_driver = context.user_data['driver']
    file_name = update.message.document.file_name
    photo_dir = context.user_data['user_dir'].joinpath('tmp').resolve()
    file = photo_dir.joinpath(file_name)
    mkdir(photo_dir)

    photo_file = update.message.document.get_file()
    photo_file.download(file)

    logger.info("Photo of %s: %s", user.first_name, file_name)

    # now to FileHandler upload etc
    f_handler = FileHandler(file)

    pictures_id = context.user_data['photo_store_root']
    year_id = g_driver.mk_google_dir(pictures_id, f_handler.year)
    month_id = g_driver.mk_google_dir(year_id, f_handler.month)

    file_id = g_driver.upload_file(f_handler, month_id)

    update.message.reply_text('uploaded your photo')
    f_handler.cleanup()


def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove()
    )
    # store user context data in db
    return ConversationHandler.END

def delete_user(update, context):
    user = update.message.from_user
    m_driver.remove_user_data(user.id)
    update.message.reply_text(
        'You have revoked the bot\'s access to your google drive\n'
        'to continue using this bot send \start\n',
        reply_markup=ReplyKeyboardRemove()
    )
def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


def main() -> None:
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(telegram_token)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states
    setup_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={ACCESS_CODE: [MessageHandler(Filters.text, access_code)],
                PHOTO_STORE_ROOT: [MessageHandler(Filters.text, photo_store_root)]},
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    update_photo_root_handler = ConversationHandler(
        entry_points=[CommandHandler('update_photo_root', update_photo_root_entry),
                      #MessageHandler(Filters.text, update_photo_root)
                      ],
        states={PHOTO_STORE_ROOT: [MessageHandler(Filters.text, update_photo_root)]},
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    photo_handler = MessageHandler(Filters.document & (~ Filters.photo), upload_photo)
    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    delete_user_handler = CommandHandler('delete', delete_user)

    dispatcher.add_handler(setup_handler)
    dispatcher.add_handler(update_photo_root_handler)
    dispatcher.add_handler(photo_handler)
    dispatcher.add_handler(delete_user_handler)
    dispatcher.add_handler(echo_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
