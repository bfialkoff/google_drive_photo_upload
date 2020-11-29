Auto Photo Upload
-------

It contains the source code for a telegram bot that can be configured to autmatically upload photos to a google drive account. It uses [PyDrive](https://github.com/googleworkspace/PyDrive), [pymongo](https://github.com/mongodb/mongo-python-driver), and [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot/tree/master/examples).

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
- Improve logging to indicate to record actions, file uploads, new users, etc, set up another DB
- Implement functionality for working with video
