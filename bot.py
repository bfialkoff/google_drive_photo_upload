""" todo
- something about storage root name
- something about updating photo root
- clear auth
"""
import logging

from telegram import ReplyKeyboardRemove, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext

from settings.example_credentials import url_host, telegram_token
from utils.mongo_driver import MongoDriver
from utils.onboarding import OnBoarding
from utils.photo_handler import PhotoHandler
from utils.configs import *
from utils.messages import *

m_driver = MongoDriver()

mkdir = lambda p: p.mkdir(parents=True) if not p.exists() else None

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)


logger = logging.getLogger(__name__)



def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(operation_cancelled_message, reply_markup=ReplyKeyboardRemove())
    # store user context data in db
    return ConversationHandler.END

def delete_user(update, context):
    user = update.message.from_user
    m_driver.remove_user_data(user.id)
    update.message.reply_text(auth_revoked_message,reply_markup=ReplyKeyboardRemove())


def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


def main() -> None:
    updater = Updater(telegram_token)

    # containes methods for handling the onboarding flow
    onboarder = OnBoarding(m_driver)

    #contains methods for handling photo upload flows
    photo_handler = PhotoHandler(m_driver, logger)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # define a handler to implement the onboarding flow
    setup_handler = ConversationHandler(
        entry_points=[CommandHandler('start', onboarder.start)],
        states={ACCESS_CODE: [MessageHandler(Filters.text, onboarder.access_code)],
                PHOTO_STORE_ROOT: [MessageHandler(Filters.text, photo_handler.photo_store_root)]},
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # define a handler to allow for upload location changes
    update_photo_root_handler = ConversationHandler(
        entry_points=[CommandHandler('update_photo_root', photo_handler.update_photo_root_entry),
                      #MessageHandler(Filters.text, update_photo_root) # todo accept as message
                      ],
        states={PHOTO_STORE_ROOT: [MessageHandler(Filters.text, photo_handler.update_photo_root)]},
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # define a handler to upload photos after onboarding independant of any flow
    photo_handler = MessageHandler(Filters.document & (~ Filters.photo), photo_handler.upload_photo)

    # define a handler to delete user info and revoke access
    delete_user_handler = CommandHandler('delete', delete_user)

    # define an uplaod handler so people dont feel ignored
    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)


    # add the handler to the dispatcher
    dispatcher.add_handler(setup_handler)
    dispatcher.add_handler(update_photo_root_handler)
    dispatcher.add_handler(photo_handler)
    dispatcher.add_handler(delete_user_handler)
    dispatcher.add_handler(echo_handler)

    # Start the Bot
    updater.start_polling()
    updater.start_webhook(listen="0.0.0.0", port=int(os.environ.get('PORT', 5000)), url_path=telegram_token)
    updater.bot.set_webhook(url_host + telegram_token)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
