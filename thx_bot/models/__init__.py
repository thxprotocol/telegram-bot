import os

from bson import ObjectId
from pymongo import MongoClient

mongo_client = MongoClient(
    f"mongodb://{os.getenv('MONGODB_USERNAME')}:"
    f"{os.getenv('MONGODB_PASSWORD')}@{os.getenv('MONGODB_HOSTNAME')}"
)


class Model(dict):

    collection = None
    __getattr__ = dict.get
    __delattr__ = dict.__delitem__
    __setattr__ = dict.__setitem__

    def save(self):
        if not self._id:
            self.collection.insert(self)
        else:
            self.collection.update(
                {"_id": ObjectId(self._id)}, self)

    def reload(self):
        if self._id:
            self.update(self.collection.find_one({"_id": ObjectId(self._id)}))

    def remove(self):
        if self._id:
            self.collection.remove({"_id": ObjectId(self._id)})
            self.clear()
