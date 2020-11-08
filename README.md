Auto Photo Upload
-------

This project is based on *PyDrive* which is a wrapper library of
`google-api-python-client <https://github.com/google/google-api-python-client>`
that simplifies many common Google Drive API tasks. It is a simple framwork for uploading and cataloging images to your google drive

Project Info
------------

- PyDrive Homepage: `https://pypi.python.org/pypi/PyDrive <https://pypi.python.org/pypi/PyDrive>`_

Features
-------------------

-  Automates OAuth2.0 into just few lines with flexible settings.
-  Wraps `PyDrive https://pypi.python.org/pypi/PyDrive <https://pypi.python.org/pypi/PyDrive>` for simple usage

How to install
--------------

Simply clone this repository and install the `requirements.txt`

OAuth made easy
---------------

OAuth2.0 is done in two lines.Simply ownload *client\_secrets.json* from the Google API Console and follow the instructions to fill out the appropriate fields in `settings.yaml`.

Photo ordering made easy
---------------
Simply paste your unordered photos in `unprocessed` and run `main.py`.  After completeign authorization the photos will be uploaded into a convenenient folder structure by year and month.  
The photos are assumed either to contain an 8 digit capture date in its file name, otherwise the year 0000 is chose and month 00.

To Do
-----
- Try to read EXIF data if date isn't contained in name
- Create a Telegram bot to handle frontend, and recieve photos straight from mobile device
