from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, CallbackContext

from utils.file_handler import FileHandler
from utils.configs import *
from utils.messages import *


class PhotoHandler:
    def __init__(self, m_driver, logger):
        self.m_driver = m_driver
        self.logger = logger

    def update_photo_root_entry(self, update: Update, context: CallbackContext):
        user = update.message.from_user
        if not bool(context.user_data):
            user_params = self.m_driver.get_user_params(user.id)
            if not bool(user_params):
                update.message.reply_text(
                    'Auth failed, trying sending /start again.', reply_markup=ReplyKeyboardRemove()
                )
                return ConversationHandler.END
            context = restore_state(user_params, context)
        update.message.reply_text(
            send_photo_id_message
        )
        update.message.reply_photo(open(folder_id_screenshot_path, 'rb'))
        return PHOTO_STORE_ROOT

    def handle_photo_store_loc(self, update: Update, context: CallbackContext):
        user = update.message.from_user
        try:
            folder_name, photo_store_root = update.message.text.split(',')
            photo_store_root = photo_store_root.strip()
        except:
            update.message.reply_text(file_id_format_error)
            return PHOTO_STORE_ROOT, context

        folder_name = context.user_data['driver'].id2name(folder_name, photo_store_root)
        if folder_name is None:
            update.message.reply_text(file_not_found_error(photo_store_root))
            return PHOTO_STORE_ROOT

        context.user_data['photo_store_root'] = photo_store_root
        context.user_data['folder_name'] = folder_name

        self.logger.info("User logged photo store %s.", photo_store_root)
        return user.id, context

    def update_photo_root(self, update: Update, context: CallbackContext):
        retval, context = self.handle_photo_store_loc(update, context)
        if retval == PHOTO_STORE_ROOT:
            return PHOTO_STORE_ROOT

        update.message.reply_text(
            f"Your photos will now be uploaded to {context.user_data['folder_name']}\n"
            , reply_markup=ReplyKeyboardRemove()
        )
        self.m_driver.update_photo_store_root(retval, photo_store_root)
        return ConversationHandler.END

    def photo_store_root(self, update: Update, context: CallbackContext) -> int:
        retval, context = self.handle_photo_store_loc(update, context)
        if retval == PHOTO_STORE_ROOT:
            return PHOTO_STORE_ROOT

        update.message.reply_text(
            onboarding_complete_message(context.user_data['folder_name']), reply_markup=ReplyKeyboardRemove()
        )

        user_data = {'user_id': retval,
                     'user_dir': str(context.user_data['user_dir']),
                     'photo_store_root': context.user_data['photo_store_root'],
                     'credentials': context.user_data['driver'].get_credentials()
                     }
        self.m_driver.store_user_data(user_data)
        return ConversationHandler.END

    def upload_photo(self, update: Update, context: CallbackContext) -> None:
        user = update.message.from_user

        # if context.user_data is {} try to load from db else user didnt auth properly
        if not bool(context.user_data):
            user_params = self.m_driver.get_user_params(user.id)
            if not bool(user_params):
                update.message.reply_text(auth_failed_message, reply_markup=ReplyKeyboardRemove())
                return ConversationHandler.END
            context = restore_state(user_params, context)

        g_driver = context.user_data['driver']
        file_name = update.message.document.file_name
        photo_dir = context.user_data['user_dir'].joinpath('tmp').resolve()
        file = photo_dir.joinpath(file_name)
        mkdir(photo_dir)

        photo_file = update.message.document.get_file()
        photo_file.download(file)

        self.logger.info("Photo of %s: %s", user.first_name, file_name)

        # now to FileHandler upload etc
        f_handler = FileHandler(file)

        pictures_id = context.user_data['photo_store_root']
        year_id = g_driver.mk_google_dir(pictures_id, f_handler.year)
        month_id = g_driver.mk_google_dir(year_id, f_handler.month)

        file_id = g_driver.upload_file(f_handler, month_id)

        update.message.reply_text(photo_uploaded_message)
        f_handler.cleanup()
