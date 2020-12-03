Auto Photo Upload
-------

This project contains the source code for a telegram bot that can be configured to automatically upload photos to a google drive account. It uses [PyDrive](https://github.com/googleworkspace/PyDrive), [pymongo](https://github.com/mongodb/mongo-python-driver), and [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot/tree/master/examples). A live version of this bot can be found [Here](https://t.me/violetlogitbot).

Setup
--------------

Simply clone this repository and install the `requirements.txt`.  
Follow the instructions 
 - [PyDrive](https://github.com/googleworkspace/PyDrive) to enable Google Cloud APIs and to get credentials
 - [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) to get your own bot set up
 - [pymongo](https://github.com/mongodb/mongo-python-driver) and [MongoDB](https://www.mongodb.com/) to setup a database.


To Do
-----
- Try to read EXIF data if date isn't contained in file name
- Move to PyDrive2 for better support, better yet stop using an API wrapper
- Improve logging to indicate to record actions, file uploads, new users, etc, set up another DB
- Implement functionality for working with video
