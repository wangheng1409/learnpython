import pymongo

class MongoUtil(object):
    def __init__(self, collection_name,db_name):
        self.collection_name = collection_name
        self.db_name = db_name
        self._handler = None
        self.connect()

    def connect(self):
        client = pymongo.MongoClient()
        db = client[self.db_name]
        self._handler = db[self.collection_name]

    @property
    def handler(self):
        return self._handler
