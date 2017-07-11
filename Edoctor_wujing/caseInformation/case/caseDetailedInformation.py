#!/usr/bin/python3
# -*- coding: UTF-8 -*-
__author__ = 'wangchenglong'
from function import gldb
from caseInformation.case import caseQuery

'''
入口参数：cases,exam,laboratory,drug,caseID。
出口参数：result。
函数作用：用于查看病例的详细信息。
'''
def caseDetailedInformation(patients,exam,examdetail,laboratory,labdetail,drug,diagnose,
                            operation,costdetail,caseID,expenseCategory):
    # 用于返回病历的详细信息
    result =[
    {
    },
    {
        "type":"诊断",
        "result":[]
    },
    {
        "type":"手术",
        "result":[]
    },
    {
        "type":"检查",
        "result":[]
    },
    {
        "type":"检验",
        "result":[]
    },
    {
        "type":"药品",
        "result":[]
    },
    {
        "type":"费用信息",
        "result":[]

    },
    {
        "type":"治疗",
        "result":[]
    },
    {
        "type":"麻醉",
        "result":[]
    },
    {
        "type":"护理",
        "result":[]
    },
    {
        "type":"膳食",
        "result":[]
    },
    {
        "type":"血费",
        "result":[]
    },
    {
        "type":"床位",
        "result":[]
    },
    {
        "type":"材料",
        "result":[]
    },
    {
        "type":"其他",
        "result":[]
    }
]
    caseID = eval(caseID)
    # print("caseID:%s" % caseID)
    # 用于获取病历基本信息
    result[0] = caseQuery.caseInforamtion(patients, caseID)

    # result[1]= {"type":"检查"}
    result[3]["result"] = caseQuery.examInformation(exam,caseID,examdetail,costdetail)

    # result[2]={"type":"诊断"}
    result[1]["result"] = caseQuery.diagnoseformation(diagnose, caseID)

    # result[3]={"type":"药品"}
    result[5]["result"] = caseQuery.drugInformation(drug,costdetail,caseID)

    # result[4]={"type":"检验"}
    result[4]["result"] = caseQuery.laboratoryInformation(laboratory,labdetail, caseID,costdetail)

    # result[5]={"type":"手术"}
    result[2]["result"]=caseQuery.operationInfomation(costdetail,caseID)

    # result[6]={"type":"费用信息"}
    result[6]["result"] = caseQuery.costInfomation(costdetail, caseID,expenseCategory)

    # result[7]={"type":"治疗信息"}
    result[7]["result"]=caseQuery.treatmentInfomation(costdetail,caseID)

    # result[8]={"type":"麻醉信息"}
    result[8]["result"] = caseQuery.narcosisInfomation(costdetail, caseID)

    # result[9]={"type":"护理信息"}
    result[9]["result"] = caseQuery.nurseInfomation(costdetail, caseID)

    # result[11]={"type":"血费信息"}
    result[11]["result"] = caseQuery.bloodInfomation(costdetail, caseID)

    # result[12]={"type":"床位信息"}
    result[12]["result"] = caseQuery.bedInfomation(costdetail, caseID)

    # result[10]={"type":"膳食信息"}
    result[10]["result"]=caseQuery.foodInformation(costdetail,caseID)

    # result[13]={"type":"材料信息"}
    result[13]["result"]= caseQuery.materialInfomation(costdetail, caseID)

    # result[14]={"type":"其他信息"}
    result[14]["result"] = caseQuery.otherInfomation(costdetail, caseID)

    return result

# if __name__ == "__main__":
#     cases = gldb.seedata_mongo(colname="cases690012").getCollection()
#     laboratory = gldb.seedata_mongo(colname="laboratory690012").getCollection()
#     labdetail = gldb.seedata_mongo(colname="labdetail690012").getCollection()
#     exam = gldb.seedata_mongo(colname="exam690012").getCollection()
#     examdetail = gldb.seedata_mongo(colname="examdetail690012").getCollection()
#     drug = gldb.seedata_mongo(colname="drug690012").getCollection()
#     diagnose = gldb.seedata_mongo(colname="diagnose690012").getCollection()
#     operation = gldb.seedata_mongo(colname="operation690012").getCollection()
#     costdetail = gldb.seedata_mongo(colname="costdetail690012").getCollection()
#     caseID = {
# 'CASE_TYPE': '门诊',
# 'PATIENT_ID': '9712673',
# 'VISIT_DATE': '2017-04-28 00:00:00', 'VISIT_NO': 521}
#     # caseID = "90125040-20161221024101-1"
#     m = caseDetailedInformation(cases,exam,examdetail,laboratory,labdetail,drug,diagnose,operation,costdetail,caseID)
    # for i in m:
    #     print(i)
    # print(m)


