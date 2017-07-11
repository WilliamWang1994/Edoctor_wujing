#!/usr/bin/python3
# -*- coding: UTF-8 -*-
__author__ = 'wangchenglong'
from flask import request
from flask_restful import Resource

from function import gldb
from caseInformation.case import caseDetailedInformation
from function.glauth import auth


class caseDetailed(Resource):

    # 用于加密验证
    method_decorators = [auth]
    def get(self, hospital_id):

        try:
            # 病历的case的链接
            patients = gldb.seedata_mongo(colname="patients690012").getCollection()
            laboratory = gldb.seedata_mongo(colname="laboratory690012").getCollection()
            labdetail = gldb.seedata_mongo(colname="labdetail690012").getCollection()
            exam = gldb.seedata_mongo(colname="exam690012").getCollection()
            examdetail = gldb.seedata_mongo(colname="examdetail690012").getCollection()
            drug = gldb.seedata_mongo(colname="drug690012").getCollection()
            diagnose = gldb.seedata_mongo(colname="diagnose690012").getCollection()
            operation = gldb.seedata_mongo(colname="operation690012").getCollection()
            costdetail = gldb.seedata_mongo(colname="costdetail690012").getCollection()
            # 返回获取的数据
            result = []
            # 获取相关的参数
            filter = request.args.get('filter')
            # 将字符串变为字典
            filter = eval(filter)
            print("filterrrrrr%s"%filter)
            caseID=eval(filter["caseID"])
            expenseCategory=filter["expenseCategory"]
            # expenseCategory='全部'

    # 获得总人数
            result.extend(caseDetailedInformation.caseDetailedInformation(
                patients,exam,examdetail,laboratory,labdetail,drug,diagnose,operation,costdetail, caseID,expenseCategory)
            )
            return result,201
        except:
            result = [
                {
                    "state": 0,
                    "reason": "缺失关键字段"
                }
            ]
            return result,500
