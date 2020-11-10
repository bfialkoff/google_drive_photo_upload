""" todo
i need to work on the flow here
- try to find a better solution to driver than global
- the whole /start situation is a mess... do this better
- something for viewing credentials
- something for modifying credentials
- something for handling photos

- test upload capabilities
"""

from pathlib import Path
import logging

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext

from settings.telegram_credentials import *


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
project_root = Path(__file__).joinpath('..').resolve()

settings_file = project_root.joinpath('settings', 'dev_settings.yaml')

g_login = GoogleAuth(settings_file)
auth_url = g_login.GetAuthUrl()
driver = None

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
    logger.info("Gender of %s: %s", user.first_name, update.message.text)

    # handles auth flow
    # Try to load saved client credentials
    g_login.LoadCredentialsFile()

    if g_login.credentials is None:
        # figure out if this is necessary
        #g_login.GetFlow()
        #g_login.flow.params.update({'access_type': 'offline', 'approval_prompt': 'force'})

        g_login.Auth(update.message.text)
        print('something')
    elif g_login.access_token_expired:
        # Refresh them if expired
        g_login.Refresh()
    else:
        # Initialize the saved creds
        g_login.Authorize()
    # Save the current credentials to a file
    g_login.SaveCredentialsFile()

    global driver
    driver = GoogleDrive(g_login)

    update.message.reply_text(
        'Send the ID of the google drive folder you want to upload to.\n'
        'to find the id, right click on the folder you wish to upload, select share, the link will be of the form:\n'
        'https://drive.google.com/drive/folders/<root-folder-id-here>?usp=sharing'
    )

    return PHOTO_STORE_ROOT

def photo_store_root(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Got auth code and root id', reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

def photo(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('user_photo.jpg')
    logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')
    update.message.reply_text(
        'Gorgeous! Now, send me your location please, ' 'or send /skip if you don\'t want to.'
    )

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

    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(setup_handler)
    dispatcher.add_handler(echo_handler)
    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
