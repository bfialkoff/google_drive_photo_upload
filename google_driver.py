"""
im trying to move to a model where all my data is stored in the context object and the database
to this end i need to store and retrieve the content of credentials.json in the db which means
i need to instantiate my driver with a json and not a path and integrate back into bot and stop saving to disk

"""
import pickle
import json
from pathlib import Path


from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from credentials_from_dict import CredentialsFromDict


google_folder = 'application/vnd.google-apps.folder'

def load_json(path):
    j = None
    with open(path, 'r') as f:
        j = json.load(f)
    return j

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
    def __init__(self, g_login, auth_code=None, credentials=None):
        self.credentials = credentials
        self.driver = self.get_driver(g_login, auth_code=auth_code, credentials=self.credentials)


    def get_driver(self, g_login, auth_code=None, credentials=None):
        """
        credentials is a dict of credentials
        """
        assert auth_code or credentials
        if bool(credentials):
            storage = CredentialsFromDict(content=credentials)
            g_login.credentials = storage.get()

        if g_login.credentials is None:
            g_login.Auth(auth_code)
        elif g_login.access_token_expired:
            g_login.Refresh()
        else:
            g_login.Authorize()

        driver = GoogleDrive(g_login)
        return driver

    def get_credentials(self):
        return json.loads(self.driver.auth.credentials.to_json())

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
                  'parents': [{'id': dst_id}]}
        file = self.driver.CreateFile(params)
        file.SetContentFile(str(file_handler.file_name))
        file.Upload()
        file_id = file['id']
        return file_id

if __name__ == '__main__':
    pass

