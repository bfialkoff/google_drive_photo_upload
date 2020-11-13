import pickle
from pathlib import Path

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

google_folder = 'application/vnd.google-apps.folder'

def save_driver(driver, dir):
    drive_path = dir.joinpath('driver.pkl').resolve()
    with open(drive_path, 'wb') as f:
        pickle.dump(driver, f)

def load_driver(dir, settings_file):
    drive_path = dir.joinpath('driver.pkl').resolve()
    with open(drive_path, 'rb') as f:
        g_driver = pickle.load(f)
    g_driver.refresh(settings_file)
    return g_driver

class GoogleDriver:
    def __init__(self, g_login, auth_code, credentials_file):
        self.credentials_file =  credentials_file
        self.driver = self.get_driver(g_login, auth_code, self.credentials_file)


    def refresh(self, settings_file):
        g_login = GoogleAuth(settings_file)
        g_login.LoadCredentialsFile(credentials_file=self.credentials_file)

        if g_login.access_token_expired:
            g_login.Refresh()
        else:
            g_login.Authorize()

        # Save the current credentials to a file
        g_login.SaveCredentialsFile(credentials_file=self.credentials_file)

        self.driver = GoogleDrive(g_login)



    def get_driver(self, g_login, auth_code, credentials_file):
        g_login.LoadCredentialsFile(credentials_file=credentials_file)

        if g_login.credentials is None:
            g_login.Auth(auth_code)
        elif g_login.access_token_expired:
            g_login.Refresh()
        else:
            g_login.Authorize()

        # Save the current credentials to a file
        g_login.SaveCredentialsFile(credentials_file=credentials_file)


        driver = GoogleDrive(g_login)
        return driver

    def id2name(self, id):
        q = {'q': f"'root' in parents and trashed=false and mimeType='{google_folder}'"}
        file_list = self.driver.ListFile(q).GetList()
        name = None
        for i, f in enumerate(file_list):
            if f['id'] == id:
                name = f['title']
                break
        return name

    def name2id(self, parent, name):
        # searches for the id of the folder called name in
        # the parent directory parent, returns None if subfolder doesnt exist
        q = {'q': f"'{parent}' in parents and trashed=false and mimeType='{google_folder}'"}
        file_list = self.driver.ListFile(q).GetList()
        id = None
        for i, f in enumerate(file_list):
            if f['title'] == name:
                id = f['id']
                break
        return id

    def mk_google_dir(self, parent_dir_id, dirname):
        # creates a google drive subfolder called dirname inside the directory indicated by parent_dir_id
        folder_id = self.name2id(parent_dir_id, dirname)
        if folder_id is None:
            params = {'title': dirname,
                      'parents': [{'id': parent_dir_id}],
                      'mimeType': google_folder
                      }
            file = self.driver.CreateFile(params)
            file.Upload()
            folder_id = file['id']
        return folder_id

    def upload_file(self, file_handler, dst_id):
        params = {'title': file_handler.name,
                  #'mimeType': google_photo,
                  'parents': [{'id': dst_id}]}
        file = self.driver.CreateFile(params)
        file.SetContentFile(str(file_handler.file_name))
        file.Upload()
        file_id = file['id']
        return file_id