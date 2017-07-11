#!/usr/bin/python3
# -*- coding: UTF-8 -*-
__author__ = 'wangchenglong'
#导入相关的包
from flask import request
from flask_restful import Resource

from function import gldb
# from head.case import patient
from caseInformation.case import patient

from function.glauth import auth
import datetime

class patients(Resource):
    # 用于加密验证
    method_decorators = [auth]

    def get(self, hospital_id):
        try:
            # 病历的case的链接
            queryNine = gldb.seedata_mongo(colname="queryTenTest" + hospital_id).getCollection()
            case = gldb.seedata_mongo(colname="cases" + hospital_id).getCollection()
            patients= gldb.seedata_mongo(colname="patients" + hospital_id).getCollection()
            # 返回获取的数据
            result = []

            # 获取相关的参数
            filter = request.args.get('filter')

            # 将字符串变为字典
            filter = eval(filter)

            # 将这个替换成相应的格式
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
            # filter["timeSign"]=1
            if filter["ageMin"]!='':
               filter["ageMin"]=int(filter["ageMin"])
            if filter["ageMax"]!='':
               filter["ageMax"]=int(filter["ageMax"])
            if filter["laboratoryResultMin"]!='':
               filter["laboratoryResultMin"]=int(filter["laboratoryResultMin"])
            if filter["laboratoryResultMax"] != '':
                filter["laboratoryResultMax"] = int(filter["laboratoryResultMax"])
            # if filter["timeSign"]!='':
            #    filter["timeSign"]=int(filter["timeSign"])
            # print("filter%s" % filter)
            # 获得总人数
            result.extend(patient.patient_id(queryNine,case,patients,filter["patientId"], filter["name"], filter["deptName"],
                                             filter["startTime"], filter["endTime"], int(filter["pages"]),
                                             int(filter["lineNumber"]),filter["ageMin"],filter["ageMax"],
                                             filter["diagnoseResult"],
                                             filter["laboratoryName"],filter["laboratoryResultMin"],filter["laboratoryResultMax"],
                                             filter["examName"],filter["examResult"],
                                             filter["drugName"],filter["operationName"],filter["treatmentResult"],filter["timeSign"]))
            return result,201

        except:
            result = [
                {
                    "state": 0,
                    "reason": "缺失关键字段"
                }
            ]
            return result,404