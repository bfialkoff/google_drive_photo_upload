import pymongo

from settings.example_credentials import mongo_db_name, mongodb_password, mongodb_user, collection, cluster_name


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

    def remove_user_data(self, user_id):
        num_removed = self.db.delete_many({'user_id': user_id})
        return num_removed

    def update_photo_store_root(self, user_id, new_photo_store_root):
        self.db.update_one({'user_id': user_id}, {"$set": {"photo_store_root": new_photo_store_root}})

if __name__ == '__main__':
    m_driver = MongoDriver()
    user_data = m_driver.get_user_params(2)

    if user_data is None:
        user_data = {'user': 2}
        x = m_driver.store_user_data(user_data)

    user_data = m_driver.get_user_params(2)

    print()
