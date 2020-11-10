from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

google_folder = 'application/vnd.google-apps.folder'

class GoogleDriver:
    def __init__(self, settings_files):
        self.driver = self.get_driver(settings_files)

    def get_driver(self, settings_file):
        # handles auth flow
        g_login = GoogleAuth(settings_file)
        auth_url = g_login.GetAuthUrl()
        # Try to load saved client credentials
        g_login.LoadCredentialsFile()

        if g_login.credentials is None:
            g_login.GetFlow()
            g_login.flow.params.update({'access_type': 'offline', 'approval_prompt': 'force'})

            # prompt user to visit url and return code
            g_login.LocalWebserverAuth()

        elif g_login.access_token_expired:
            # Refresh them if expired
            g_login.Refresh()
        else:
            # Initialize the saved creds
            g_login.Authorize()
        # Save the current credentials to a file
        g_login.SaveCredentialsFile()

        driver = GoogleDrive(g_login)
        return driver

    def find_subfolder_id(self, parent, name):
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
        folder_id = self.find_subfolder_id(parent_dir_id, dirname)
        if folder_id is None:
            params = {'title': dirname, 'parents': [{'id': parent_dir_id}], 'mimeType': f'{google_folder}'}
            file = self.driver.CreateFile(params)
            file.Upload()
            folder_id = file['id']
        return folder_id

    def upload_file(self, file_handler, dst_id):
        params = {'title': file_handler.file_name, 'parents': [{'id': dst_id}]}
        file = self.driver.CreateFile(params)
        file.SetContentFile(file_handler.file_name)
        file.Upload()
        file_id = file['id']
        return file_id