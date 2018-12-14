# -*- coding: utf-8 -*-
# @Time    : 2018/8/19下午4:29
# @Author  : Wang Chao

# Written with pymongo-3.4
# Documentation: http://docs.mongodb.org/ecosystem/drivers/python/
# A python script connecting to a MongoDB given a MongoDB Connection URI.

import sys
import pymongo


class MongoApi():
    def __init__(self, uri, collection):
        self.client = pymongo.MongoClient(uri)
        self.db = self.client.get_database()
        self.collection = self.db[collection]

    def find(self, query=None):
        # 查一个collection
        if query:
            array = self.collection.find(query)
        else:
            array = self.collection.find()

        f_list = [x for x in array]

        return f_list

    def create(self, data):
        # 添加文档
        self.collection.insert_many(data)

    def delete(self, query):
        self.collection.delete_many(query)

    def drop(self):
        self.collection.drop()

    def close(self):
        self.client.close()


def main():
    uri = "xxxxxxxxxxxxxxxxxxxx"
    m = MongoApi(uri, 'credentinal')
    m.drop()
    m = MongoApi(uri, 'credential')
    m.find()
    # m.drop()
    m.close()


if __name__ == '__main__':
    main()
