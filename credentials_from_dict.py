import json
import os
import threading

from oauth2client import _helpers
from oauth2client import client


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
        # todo save to db

    def locked_delete(self):
        """Delete Credentials file.

        Args:
            credentials: Credentials, the credentials to store.
        """
        raise NotImplementedError
