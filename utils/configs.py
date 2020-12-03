from pathlib import Path

from pydrive.auth import GoogleAuth
from telegram.ext import CallbackContext

from utils.google_driver import GoogleDriver


ACCESS_CODE, PHOTO_STORE_ROOT = 0, 1
mkdir = lambda p: p.mkdir(parents=True) if not p.exists() else None

project_root = Path(__file__).joinpath('..', '..').resolve()
settings_file = project_root.joinpath('settings', 'dev_settings.yaml')
folder_id_screenshot_path = project_root.joinpath('settings', 'file_id_screenshot.png').resolve()

credentials_dir = project_root.joinpath('user_credentials').resolve()

def restore_state(user_params: dict, context: CallbackContext) -> CallbackContext:
    g_login = GoogleAuth(settings_file)
    g_driver = GoogleDriver(g_login, credentials=user_params['credentials'])

    context.user_data['auth_object'] = g_login
    context.user_data['driver'] = g_driver
    context.user_data['photo_store_root'] = user_params['photo_store_root']
    context.user_data['user_dir'] = Path(user_params['user_dir'])
    return context


