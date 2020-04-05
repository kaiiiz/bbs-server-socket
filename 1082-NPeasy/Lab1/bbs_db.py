import pymongo


class BBS_DB_BASE:
    def __init__(self, username, pwd):
        self.client = pymongo.MongoClient(f'mongodb://{username}:{pwd}@127.0.0.1')
        self.db = self.client['bbs']
        self.init_collection()

    def init_collection(self):
        if 'USERS' not in self.db.list_collection_names():
            self.userCol = self.db['USERS']


class BBS_DB(BBS_DB_BASE):
    def __init__(self, username, pwd):
        super().__init__(username, pwd)
