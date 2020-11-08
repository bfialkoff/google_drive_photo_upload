Auto Photo Upload
-------

This project is based on [PyDrive](https://github.com/googleworkspace/PyDrive).
It provides a simple framwork for uploading and cataloging images to your google drive

Features
-------------------

-  Automates OAuth2.0 into just few lines with flexible settings.
-  Wraps [PyDrive](https://github.com/googleworkspace/PyDrive). for simple usage

Setup
--------------

Simply clone this repository and install the `requirements.txt`. Follow the instructions [PyDrive](https://github.com/googleworkspace/PyDrive) here to enable Google Cloud APIs and to get credentials

OAuth made easy
---------------

OAuth2.0 is done in two lines.Simply download `client\_secrets.json1 from the Google API Console and follow the instructions to fill out the appropriate fields in `settings.yaml`.

Photo ordering made easy
---------------
Simply paste your unordered photos in `unprocessed` and run `main.py`.  After completeign authorization the photos will be uploaded into a convenenient folder structure by year and month.  
The photos are assumed either to contain an 8 digit capture date in its file name, otherwise the year 0000 is chose and month 00.

To Do
-----
- Try to read EXIF data if date isn't contained in name
- Create a Telegram bot to handle frontend, and recieve photos straight from mobile device
