import threading
import json

from pydrive.drive import GoogleDrive
from oauth2client import client

google_folder = 'application/vnd.google-apps.folder'
google_file = 'application/vnd.google-apps.file'


class CredentialsFromDict(client.Storage):
    """Store and retrieve a single credential to and from a file."""

    def __init__(self, filename=None, content=None):
        super(CredentialsFromDict, self).__init__(lock=threading.Lock())
        assert bool(filename) ^ bool(content)
        self._filename = filename
        self._content = bytes(json.dumps(content), 'utf-8') if content is not None else content

    def locked_get(self):
        """Retrieve Credential from file.

        Returns:
            oauth2client.client.Credentials

        Raises:
            IOError if the file is a symbolic link.
        """
        credentials = None

        try:
            credentials = client.Credentials.new_from_json(self._content)
            credentials.set_store(self)
        except ValueError:
            pass

        return credentials

    def locked_put(self, credentials):
        """Write Credentials to file.

        Args:
            credentials: Credentials, the credentials to store.

        Raises:
            IOError if the file is a symbolic link.
        """
        credentials_dict = credentials.to_json()

    def locked_delete(self):
        """Delete Credentials file.

        Args:
            credentials: Credentials, the credentials to store.
        """
        raise NotImplementedError


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

    def id2name(self, folder_name, id):
        q = {'q': f"title='{folder_name}'"}
        file_list = self.driver.ListFile(q).GetList()
        name = None
        for i, f in enumerate(file_list):
            if f['id'] == id:
                name = f['title']
                break
        return name

    def id2name_(self, id):
        q = {'p': f"'root' in parents and trashed=false and (mimeType='{google_folder}' or mimeType='{google_file}')"}
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
