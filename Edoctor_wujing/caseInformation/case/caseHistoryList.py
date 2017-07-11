#!/usr/bin/python3
# -*- coding: UTF-8 -*-
__author__ = 'wangchenglong'
'''
代码作用：用于显示患者所有就诊记录
'''

from function import gldb
from caseInformation.case import caseQuery

def caseHistoryList(cases,cost,queryNine,patient_id,startTime,endTime,deptName,timeSign):
    result=[]
    # 使用find方式查询
    findCondition = {"$and":[]}
    # 返回结果值
    result.append({'state': 1, 'reason': '查询成功'})

    # 判断其是否缺少该关键字段
    if patient_id == '':
        return [{"status":0,"result":"缺失patient_id关键字段"}]

    else:
        findCondition["$and"].append({"PATIENT_ID":patient_id})



    # 增加时间条件限制，出院时间或者入院时间，对查询为出院时间的还要添加没有出院的时间的记录的查询条件。
    if timeSign=="1":
        if startTime > endTime:
            findCondition["$and"].append({"VISIT_DATE": {"$gte": endTime + " 00:00:00", "$lt": startTime + " 00:00:00"}})
        else:
            findCondition["$and"].append({"VISIT_DATE": {"$gte": startTime + " 00:00:00", "$lt": endTime + " 00:00:00"}})
    else:
        if startTime > endTime:
            findCondition["$and"].append({"$or":[{"DISCHARGE_DATE_TIME": {"$gte": endTime + " 00:00:00", "$lt": startTime + " 00:00:00"}},
                                                   {
                                                    "VISIT_DATE":{"$gte": endTime + " 00:00:00", "$lt": startTime + " 00:00:00"},"CASE_TYPE":{"$ne":"住院"}
                                                   }
                                                 ]
                                          })
        else:
            findCondition["$and"].append({"$or":[{"DISCHARGE_DATE_TIME": {"$gte": startTime + " 00:00:00", "$lt": endTime + " 00:00:00"}},
                                                   {
                                                    "VISIT_DATE":{"$gte": startTime + " 00:00:00", "$lt": endTime + " 00:00:00"},"CASE_TYPE":{"$ne":"住院"}
                                                  }
                                                 ]
                                          })


    # 添加部门名称的查询条件
    if deptName != "":
        findCondition["$and"].append({"DEPT_NAME":{"$regex":deptName}})


     #获取病人的姓名，性别，出生日期（因为cases集合数据残缺，所以到cost集合进行查找）。
    costdata=cost.find({
        "PATIENT_ID": patient_id,
    }).limit(1)
    for data in costdata:
        if "NAME" not in data or data["NAME"] == None:
            data["NAME"] = ""
        if "SEX" not in data or data["SEX"] == None:
            data["SEX"] = ""
        if "DATE_OF_BIRTH" not in data or data["DATE_OF_BIRTH"] == None:
            data["DATE_OF_BIRTH"] = ""
        result.append({"name": data["NAME"],
                       "sex": data["SEX"],
                       "birthDay": data["DATE_OF_BIRTH"][0:10]})

    #查询病历的信息
    m=cases.find(findCondition)
    for data in m:
        if "DISCHARGE_DATE_TIME"in data :
            pass
        else:
            data["DISCHARGE_DATE_TIME"]=data["VISIT_DATE"]
        CASE_ID = {
            "PATIENT_ID":data["PATIENT_ID"],
            "VISIT_DATE":data["VISIT_DATE"],
            "VISIT_NO":data["VISIT_NO"],
            "CASE_TYPE":data["CASE_TYPE"]
        }
        # 用于判断部门信息是否为空
        if "DEPT_NAME" in data and data["DEPT_NAME"] != None:
            pass
        else:
            data["DEPT_NAME"]="无"

        #获取医生名称（case集合医生姓名出现丢失，到cost集合查找）
        doctorName = cost.find({
            "PATIENT_ID": data["PATIENT_ID"],
            "VISIT_DATE": data["VISIT_DATE"],
            "VISIT_NO": data["VISIT_NO"]
        }).limit(1)
        for doctorNameFind in doctorName:
            if "DOCTOR_NAME" in doctorNameFind and doctorNameFind["DOCTOR_NAME"] != None:
                DOCTOR=doctorNameFind["DOCTOR_NAME"]
            else:
                DOCTOR="无"
        if "DOCTOR_NAME" in data and data["DOCTOR_NAME"] != None:
            pass
        else:
            data["DOCTOR_NAME"]=DOCTOR


        # 用于判断其诊断和治疗结果是否为空，并且将诊断和治疗结果从数组中取出。
        a=queryNine.find({"PATIENT_ID":data["PATIENT_ID"],
            "VISIT_DATE":data["VISIT_DATE"]}).limit(1)
        c = []
        licS = []
        for querydata in a:
            if "ITEM" in querydata:
               c, licS = caseQuery.getDetailInfomation(querydata["ITEM"])
        if licS != []:
            if "死亡" in licS:
               diagnose="死亡"
            elif "治愈" in licS:
                diagnose = "治愈"
            elif "好转" in licS:
                diagnose = "好转"
            elif "无效" in licS:
                diagnose = "无效"
            elif "未治" in licS:
                diagnose = "未治"
            else:
                diagnose = "其他"
        else:
            diagnose = "无"

        #将信息添加到result
        if c != []:
            result.append({
                "CASE_ID": str(CASE_ID),
                "caseVisitDate": data["VISIT_DATE"],
                "caseOutDate":data["DISCHARGE_DATE_TIME"],
                "caseType": data["CASE_TYPE"],
                "deptName": data["DEPT_NAME"],
                "doctor": data["DOCTOR_NAME"],
                "diagnose":diagnose,
                "result":c
            })
        else:
            result.append({
                "CASE_ID": str(CASE_ID),
                "caseVisitDate": data["VISIT_DATE"],
                "caseOutDate": data["DISCHARGE_DATE_TIME"],
                "caseType": data["CASE_TYPE"],
                "deptName": data["DEPT_NAME"],
                "doctor": data["DOCTOR_NAME"],
                "diagnose": diagnose,
                "result": "无"
            })
    # print(result)
    return result

# if __name__ == '__main__':
#
#     cases = gldb.seedata_mongo(colname="cases690012" ).getCollection()
#
#     patient_id = "0002340"
#     startTime = "2003-07-12"
#     endTime = "2003-09-20"
#     drugName = ""
#     pages = 3
#     lineNumber = 5
#
#     m = caseHistoryList(cases,patient_id,startTime,endTime,drugName,pages,lineNumber)
#     print(m)











