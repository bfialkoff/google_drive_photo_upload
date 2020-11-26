import pymongo

mongodb_user = 'photo-bot'
mongodb_password = 'FncQJgTiklYIZBeo'
cluster_name = 'photo-app'
mongo_db_name = 'drive_bot'
collection = 'users'


class MongoDriver:
    def __init__(self):
        client = pymongo.MongoClient(
            f"mongodb+srv://{mongodb_user}:{mongodb_password}@cluster0.3zxzp.mongodb.net/{cluster_name}?retryWrites=true&w=majority")
        self.db = client[mongo_db_name][collection]


    def get_user_params(self, user_id):
        user_data = self.db.find_one({'user_id': user_id})
        return user_data

    def store_user_data(self, user_data):
        if bool(self.get_user_params(user_data['user_id'])):
            return
        self.db.insert_one(user_data)

if __name__ == '__main__':
    m_driver = MongoDriver()
    user_data = m_driver.get_user_params(2)

    if user_data is None:
        user_data = {'user': 2}
        x = m_driver.store_user_data(user_data)

    user_data = m_driver.get_user_params(2)

    print()
