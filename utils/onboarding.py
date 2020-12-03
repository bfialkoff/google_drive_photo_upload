from pydrive.auth import GoogleAuth
from telegram import Update
from telegram.ext import ConversationHandler, CallbackContext

from utils.google_driver import GoogleDriver
from utils.configs import *
from utils.messages import *

class OnBoarding:

    def __init__(self, m_driver):
        self.m_driver = m_driver


    def start(self, update: Update, context: CallbackContext) -> int:
        user = update.message.from_user
        user_params = self.m_driver.get_user_params(user.id)
        if bool(user_params):
            update.message.reply_text(already_onboarded_message)
            return ConversationHandler.END

        g_login = GoogleAuth(settings_file)
        context.user_data['auth_object'] = g_login
        auth_url = g_login.GetAuthUrl()

        update.message.reply_text(
            follow_link_message + f'{auth_url}'
        )
        return ACCESS_CODE

    def access_code(self, update: Update, context: CallbackContext) -> int:
        user = update.message.from_user
        user_dir = credentials_dir.joinpath(f'{user.id}')
        mkdir(user_dir)
        user_credentials_file = user_dir.joinpath(f'{user.id}_credentials.json')
        auth_code = update.message.text

        g_driver = GoogleDriver(context.user_data['auth_object'], auth_code)

        context.user_data['driver'] = g_driver
        context.user_data['user_dir'] = user_dir
        context.user_data['credentials'] = user_credentials_file


        update.message.reply_text(send_photo_id_message)
        update.message.reply_photo(open(folder_id_screenshot_path, 'rb'))

        return PHOTO_STORE_ROOT
