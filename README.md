Auto Photo Upload
-------

This project is based on [PyDrive](https://github.com/googleworkspace/PyDrive).
It provides a simple framwork for uploading and cataloging images to your google drive

Features
-------------------

-  Automates OAuth2.0 into just few lines with flexible settings.
-  Wraps [PyDrive](https://github.com/googleworkspace/PyDrive). for simple usage

How to install
--------------

Simply clone this repository and install the `requirements.txt`

OAuth made easy
---------------

OAuth2.0 is done in two lines.Simply download `client\_secrets.json1 from the Google API Console and follow the instructions to fill out the appropriate fields in `settings.yaml`.

Photo ordering made easy
---------------
Simply paste your unordered photos in `unprocessed` and run `main.py`. After completeign authorization the photos will be uploaded into a convenenient folder structure by year and month. 
