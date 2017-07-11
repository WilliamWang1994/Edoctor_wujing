#!/usr/bin/python3
# -*- coding: UTF-8 -*-
__author__ = 'wangchenglong'
from flask import request
from flask_restful import Resource

from function import gldb
from caseInformation.case import caseHistoryList
from function.glauth import auth
import datetime


class caseHistoryListFind(Resource):

    # 用于加密验证
    method_decorators = [auth]

    def get(self, hospital_id):

        # try:
            # 病历的case的链接
            case = gldb.seedata_mongo(colname="cases" + hospital_id).getCollection()
            cost=gldb.seedata_mongo(colname="cost" + hospital_id).getCollection()
            queryNine=gldb.seedata_mongo(colname="queryTen" + hospital_id).getCollection()
            # 返回获取的数据
            result = []

            # 获取相关的参数
            filter = request.args.get('filter')

            # 将字符串变为字典
            filter = eval(filter)
            print("filter2:%s"%filter)

            filter["startTime"] = filter["startTime"].replace("年", "-")
            filter["startTime"] = filter["startTime"].replace("月", "-")
            filter["startTime"] = filter["startTime"].replace("日", "")

            filter["endTime"] = filter["endTime"].replace("年", "-")
            filter["endTime"] = filter["endTime"].replace("月", "-")
            filter["endTime"] = filter["endTime"].replace("日", "")

            endTime = datetime.datetime.strptime(filter["endTime"], "%Y-%m-%d")
            endTime = endTime + datetime.timedelta(days=1)
            filter["endTime"] = datetime.datetime.strftime(endTime, "%Y-%m-%d")

            endTime = datetime.datetime.strptime(filter["startTime"], "%Y-%m-%d")
            filter["startTime"] = datetime.datetime.strftime(endTime, "%Y-%m-%d")

            # 获得总人数
            result.extend(caseHistoryList.caseHistoryList(case, cost,queryNine,filter["patientId"], filter["startTime"],
                                                          filter["endTime"], filter["drugName"],filter["timeSign"]
                                                         ))
            print(result)
            return result,201

        # except:
        #
        #     result = [
        #         {
        #             "state": 0,
        #             "reason": "缺失关键字段"
        #         }
        #     ]
        #     return result,500
