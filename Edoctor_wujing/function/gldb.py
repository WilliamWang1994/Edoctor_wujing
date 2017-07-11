#!/usr/bin/python3
# -*- coding: UTF-8 -*-


import logging
import pymongo
import threadpool
from function.glconfig import mongodb_cfg
from function.glloger import Logger


# import threadpool
class seedata_mongo():
    def __init__(self,colname,dbname=mongodb_cfg["defaultdb"]):
        # 创建连接
        self.logger = Logger("seedata_mongo", logging.ERROR).getlog()
        try:
            # self.conn = pymongo.MongoClient(mongodb_cfg["host"], mongodb_cfg["port"],maxPoolSize=100)
            # self.conn = pymongo.MongoClient(mongodb_cfg["host"], mongodb_cfg["port"],connect=False)
            self.logger.info("Create Mongo connection")
            self.conn = pymongo.MongoClient(mongodb_cfg["host"], mongodb_cfg["port"])
            self.db = self.conn[dbname]
            #选择集合
            self.collection = self.db[colname]
        except:
            self.logger.error("Connection :"+dbname+'->'+colname)

    def getCollection(self):
        return self.collection


class seedata_thread():
    def __init__(self,threadNumber=16):
        self.logger = Logger("seedata_thread", logging.INFO).getlog()
        self.__threadNumber__=threadNumber
        self.__threadPool__ = threadpool.ThreadPool(self.__threadNumber__)

    def __execute__(self, obj):
        try:
            result=obj[0]()
            obj.pop()
            for _ in result:
                obj.append(_)
            result.close()
        except:
            self.logger.error(obj)

    def thread_query(self,requests):
        # 这句话的意思是获得相关的线程池结果，并且他的位置，一定会是相应的位置。
        try:
            self.results = [[requests[i]] for i in range(0, len(requests))]
            item_requests = threadpool.makeRequests(self.__execute__,self.results)
            [self.__threadPool__.putRequest(req) for req in item_requests]
            self.__threadPool__.wait()
            return self.results
        except Exception as E:
            self.logger.error(str(E))

    def __makeLambda__(self, collection, dbOps, allowDiskUse):
        try:
            return lambda:collection.aggregate(dbOps, allowDiskUse=allowDiskUse)
        except Exception as E:
            self.logger.error(str(E))

    def excute_aggregate(self, collectionName, ops, allowDiskUse=False):
        dbOps=[]
        result=None
        try:
            collection = seedata_mongo(colname=collectionName).getCollection()
            for _ in ops:
                dbOps.append(self.__makeLambda__(collection , _ , allowDiskUse))
            if len(dbOps)>0:
               result=self.thread_query(dbOps)
            return result
        except Exception as E:
            self.logger.error(str(E))



if __name__ == '__main__':
    # pass

    ops=[]
    ops.append([{'$match': {'DEPT_NAME': {'$in': ['肾脏内分泌', '二病区']}}}, {'$match': {'SETTLING_DATE': {'$lte': '2016-05-04 23:59:59', '$gte': '2016-05-02 00:00:00'}}}, {'$group': {'total': {'$sum': 1}, '_id': {'部门': '$DEPT_NAME'}}}])
    th=seedata_thread()
    results=th.excute_aggregate("count_v3", ops)
    print(results)







