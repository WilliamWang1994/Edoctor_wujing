#!/usr/bin/python3
# -*- coding: UTF-8 -*-
__author__ = 'wangchenglong'
'''
# 对应患者查询页面，第一页
'''

# from caseInformation.functionBack import function
from caseInformation.case import caseQuery
from dbLink import gldb

# 用于查询第一页面接口
def patient_id(cases,name,deptname,startTime,endTime,pages,lineNumber):
    # 用于返回查询的数值
    result = []
    # 用于进行数据缓存
    resultList = []

    numberCount = (int(pages) - 1) * int(lineNumber)

    sumTest = 0

    # 管道条件 增加时间段限制、患者名字查询、部门查询
    aggregate = [
        {
            "$match": caseQuery.timeManage(startTime, endTime)
        }
    ]

    # 判断名字、部门相关信息
    aggregate.extend(caseQuery.aggregateManage(name, deptname))

    # 为了区分其两次管道的条件
    aggregateCount = aggregate

    # 获取条件下的总页数
    pageCountNumber = caseQuery.pageNumber(cases, aggregateCount, lineNumber)

    result.append(
        {
            "state": 1,
            "reason": "查询成功"
        }
    )

    # 将统计出来的总页数插入到其数据库中
    result.append(
        {
            "pagesCountNumber":pageCountNumber
        }
    )

    del aggregate[-1]
    del aggregate[-1]

    endTime = endTime + " 00:00:00"
    startTime = startTime + " 00:00:00"
    betweenTime = endTime
    # 用于判断跳跃的个数
    skipNumber = 0
    skipCount = (pages - 1) * lineNumber
    # 缓存处理
    while(1):

        # 用于进行时间段内的统计
        betweenEndTime,betweenStartTime = function.startTimeEndTime(betweenTime,-1)

        # 用于循环，用于判断其时间段内的分析控制
        aggregate[0]["$match"] = {"VISIT_DATE":{"$gte":"%s"%betweenStartTime,"$lt":"%s"%endTime}}

        # 增加管道信息，先将数据进行分组，然后查看总页数。
        aggregate.append(
            {
                "$group": {"_id": "$PATIENT_ID"}
            }
        )

        aggregate.append(
            {
                "$group": {"_id": "$id", "sum": {"$sum": 1}}
            }
        )

        # 管道处理，用于判断其总共有多少页
        m = cases.aggregate(aggregate)
        # 用于统计时间段的总个数

        for data in m:
            sumTest = data["sum"]

        if numberCount > sumTest:
            betweenTime = betweenStartTime
            del aggregate[-1]
            del aggregate[-1]
            continue

        else:
            # 用于确定这个时间段的总个数
            aggregate[0]["$match"] = {"VISIT_DATE": {"$gte": "%s" % betweenEndTime, "$lt": "%s" % endTime}}

            m = cases.aggregate(aggregate)
            # 用于统计时间段的总个数

            for data in m:
                sumTest = data["sum"]

            skipNumber = skipCount - sumTest

            if skipNumber < 0:
                skipNumber = 0

        del aggregate[-1]
        del aggregate[-1]

        aggregate[0]["$match"] = {"VISIT_DATE": {"$gte": "%s" % betweenStartTime, "$lt": "%s" % betweenEndTime}}

        # 进行分组、排序
        aggregate.extend([
            {
                "$group": {
                    "_id": "$PATIENT_ID",
                    "VISIT_DATE": {"$max": "$VISIT_DATE"},
                    "NAME": {"$first": "$NAME"},
                    "SEX": {"$first": "$SEX"},
                    "DATE_OF_BIRTH": {"$first": "$DATE_OF_BIRTH"},
                    "SUM": {"$sum": 1}
                }
            },
            {
                "$sort": {"VISIT_DATE": -1}
            },
        ])

        # 增加限制和返回数据
        # aggregate.extend(caseQuery.skipLimtNumber(pages,lineNumber))
        aggregate.append({"$skip": skipNumber})
        aggregate.append({"$limit": lineNumber})

        # 管道处理
        m = cases.aggregate(aggregate)

        # 用于判断其查询的结果长度
        length = 0

        for i in m:
            resultList.append(i)
            length = length + 1

        if length < lineNumber:
            lineNumber = lineNumber - length

        if len(resultList) >= lineNumber or betweenStartTime < startTime:
            break

        # 用于循环
        betweenTime = betweenEndTime

    for data in resultList:

        # 用于判断其基本的信息设计模式
        text = [
            {"PATIENT_ID":data["_id"]},
            {"name":data["NAME"]},
            {"sex":data["SEX"]},
            {"birthDay":data["DATE_OF_BIRTH"][0:10]},
            {"caseCountNumber":data["SUM"]},
            {"caseVisitDate":data["VISIT_DATE"]}
        ]

        # 获取最新病历的病种、部门科室信息
        diagDescDeptNmae = cases.aggregate([
            {
                "$match": {"PATIENT_ID": data["_id"]}
            },
            {
                "$match": {"VISIT_DATE": data["VISIT_DATE"]}
            },
            {
                "$project": {"DIAG_DESC": 1,"DEPT_NAME":1}
            }
        ])

        # 用于判断其循环只有一次，因为一个人可能同时挂号2次或者以上。
        mark = 0

        # 增加其病历信息
        for casedata in diagDescDeptNmae:

            # 判断其是否发现基本信息
            mark = mark + 1

            if "DEPT_NAME"  in casedata and casedata["DEPT_NAME"] != None:
                text.append(
                    {"deptName": casedata["DEPT_NAME"]}
                )

            else:
                text.append(
                    {"deptName": "无"}
                )

            if "DIAG_DESC" in casedata and casedata["DIAG_DESC"] != None:

                # 将其中的数组变为字符串，因为前端对于数组需要循环。变为字符串可以直接读取。
                diagDesc = ""

                for i in casedata["DIAG_DESC"]:

                    # 解决首先","逗号的问题。
                    if diagDesc == "":
                        diagDesc = i

                    else:
                        diagDesc = diagDesc + "," + i

                text.append(
                    {"caseDetails": diagDesc}
                )

            else:
                text.append(
                    {"caseDetails": "无"}
                )

            if mark > 0:
                break

        # 将其返回值增加
        result.append(text)

        # 循环，用于清空其text的数据，
        text = []

    return result



if __name__ == '__main__':

    result = []

    pretreatment = None

    cases = gldb.seedata_mongo(colname="cases690012").getCollection()

    m = patient_id(cases,"","","2003-07-12","2003-09-20",1600,5)

    print(m)