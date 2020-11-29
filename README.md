Auto Photo Upload
-------

This project is based on [PyDrive](https://github.com/googleworkspace/PyDrive).  
It contains the source code for a telegram bot that can be configured
to autmotically upload photos to a google drive account.

Features
-------------------

-  Uses MongDB to store user data.
-  Automates OAuth2.0 for google drive access.
-  Wraps [PyDrive](https://github.com/googleworkspace/PyDrive).
-  Leverage python-telegram-bot for a convenient and easy to use frontend.

Setup
--------------

Simply clone this repository and install the `requirements.txt`.  
Follow the instructions [PyDrive](https://github.com/googleworkspace/PyDrive) here to enable Google Cloud APIs and to get credentials



To Do
-----
- Try to read EXIF data if date isn't contained in name
- Improve logging to indicate to record actions set up another DB
- Implement functionality for working with video
