""" todo
i need to work on the flow here
- try to find a better solution to driver than global
	 maybe something like driver = GoogleDrive instead of None, and then later driver = driver(g_login) ? 
- i need settings per user... save_credentials_file, photo_store_root need to be set
- the whole /start situation is a mess... do this better
- something for viewing credentials
- something for modifying credentials
- something for handling photos

- test upload capabilities
"""

from pathlib import Path
import logging
import json

from pydrive.auth import GoogleAuth

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext

from google_driver import GoogleDriver, save_driver, load_driver
from file_handler import FileHandler
from settings.telegram_credentials import *

mkdir = lambda p: p.mkdir(parents=True) if not p.exists() else None

def save_json(j, path):
    if path.exists():
        j_ = load_json(path)
        j.update(j_)

    with open(path, 'w') as f:
        json.dump(j, f)

def load_json(path):
    with open(path, 'r') as f:
        j = json.load(f)
    return j

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

project_root = Path(__file__).joinpath('..').resolve()
settings_file = project_root.joinpath('settings', 'dev_settings.yaml')

credentials_dir = project_root.joinpath('user_credentials').resolve()

g_login = GoogleAuth(settings_file)
auth_url = g_login.GetAuthUrl()
g_driver = None

logger = logging.getLogger(__name__)

ACCESS_CODE, PHOTO_STORE_ROOT = 0, 1


def start(update: Update, context: CallbackContext) -> int:
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

    #logger.info("Gender of %s: %s", user.first_name, update.message.text)

    auth_code = update.message.text

    global g_driver
    g_driver = GoogleDriver(g_login, auth_code, user_credentials_file)
    save_driver(g_driver, user_dir)
    context.user_data['driver'] = g_driver
    update.message.reply_text(
        'Send the ID of the google drive folder you want to upload to.\n'
        'to find the id, simply open the destination folder on your google drive, the url will be of the form:\n'
        'https://drive.google.com/drive/u/4/folders/<root-folder-id-here>'
    )

    return PHOTO_STORE_ROOT


def photo_store_root(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    user_dir = credentials_dir.joinpath(f'{user.id}')
    user_data_path = user_dir.joinpath(f'{user.id}_data.json')
    photo_store_root = update.message.text
    # validate that id exists, else return PHOTO_STORE_ROOT, maybe confirm using folder name
    save_json({'photo_store_root': photo_store_root}, user_data_path)

    context.user_data['photo_store_root'] = photo_store_root
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Authorization granted.\n'
        f'Your photos will be uploaded to {g_driver.id2name(photo_store_root)}\n'
        'Note you must send your photos as a File attachment.\n'
        'This ensures the images wont be compressed and that\n'
        'The images can be archived correctly.', reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def upload_photo(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    user_dir = credentials_dir.joinpath(f'{user.id}')
    user_data_path = user_dir.joinpath(f'{user.id}_data.json')

    global g_driver
    if g_driver is None:
        try:
            g_driver = load_driver(user_dir, settings_file)
        except Exception as e:
            update.message.reply_text('cant access account, try running \start to restart onboarding')
            return ConversationHandler.END

    g_driver = context.user_data['g_driver']

    file_name = update.message.document.file_name
    photo_dir = user_dir.joinpath('tmp').resolve()
    file = photo_dir.joinpath(file_name)
    mkdir(photo_dir)

    photo_file = update.message.document.get_file()
    photo_file.download(file)

    logger.info("Photo of %s: %s", user.first_name, file_name)

    # now to FileHandler upload etc
    f_handler = FileHandler(file)

    #user_params = load_json(user_data_path)
    #pictures_id = user_params['photo_store_root']

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

    return ConversationHandler.END


def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


def main() -> None:
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(telegram_token)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    setup_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={ACCESS_CODE: [MessageHandler(Filters.text, access_code)],
                PHOTO_STORE_ROOT: [MessageHandler(Filters.text, photo_store_root)]},
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    photo_handler = MessageHandler(Filters.document & (~ Filters.photo), upload_photo)
    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(setup_handler)
    dispatcher.add_handler(photo_handler)
    dispatcher.add_handler(echo_handler)
    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
