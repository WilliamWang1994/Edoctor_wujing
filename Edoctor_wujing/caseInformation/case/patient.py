#!/usr/bin/python3
# -*- coding: UTF-8 -*-
__author__ = 'wangchenglong'
'''
# 对应患者查询页面，第一页
'''

# 导入相关的数据包
from function import gldb
# from head.case import caseQuery
from caseInformation.case import caseQuery


# 用于查询第一页面接口
def patient_id(queryNine,case,patients,patientId,name,deptname,startTime,endTime,pages,lineNumber,ageMin,ageMax,diagnoseResult,
               laboratoryName,laboratoryResultMin,laboratoryResultMax,
               examName,examResult,
               drugName,operationName,treatmentResult,timeSign):

    # 用于确定相关返回测试
    result=[]
    findDict ={"$and":[]}


    #时间处理：出院时间和入院时间的选择，并添加到搜索条件中
    if timeSign=="1":
        # if startTime != None and endTime != None:
            if  startTime > endTime:
                findDict["$and"].append({"VISIT_DATE": {"$gte": endTime+ " 00:00:00","$lt": startTime+ " 00:00:00"}})
            else:
                findDict["$and"].append({"VISIT_DATE": {"$gte": startTime + " 00:00:00", "$lt": endTime+ " 00:00:00"}})
    else:
        # if startTime != None and endTime != None:
            if  startTime > endTime:
                findDict["$and"].append({"SETTLING_DATE": {"$gte": endTime+ " 00:00:00","$lt": startTime+ " 00:00:00"}})
            else:
                findDict["$and"].append({"SETTLING_DATE": {"$gte": startTime + " 00:00:00", "$lt": endTime+ " 00:00:00"}})


    # 判断名字、部门相关信息
    findDict["$and"].extend(caseQuery.Manage(patientId,name, deptname,ageMin,ageMax,diagnoseResult,drugName,operationName,treatmentResult))


    # 获取条件下的总页数，添加到
    pageCountNumber,findDict = caseQuery.pageNumber(queryNine, findDict, lineNumber,
                                           laboratoryName,laboratoryResultMin,laboratoryResultMax,
                                           examName,examResult)
    result.append(
        {
            "state": 1,
            "reason": "查询成功"
        }
    )

    # 将从集合内查找并统计出来的总页数添加到result中
    result.append(
        {
            "pagesCountNumber":pageCountNumber
        }
        )


    # 对重复的PATIENT_ID的病历做处理，并获取skip值和limit值
    pagecount=pages
    linecount=lineNumber
    a=caseQuery.pretreatment(queryNine,findDict,pagecount,linecount)


    # 正式开始查找！！！！！！！！！！
    n = queryNine.find(findDict).skip((pages - 1) * lineNumber).limit(lineNumber+a)
    lisC = []


    #遍历查询结果
    for data in n:
        #处理数据库内记录内PATIENT_ID重复
        if "PATIENT_ID" in data:
             if data["PATIENT_ID"] in lisC:
                 continue
             else:
                lisC.append(data["PATIENT_ID"])


        # 初始化text（result内容的中转存放变量）并添加信息
        if "DATE_OF_BIRTH" in data and data["DATE_OF_BIRTH"] != None:
            pass
        else:
            date=patients.find({"PATIENT_ID":data["PATIENT_ID"]}).limit(1)
            for dateFind in date:
                if "DATE_OF_BIRTH" in dateFind and dateFind["DATE_OF_BIRTH"] != None:
                    birth=dateFind["DATE_OF_BIRTH"]
                else:
                    birth="无"
            data["DATE_OF_BIRTH"]=birth
        if "SEX" in data and data["SEX"] != None:
            pass
        else:
            data["SEX"] = "无"
        text = [
                {"PATIENT_ID":data["PATIENT_ID"]},
                {"name":data["NAME"]},
                {"sex":data["SEX"]},
                {"birthDay":data["DATE_OF_BIRTH"][0:10]},
                {"age":data["AGE"]},
                {"caseVisitDate":data["VISIT_DATE"]},
            ]



        #处理电话，本人电话没有的就添加家庭电话
        if "NEXT_OF_KIN_PHONE"in data and data["NEXT_OF_KIN_PHONE"]!=None:
            text.append({"mobilePhone":data["NEXT_OF_KIN_PHONE"]})
        elif "PHONE_NUMBER_HOME"in data and data["PHONE_NUMBER_HOME"]!=None:
            text.append({"mobilePhone": data["PHONE_NUMBER_HOME"]})
        elif "PHONE_NUMBER_BUSINESS"in data and data["PHONE_NUMBER_BUSINESS"]!=None:
            text.append({"mobilePhone": data["PHONE_NUMBER_BUSINESS"]})
        else:
            text.append({"mobilePhone":"无"})



        #获取病人的病历数量line116-169
        if timeSign=="1":
            if startTime>endTime:
                a=startTime
                startTime=endTime
                endTime=a
            casecount = case.find(
                {
                    "$and": [
                        {
                            "PATIENT_ID": data["PATIENT_ID"]
                        },
                        {
                            "VISIT_DATE":{"$gte": startTime+ " 00:00:00","$lt": endTime+ " 00:00:00"}
                        },
                    ]
                }
            ).count()
        else:
            if startTime>endTime:
                a=startTime
                startTime=endTime
                endTime=a
            casecount1 = case.find(
                {
                    "$and": [
                        {
                            "PATIENT_ID": data["PATIENT_ID"]
                        },
                        {
                            "DISCHARGE_DATE_TIME":{"$gte": startTime+ " 00:00:00","$lt": endTime+ " 00:00:00"}
                        },
                        {
                            "CASE_TYPE": "住院"
                        }
                    ]
                }
            ).count()
            casecount2 = case.find(
                {
                    "$and": [
                        {
                            "PATIENT_ID": data["PATIENT_ID"]
                        },
                        {
                            "VISIT_DATE": {"$gte": startTime + " 00:00:00", "$lt": endTime + " 00:00:00"}
                        },
                        {
                            "CASE_TYPE": {"$ne":"住院"}
                        }
                    ]
                }
            ).count()
            casecount=casecount1+casecount2


        #添加部门名称
        if "DEPT_NAME" in data and data["DEPT_NAME"] != None:
                text.append(
                    {"deptName": data["DEPT_NAME"]}
                )
        else:
                text.append(
                    {"deptName": "无"}
                )



        # 获取诊断结果
        c=[]
        licS = []
        if "ITEM"in data:
           c,licS=caseQuery.getDetailInfomation(data["ITEM"])
        if c!=[]:
                        # result.replace(" ",",")
            text.append(
                    {"caseDetails": c}
            )
        else:
            text.append(
                    {"caseDetails": "无"}
             )


        #添加病历数量和费别
        text.append({
            "caseCountNumber":casecount
        })
        if "CHARGE_TYPE" in data and data["CHARGE_TYPE"]!=None:
            text.append({"chargeType": data["CHARGE_TYPE"]})
        else:
            text.append({"chargeType": "无"})


        # 治疗结果的优先级获取，因为一个病人有多个治疗结果，处理各类结果的优先级
        if licS!=[]:
            if "死亡" in licS:
                text.append({"treatmentResult": "死亡"})
            elif "治愈" in licS:
                text.append({"treatmentResult": "治愈"})
            elif "好转" in licS:
                text.append({"treatmentResult": "好转"})
            elif "无效" in licS:
                text.append({"treatmentResult": "无效"})
            elif "未治" in licS:
                text.append({"treatmentResult": "未治"})
            else:
                text.append({"treatmentResult": "其他"})
        else:
            text.append({"treatmentResult": "无"})


         #添加出院时间
        text.append({"patientId":data["PATIENT_ID"] })
        if "SETTLING_DATE" in data and data["SETTLING_DATE"]!=None:
            text.append({"caseOutDate": data["SETTLING_DATE"]})
        else:
            text.append({"caseOutDate": "无"})
        # text.append({"caseOutDate": data["SETTLING_DATE"]})
        #将text加入到result
        result.append(text)
        # 循环，用于清空其text的数据
        text = []
    return result



if __name__ == '__main__':

    result = []

    pretreatment = None

    queryNine = gldb.seedata_mongo(colname="queryTen"+"690012").getCollection()

    # m = patient_id(queryNine,"","","2003-07-12","2009-09-20",1,5)

    # print(m)