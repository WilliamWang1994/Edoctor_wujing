#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import copy
import re
__author__ = 'wangchenglong'
'''
入口参数：startTime,endTime
出口参数：result
函数作用：判断startTime、endTime的大小，并且在最后增加：00:00:00，返回用于管道相关设置
'''
def timeManage(startTime,endTime):
    # 用于返回处理后的mongodb $match 条件
    result  = None

    # 判断其结束时间时间的大小是否为最大值,
    if startTime != None and endTime != None:

        if endTime == "至今":

            result = {"VISIT_DATE":{"$gte":startTime+"00:00:00"}}

        else:
            if  startTime > endTime:
                result =timeQuantum(endTime,startTime,"caseQuery")

            else:
                result =timeQuantum(startTime,endTime,"caseQuery")

    return result
'''
入口参数：startTime,endTime
出口参数：match
函数作用：在管道的match条件中加入时间条件：{"$gte":startTime,"$lt":endTime}
'''
def timeQuantum(startTime,endTime,queryType):
    # 这个适用于传输时间的判断格式
    match = {}

    if startTime != None and endTime != None:
        startTime = startTime + " 00:00:00"
        endTime = endTime + " 00:00:00"

        if queryType == "income":
            match["SETTLING_DATE"] = {"$gte":"%s"%startTime,"$lt":"%s"%endTime}
        elif queryType == "EXPORT_DATE":
            match["EXPORT_DATE"] = {"$gte": "%s" % startTime, "$lt": "%s" % endTime}
        elif queryType == "OP_DATE":
            match["OP_DATE"] = {"$gte": "%s" % startTime, "$lt": "%s" % endTime}
        elif queryType == "执行科室":
            match["ITEM.DETAIL.TIME"] = {"$gte": "%s" % startTime, "$lt": "%s" % endTime}
        else:
            match["VISIT_DATE"] = {"$gte": "%s" % startTime, "$lt": "%s" % endTime}

    return match

'''
入口参数：pages,lineNumber
出口参数：result
函数作用：用于计算skip、limit 的数据。分页输入条件计算。
'''
def skipLimtNumber(pages,lineNumber):
    # 管道的条件限制
    result = []

    # 用于计算skip 输入的数据
    skipNumber = (pages - 1) * lineNumber

    # 用于计算limit 输入的数据
    limitNumber = lineNumber

    # aggregate 条件判断
    result.append({"$skip":skipNumber})
    result.append({"$limit":limitNumber})

    return result

'''
入口参数：name,deptname
出口参数：result
函数作用：用于增加管道的条件
'''
def Manage(patientId,name,deptname,age1,age2,diagnoseResult,drugName,operationName,treatmentResult):
    # 返回管道条件处理
    result = []
    # 判断名字是否为空
    if patientId != '':
            result.append(
                {
                    "PATIENT_ID": patientId
                }
            )
    if name != '':
        result.append(
            {
                "NAME":name
            }
        )
    if deptname != '':
            result.append(
                {
                    "DEPT_NAME": deptname
                }
            )
            # 诊断结果
    if diagnoseResult != '':
            result.append(
                {
                    "ITEM.DETAIL.DIAG_RESULT": {"$regex":diagnoseResult}
                }
            )
            # 药品名称
    if drugName != '':
            result.append(
                {
                    "ITEM.DETAIL.DRUG_NAME": {"$regex":drugName}
                }
            )
        # 手术名称
    if operationName != '':
            result.append(
                {
                    "ITEM.DETAIL.OPERATION_NAME": {"$regex":operationName}
                }
            )
    if treatmentResult != '':
            result.append(
                {
                        "ITEM.DETAIL.RESULT": treatmentResult
                }
            )

        # 年龄处理
        # if (age1 != None)and(age2!=None):
    match = ageManage(age1, age2)
    result.extend(match)
    return result
'''
王成龙修改代码
入口参数：ageMin，ageMax
出口参数：match
函数作用：用于增加管道的年龄条件
'''
def ageManage(ageMin,ageMax):
    # mongodb 管道 "$or":[{},{}]。所以将其信息改变为基本信息
    # 管道的条件
    match =[]
    # 用于返回需要查询的年龄，确定其位置
    if ageMin !='':
        if ageMax!='':
            match.append(
                {
                    "AGE": {"$gte": ageMin, "$lt": ageMax}
                }
                          )
        else:
            match.append(
                {
                            "AGE": {"$gte": ageMin}
                 }
                           )
    else:
        if ageMax != '':
            match.append(
                {
                    "AGE": {"$lt": ageMax}
                }
            )
    return match
'''
入口参数：cases,aggregate,lineNumber
出口参数：result,residue
函数作用：获取查询条件下的总页数和最后一页的行数
'''
def pageNumber(test, aggregate, lineNumber,
               laboratoryName,laboratoryResultMin,laboratoryResultMax,
               examName,examResult):
    # 检验的处
    result = None
    if laboratoryName != "":
        if (laboratoryResultMin!='')and(laboratoryResultMax!=''):
            aggregate["$and"].append({"ITEM.DETAIL": {
                "$elemMatch": {
                    "LAB_NAME": {"$regex":laboratoryName},
                    "LAB_RESULT": {"$gte":laboratoryResultMin, "$lt": laboratoryResultMax}
                }
            }
            })
        elif (laboratoryResultMin=='')and(laboratoryResultMax!=''):
            aggregate["$and"].append({"ITEM.DETAIL": {
                "$elemMatch": {
                    "LAB_NAME": {"$regex": laboratoryName},
                    "LAB_RESULT": {"$lt": laboratoryResultMax}
                }
            }
            })
        elif (laboratoryResultMin != '') and (laboratoryResultMax == ''):
            aggregate["$and"].append({"ITEM.DETAIL": {
                "$elemMatch": {
                    "LAB_NAME": {"$regex": laboratoryName},
                    "LAB_RESULT": {"$gte": laboratoryResultMin}
                }
            }
            })
        elif (laboratoryResultMin == '') and (laboratoryResultMax == ''):
            aggregate["$and"].append({"ITEM.DETAIL.LAB_NAME": {"$regex":laboratoryName}})
    # 检查的处理
    if (examName != "") and (examResult != ""):
        aggregate["$and"].append({"ITEM.DETAIL": {
            "EXAM_NAME": {"$regex":examName},
            "EXAM_RESULT": {"$regex":examResult}
        }
        })
    elif (examName == "") and (examResult != ""):
        aggregate["$and"].append({"ITEM.DETAIL.EXAM_RESULT": {"$regex":examResult}})
    elif (examName != "") and (examResult == ""):
              aggregate["$and"].append({"ITEM.DETAIL.EXAM_NAME":{"$regex":examName}})
    a = 0  # 用于计数
    m = test.find(aggregate)
    for data in m:
        # 取余，用于判断是否能够整除
        a += 1
    residue = a % lineNumber
    if residue == 0:
            result = a // lineNumber

    else:
            result = a // lineNumber + 1
    return result, aggregate
def pretreatment(queryNine,findDict,pages,lineNumber):
    lisc = []
    a=0
    skip=(pages - 1) * lineNumber
    datademo = {}
    while len(lisc)<lineNumber:
        if skip>=queryNine.find(findDict).count():
            break
        m = queryNine.find(findDict).skip(skip).limit(1)
        for datademo in m:
            pass
        # if datademo=='':
        #     break
        if "PATIENT_ID"in datademo:
             if datademo["PATIENT_ID"] in lisc:
                 a+=1
             else:
                lisc.append(datademo["PATIENT_ID"])
        else:
             a+=1
        skip+=1
        datademo = {}
    return a
'''
入口参数：cases,aggregate,lineNumber
出口参数：result
函数作用：获取查询条件下的病历总个数
'''
'''
获取ＩＴＥＭ．ＤＥＴＡＩＬ内的信息
'''
def getDetailInfomation(lic):
    abc = []
    liccS = []
    d=''
    for a in lic:
        for b in a["DETAIL"]:
            if "DIAG_RESULT" in b and b["DIAG_RESULT"]!="无":
                d = b["DIAG_RESULT"].replace('&','')
                if d in abc:
                    pass
                else:
                    abc.append(d)

                # d=c.replace(' ',',')
                # print("caseDetails:%s" % c)
            if "RESULT" in b:
                # d=b["RESULT"].replace('&','')
                liccS.append(b["RESULT"])
                # print("Result:%s"%b["RESULT"])
    return abc,liccS
def casePageNumber(cases,aggregate,lineNumber):

    # 返回查询条件下的总页数
    result = None

    # 增加管道信息，先将数据进行分组，然后查看总页数。
    aggregate.append(
        {
            "$group": {"_id": "","sum":{"$sum":1}}
        }
    )

    # 管道处理，用于判断其总共有多少页
    m = cases.aggregate(aggregate)

    for data in m:
        # 取余，用于判断是否能够整除
        residue = data["sum"] % lineNumber

        if residue == 0:
            result = data["sum"] // lineNumber

        else:
            result = data["sum"] // lineNumber + 1

    return result


'''
入口参数：cases,caseID
出口参数：result
函数作用：获取病历中患者基本信息：姓名、性别、出生日期
'''
def caseInforamtion(patients,caseID):
    # print("casein:%s"%caseID)
    # 字典类型，直接插入返回结果值。
    result={}
    # print (type(caseID))
    # print(type(abc))
    if "VISIT_DATE" in caseID :
        result["visitDate"]=caseID["VISIT_DATE"]
    # result={"visitDate":caseID["VISIT_DATE"]}
    casesFind = patients.find(
        {"PATIENT_ID":caseID["PATIENT_ID"]}
    )
    for data in casesFind:

        if data != {} and data != None:

            if "NAME" in data and data["NAME"]!=None:

                result["name"] = data["NAME"]

            if "SEX" in data and data["SEX"]!=None:
                result["sex"] = data["SEX"]

            if "DATE_OF_BIRTH" in data :
                result["birthDay"] = data["DATE_OF_BIRTH"][0:10]
    # result"name": "",  # 患者姓名
    # "sex": "",  # 患者性别
    # "birthDay": "",  # 患者出生日期
    # "visitDate": "",  # 该病例就诊时间
    return result


'''
入口参数：exam,caseID
出口参数：result
函数作用：获取病历中患者检查信息
'''
def examInformation(exam,caseID,examdetail,costdetail):

    result = []
    examFind = exam.find(caseID)
    for data in examFind:
        # print("start")
        # print("data:%s"%data)
        if data != {} and data != None:
            if "EXAM_CLASS" in data and data["EXAM_CLASS"] != None:
                pass
            else:
                data["EXAM_CLASS"] = "无"
            if "EXAM_SUB_CLASS" in data and data["EXAM_SUB_CLASS"] != None:
                pass
            else:
                data["EXAM_SUB_CLASS"] = "无"
            if "RESULT_DATE_TIME" in data and data["RESULT_DATE_TIME"] != None:
                pass
            else:
                data["RESULT_DATE_TIME"] = "无"
            examdetailFind = examdetail.find(
                {
                    "EXAM_NO": data["EXAM_NO"]
                }
            )
            # print("examdetailFind:%s"%(examdetailFind!=''))
            list=[]
            for examdetailFindData in examdetailFind:
                # print("examdetailFindData:"%examdetailFindData)
                if "EXAM_CLASS" in examdetailFindData and examdetailFindData["EXAM_CLASS"] != None:
                    pass
                else:
                    examdetailFindData["EXAM_CLASS"] = data["EXAM_CLASS"]
                if "EXAM_SUB_CLASS" in examdetailFindData and examdetailFindData["EXAM_SUB_CLASS"] != None:
                    pass
                else:
                    examdetailFindData["EXAM_SUB_CLASS"] =  data["EXAM_SUB_CLASS"]
                if "RESULT" in examdetailFindData and examdetailFindData["RESULT"] != None:
                    if examdetailFindData["RESULT"]=="见单":
                        examdetailFindData["RESULT"] = str(examdetailFindData["RESULT"] + data["EXAM_NO"])
                    else:
                        pass
                else:
                    examdetailFindData["RESULT"]="无"
                if "RESULT_DATE_TIME" in examdetailFindData and examdetailFindData["RESULT_DATE_TIME"] != None:
                    pass
                else:
                    examdetailFindData["RESULT_DATE_TIME"] = data["RESULT_DATE_TIME"]

                list.append(
                    {   "examDate":examdetailFindData["RESULT_DATE_TIME"],
                        "examType": examdetailFindData["EXAM_CLASS"],
                        "examClass": examdetailFindData["EXAM_SUB_CLASS"],
                        "result": examdetailFindData["RESULT"]
                    }
                )
            if list == []:
                result.append(
                    {"examDate": data["RESULT_DATE_TIME"],
                     "examType": data["EXAM_CLASS"],
                     "examClass": data["EXAM_SUB_CLASS"],
                     "result": ("检查编号:" + data["EXAM_NO"])
                     }
                )
            else:
                result.extend(list)
            # print("1%s" % result)
    if result == []:
        caseexam = copy.copy(caseID)
        caseexam["ITEM_CLASS"] = "检查"
        costdata = costdetail.find(caseexam)
        for costdetail in costdata:
            if costdetail != {} and costdetail != None:
                if "ITEM_NAME" in costdetail and costdetail["ITEM_NAME"] != None:
                    pass
                else:
                    costdetail["ITEM_NAME"] = "无"
                if "SETTLING_DATE" in costdetail and costdetail["SETTLING_DATE"] != None:
                     pass
                else:
                    costdetail["SETTLING_DATE"] = "无"
                result.append(
                    {"examDate": costdetail["SETTLING_DATE"],
                    "examType": costdetail["ITEM_NAME"],
                    "examClass": "无",
                    "result": "见单"
                     }
                    )
                # print("2%s" % result)
        if result == []:
            result = "无"



    # print("examresult%s" % result)
    return result
'''
入口参数：laboratory, caseID
出口参数：result
函数作用：获取病历中患者诊断信息信息
'''
def diagnoseformation(diagnose, caseID):
    # 返回数组，因为一个人可以同时进行多次检查
    result = []
    # 管道查询
    diagnoseFind = diagnose.find(caseID)
    # 检查的数据插入到最后的控制中。
    for data in diagnoseFind:
        if data != {} and data != None:
            # print("diagnosedata%s"%data)
            if "DIAGNOSIS_DATE_TIME" in data and data["DIAGNOSIS_DATE_TIME"]!=None:
                pass
            else:
                data["DIAGNOSIS_DATE_TIME"] = "无"
            if " DIAGNOSIS_TYPE" in data and data["DIAGNOSIS_TYPE"]!=None:
                pass
            else:
                data[" DIAGNOSIS_TYPE"] = "无"
            if "DIAG_DESC" in data and data["DIAG_DESC"]!=None:
                pass
            else:
                data["DIAG_DESC"] = "无"
            # print("date%s"%data["DIAGNOSIS_DATE_TIME"])
            result.append(
                            {
                                "date": data["DIAGNOSIS_DATE_TIME"],  # 诊断时间
                                "type": data["DIAGNOSIS_TYPE"], # 诊断类型
                                "result": data["DIAG_DESC"]
                            }
                        )
    if result == []:
        result = "无"

    return result

'''
入口参数：drug, caseID
出口参数：result
函数作用：获取病历中患者用药信息
'''
def drugInformation(drug,costdetail,caseID):
    # 返回数组，因为一个人可以同时进行多次检查
    result = []
    # 管道查询
    drugFind = drug.find(caseID)
    # 检查的数据插入到最后的控制中。
    for data in drugFind:
        if data != {} and data != None:
            if  "ITEM_NAME" in data and (data["ITEM_CLASS"]=="西药" or data["ITEM_CLASS"]=="中药"):
                #集中处理返回值
                if "ITEM_NAME" in data and data["ITEM_NAME"]!=None:
                    pass
                else:
                    data["ITEM_NAME"] = "无"
                if "ITEM_CLASS" in data and data["ITEM_CLASS"]!=None:
                    pass
                else:
                    data[" ITEM_CLASS"] = "无"
                if "UNITS" in data and data["UNITS"]!=None:
                    pass
                else:
                    data["UNITS"] = "无"
                if "ADMINISTRATION" in data and data["ADMINISTRATION"]!=None:
                    pass
                else:
                    data["ADMINISTRATION"] = "无"
                if "FREQUENCY" in data and data["FREQUENCY"]!=None:
                    pass
                else:
                    data["FREQUENCY"] = "医嘱"
                if "DOSAGE" in data and data["DOSAGE"]!=None:
                    pass
                else:
                    data["DOSAGE"] = 0
                result.append({
                    "name": data["ITEM_NAME"],  # 药品名称
                    "drugClass": data["ITEM_CLASS"],  # 药品类别
                    "drugUseWay": data["ADMINISTRATION"],  # 药品使用方式
                    "drugUseFrequency":  data["FREQUENCY"],  # 药品使用频率
                    "unit":  data["UNITS"],  # 药品单位
                    "number": data["DOSAGE"],  # 数量
                })
    if result == []:
        casedrug=copy.copy(caseID)
        casedrug["$or"]=[]
        casedrug["$or"].append({"ITEM_CLASS":"西药"})
        casedrug["$or"].append({"ITEM_CLASS":"中药"})
        # print("casedrug%s"%casedrug)
        costdata=costdetail.find(casedrug)
        for costdetail in costdata:
             if costdetail != {} and costdetail != None:
                 if "ITEM_NAME" in costdetail and costdetail["ITEM_NAME"] != None:
                     pass
                 else:
                     costdetail["ITEM_NAME"] = "无"
                 if "ADMINISTRATION" in costdetail and costdetail["ADMINISTRATION"] != None:
                     pass
                 else:
                     costdetail["ADMINISTRATION"] = "无"
                 if " FREQUENCY" in costdetail and costdetail["FREQUENCY"] != None:
                     pass
                 else:
                     costdetail["FREQUENCY"] = "无"
                 if " UNITS" in costdetail and costdetail["UNITS"] != None:
                     pass
                 else:
                     costdetail["UNITS"] = "无"
                 if " AMOUNT" in costdetail and costdetail["AMOUNT"] != None:
                     pass
                 else:
                     costdetail["AMOUNT"] = "无"
                 result.append(
                     {
                    "name": costdetail["ITEM_NAME"],  # 药品名称
                    "drugClass": costdetail["ITEM_CLASS"],  # 药品类别
                    "drugUseWay": costdetail["ADMINISTRATION"],  # 药品使用方式
                    "drugUseFrequency":  costdetail["FREQUENCY"],  # 药品使用频率
                    "unit":  costdetail["UNITS"],  # 药品单位
                    "number": costdetail["AMOUNT"],  # 数量
                     }
                 )
        if result == []:
            result = "无"
    # print("drugresult:%s"%result)
    return result

def laboratoryInformation(laboratory,labdetail, caseID,costdetail):
    # 返回数组，因为一个人可以同时进行多次检查
    result = []

    # 管道查询
    laboratoryFind = laboratory.find(caseID)
    # 检查的数据插入到最后的控制中。
    for data in laboratoryFind:
        if data != {} and data != None:
            lics = []
            if "RESULTS_RPT_DATE_TIME" in data and data["RESULTS_RPT_DATE_TIME"] != None:
                pass
            else:
                data["RESULTS_RPT_DATE_TIME"] = "无"
            if "TEST_NO" in data and data["TEST_NO"]!=None:
               labdetailFind = labdetail.find(
                  {
                      "TEST_NO":data["TEST_NO"]
                  }
             )
            else:
                result = "无"
                break
            for labdetailFindData in labdetailFind:
                if "RESULT_DATE_TIME" in labdetailFindData and labdetailFindData["RESULT_DATE_TIME"]!=None:
                    pass
                else:
                    labdetailFindData["RESULT_DATE_TIME"]="无"
                if "ITEM_CLASS" in labdetailFindData and labdetailFindData["ITEM_CLASS"]!=None:
                    labdetailFindData["ITEM_CLASS"] =(data["TEST_NO"])+(labdetailFindData["ITEM_CLASS"])
                else:
                    labdetailFindData["ITEM_CLASS"]=data["TEST_NO"]
            #理检查名称，结果，结果标志
                if "ITEM_NAME"  in labdetailFindData and labdetailFindData["ITEM_NAME"]!=None:
                    pass
                else:
                    labdetailFindData["ITEM_NAME"]="无"
                if "RESULT" in labdetailFindData and labdetailFindData["RESULT"]!=None:
                    pass
                else:
                    labdetailFindData["RESULT"] = "无"
                if "ABNORMAL_INDICATOR" in labdetailFindData and labdetailFindData["ABNORMAL_INDICATOR"]!=None:
                    pass
                else:
                    labdetailFindData["ABNORMAL_INDICATOR"] = "无"
                if "UNITS" in labdetailFindData and labdetailFindData["UNITS"]!=None:
                    pass
                else:
                    labdetailFindData["UNITS"] = " "
                #带单位
                sum=labdetailFindData["RESULT"]+labdetailFindData["UNITS"]
                lics.append({
                                "labResultName": labdetailFindData["ITEM_NAME"],
                                "labResultNumber": sum,
                                "labResultNumberCharge": labdetailFindData["ABNORMAL_INDICATOR"]
                })
            if lics==[]:
                result.append(
                    {"date": data["RESULTS_RPT_DATE_TIME"],
                     "type": data["TEST_NO"],
                     "result": {
                                "labResultName": "无",
                                "labResultNumber": "无",
                                "labResultNumberCharge": "无"
                }
                     }
                )
            else:
                result.append(
                        {   "date":labdetailFindData["RESULT_DATE_TIME"],
                            "type":labdetailFindData["ITEM_CLASS"],
                            "result":lics
                             }
                        )

    if result == []:
        liclab=[]
        caselab = copy.copy(caseID)
        caselab["$or"] = []
        caselab["$or"].append({"ITEM_CLASS": "检验"})
        caselab["$or"].append({"ITEM_CLASS": "化验"})
        labdata = costdetail.find(caselab)
        for labdetail in labdata:
            if labdetail != {} and labdetail != None:
                if "ITEM_NAME" in labdetail and labdetail["ITEM_NAME"] != None:
                    pass
                else:
                    labdetail["ITEM_NAME"] = "无"
                # if "VISIT_DATE" in labdetail and labdetail["VISIT_DATE"] != None:
                #     pass
                # else:
                #     labdetail["VISIT_DATE"] = "无"
                liclab.append(
                    {
                         "labResultName": labdetail["ITEM_NAME"],
                         "labResultNumber":"无",
                         "labResultNumberCharge": "无"
                     }
                    )
        if  liclab!=[]:
            result.append(
                  {"date":"无",
                   "type": "无",
                   "result": liclab
                  }
                  )
        # print(result)
        else:
            result = "无"
    # print(result)
    return result

def operationInfomation(costdetail,caseID):
    result = []
    case=copy.copy(caseID)
    case["ITEM_CLASS"]="手术"
    operationFind=costdetail.find(case)
    for data in operationFind:
        if data != {} and data != None:
            if "SETTLING_DATE" in data and data["SETTLING_DATE"]!=None:
                pass
            else:
                data["SETTLING_DATE"] = "无"
            if " ITEM_NAME" in data and data["ITEM_NAME"]!=None:
                pass
            else:
                data[" ITEM_NAME"] = "无"
            if " DOCTOR_NAME" in data and data["DOCTOR_NAME"] != None:
                pass
            else:
                data[" DOCTOR_NAME"] = "无"
            result.append(
                {
                    "date": data["SETTLING_DATE"],  # 手术时间
                    "name": data["ITEM_NAME"],  # 手术类型
                    "doctor":data["DOCTOR_NAME"]
                }
            )
    if result == []:
        result = "无"
    return result

def costInfomation(costdetail,caseID,expenseCategory):
    result=[]
    case=copy.copy(caseID)
    if expenseCategory!="全部":
        case["ITEM_CLASS"]=expenseCategory
    costFind=costdetail.find(case)
    #作为统计的变量赋值
    costsTotal=chargesTotal=drugCost=examCost=labCost=cureCost=operationCost=narcosisCost=nurseCost= \
    dietCost=otherCost=booldCost=bedCost=materialCost=0.00
    for data in costFind:
        # print("data%s"%data)
        if "ITEM_NAME" in data and data["ITEM_NAME"]!=None:
            data["ITEM_NAME"]=data["ITEM_NAME"].replace(" ","")
        else:
            data["ITEM_NAME"] = "无"

        if "UNITS" in data and data["UNITS"]!=None:
            pass
        else:
            data["UNITS"] = "无"

        if "AMOUNT" in data and data["AMOUNT"]!=None:
            pass
        else:
            data["AMOUNT"] = 0

        if "COSTS" in data and data["COSTS"]!=None:
           pass
        else:
            data["COSTS"] =0

        if "CHARGES" in data and data["CHARGES"]!=None:
            pass
        else:
            data["CHARGES"] = "无"

        if "UNIT_PRICE" in data and data["UNIT_PRICE"]!=None:
            pass
        elif data["AMOUNT"]!=0:
            abc=data["COSTS"] / data["AMOUNT"]
            data["UNIT_PRICE"] =round(abc,2)
        else:
            data["UNIT_PRICE"]="无"

        #检查
        if data["ITEM_CLASS"] == "中药" or data["ITEM_CLASS"] =="西药":
            # print(type(drugCost))
            # print(type( data["COSTS"]))
            drugCost=drugCost+data["COSTS"]
        if data["ITEM_CLASS"] == "检查":
            examCost=examCost+data["COSTS"]
        if data["ITEM_CLASS"] == "检验":
            labCost=labCost+data["COSTS"]
        if data["ITEM_CLASS"] == "治疗":
            cureCost=cureCost+ data["COSTS"]
        if data["ITEM_CLASS"] == "手术":
            operationCost=operationCost+data["COSTS"]
        if data["ITEM_CLASS"] == "麻醉":
            narcosisCost=narcosisCost+data["COSTS"]
        if data["ITEM_CLASS"] == "护理":
            nurseCost=nurseCost+data["COSTS"]
        if data["ITEM_CLASS"]== "膳食":
            dietCost=dietCost+data["COSTS"]
        if data["ITEM_CLASS"]== "血费":
            booldCost=booldCost+data["COSTS"]
        if data["ITEM_CLASS"]== "床位":
            bedCost=bedCost+data["COSTS"]
        if data["ITEM_CLASS"]== "材料":
            materialCost=materialCost+data["COSTS"]
        if data["ITEM_CLASS"] == "其他":
            otherCost=otherCost+data["COSTS"]

        costsTotal=costsTotal+data["COSTS"]
        chargesTotal=chargesTotal+data["CHARGES"]



        if "ITEM_CLASS"in data and data["ITEM_CLASS"]!=None:
            str={
                    "type":data["ITEM_CLASS"],
                    "name":data["ITEM_NAME"],
                    "unit":data["UNITS"],
                    "unit_price":data["UNIT_PRICE"],
                    "number": data["AMOUNT"],
                    "costs": round(data["COSTS"],2),
                    "charges": round(data["CHARGES"],2)
                }
            #去除重复的数据
            a=len(result)
            log=0
            for b in result:
                if a!=0:
                    if result[a-1]["name"]==str["name"]:
                        log=1
                        result[a-1]["number"]=result[a-1]["number"]+str["number"]
                        result[a-1]["costs"] =round((result[a-1]["costs"]+str["costs"]),2)
                        result[a-1]["charges"]=round((result[a-1]["charges"]+str["charges"]),2)
                        break
                    else:
                        a-=1
               # del b
            if log==0:
               result.append(str)

    result.append({"costsTotal":"%.2f"%costsTotal,"chargesTotal":"%.2f"%chargesTotal,"drugCost":"%.2f"%drugCost,
                   "examCost":"%.2f"%examCost,"labCost":"%.2f"%labCost,"cureCost":"%.2f"%cureCost,
                   "operationCost":"%.2f"%operationCost,"narcosisCost":"%.2f"%narcosisCost,"nurseCost":"%.2f"%nurseCost,
                   "dietCost":"%.2f"%dietCost,"booldCost":"%.2f"%booldCost,"bedCost":"%.2f"%bedCost,
                   "materialCost":"%.2f"%materialCost,"otherCost":"%.2f"%otherCost
                   })
    # if drugCost!=0:
    #     result["drugCost"]=drugCost

        # result["coststotal"]=coststotal
        # result["chargestotal"]=chargestotal
    # print("costresult:%s"%result)
    return result

'''
入口参数：cases, pretreatment, pretreatmentNone, startTime, endTime, limitNumber,
出口参数：result
函数作用：用于数据预处理，
处理原理：1.从endTime开始查询其每天的时间，若果为None，则将其数据存储到pretreatmentNone这个集合中，
不为None，则存入pretreatment，并且返回None。
'''
#治疗
def treatmentInfomation(costdetail,caseID):
    result = []
    case = copy.copy(caseID)
    case["ITEM_CLASS"] = "治疗"
    treatmentdata=costdetail.find(case)
    for data in treatmentdata:
        if data !={} and data != None:
            if "SETTLING_DATE" in data and data["SETTLING_DATE"]!=None:
                pass
            else:
                data["SETTLING_DATE"] = "无"
            if "ITEM_NAME" in data and data["ITEM_NAME"]!=None:
                pass
            else:
                data["ITEM_NAME"] = "无"
            if "DOCTOR_NAME" in data and data["DOCTOR_NAME"] != None:
                pass
            else:
                data["DOCTOR_NAME"] = "无"
            result.append(
                {
                    "date": data["SETTLING_DATE"],  # 时间
                    "name": data["ITEM_NAME"],  # 类型
                    "doctor":data["DOCTOR_NAME"]
                }
            )
    if result == []:
        result = "无"
    print("治疗信息：%s"%result)
    return result
#麻醉
def narcosisInfomation(costdetail,caseID):
    result = []
    case = copy.copy(caseID)
    case["ITEM_CLASS"] = "麻醉"
    narcosisdata=costdetail.find(case)
    for data in narcosisdata:
        if data !={} and data != None:
            if "SETTLING_DATE" in data and data["SETTLING_DATE"]!=None:
                pass
            else:
                data["SETTLING_DATE"] = "无"
            if "ITEM_NAME" in data and data["ITEM_NAME"]!=None:
                pass
            else:
                data["ITEM_NAME"] = "无"
            if "DOCTOR_NAME" in data and data["DOCTOR_NAME"] != None:
                pass
            else:
                data["DOCTOR_NAME"] = "无"
            result.append(
                {
                    "date": data["SETTLING_DATE"],  # 时间
                    "name": data["ITEM_NAME"],  # 类型
                    "doctor":data["DOCTOR_NAME"]
                }
            )
    if result == []:
        result = "无"
    print("麻醉信息：%s" % result)
    return result
#护理
def nurseInfomation(costdetail,caseID):
    result = []
    case = copy.copy(caseID)
    case["ITEM_CLASS"] = "护理"
    narcosisdata=costdetail.find(case)
    for data in narcosisdata:
        if data !={} and data != None:
            if "SETTLING_DATE" in data and data["SETTLING_DATE"]!=None:
                pass
            else:
                data["SETTLING_DATE"] = "无"
            if "ITEM_NAME" in data and data["ITEM_NAME"]!=None:
                pass
            else:
                data["ITEM_NAME"] = "无"
            if "DOCTOR_NAME" in data and data["DOCTOR_NAME"] != None:
                pass
            else:
                data["DOCTOR_NAME"] = "无"
            result.append(
                {
                    "date": data["SETTLING_DATE"],  # 时间
                    "name": data["ITEM_NAME"],  # 类型
                    "doctor":data["DOCTOR_NAME"]
                }
            )
    case2 = copy.copy(caseID)
    case2["ITEM_CLASS"] = "其他"
    case2["ITEM_NAME"] = {"$regex": "护理"}
    # case ["$and"].append({"ITEM_NAME":{"$regex":"床位"}})
    narcosisdata2 = costdetail.find(case2)
    for data2 in narcosisdata2:
        if data2 != {} and data2 != None:
            if "SETTLING_DATE" in data2 and data2["SETTLING_DATE"] != None:
                pass
            else:
                data2["SETTLING_DATE"] = "无"
            if " ITEM_NAME" in data2 and data2["ITEM_NAME"] != None:
                pass
            else:
                data2[" ITEM_NAME"] = "无"
            if " DOCTOR_NAME" in data2 and data2["DOCTOR_NAME"] != None:
                pass
            else:
                data2[" DOCTOR_NAME"] = "无"
            result.append(
                {
                    "date": data2["SETTLING_DATE"],  # 时间
                    "name": data2["ITEM_NAME"],  # 类型
                    "doctor": data2["DOCTOR_NAME"]
                }
            )
    if result == []:
        result = "无"
    print("护理信息：%s" % result)
    return result
#血费
def bloodInfomation(costdetail,caseID):
    result = []
    case = copy.copy(caseID)
    case["ITEM_CLASS"] = "血费"
    narcosisdata=costdetail.find(case)
    for data in narcosisdata:
        if data !={} and data != None:
            if "SETTLING_DATE" in data and data["SETTLING_DATE"]!=None:
                pass
            else:
                data["SETTLING_DATE"] = "无"
            if "ITEM_NAME" in data and data["ITEM_NAME"]!=None:
                pass
            else:
                data["ITEM_NAME"] = "无"
            if "DOCTOR_NAME" in data and data["DOCTOR_NAME"] != None:
                pass
            else:
                data["DOCTOR_NAME"] = "无"
            result.append(
                {
                    "date": data["SETTLING_DATE"],  # 时间
                    "name": data["ITEM_NAME"],  # 类型
                    "doctor":data["DOCTOR_NAME"]
                }
            )
    if result == []:
        result = "无"
    return result
#床位
def bedInfomation(costdetail,caseID):
    result = []
    case = copy.copy(caseID)
    case["ITEM_CLASS"] = "床位"
    narcosisdata=costdetail.find(case)
    for data in narcosisdata:
        if data !={} and data != None:
            if "SETTLING_DATE" in data and data["SETTLING_DATE"]!=None:
                pass
            else:
                data["SETTLING_DATE"] = "无"
            if "ITEM_NAME" in data and data["ITEM_NAME"]!=None:
                pass
            else:
                data["ITEM_NAME"] = "无"
            if "DOCTOR_NAME" in data and data["DOCTOR_NAME"] != None:
                pass
            else:
                data["DOCTOR_NAME"] = "无"
            result.append(
                {
                    "date": data["SETTLING_DATE"],  # 时间
                    "name": data["ITEM_NAME"],  # 类型
                    "doctor":data["DOCTOR_NAME"]
                }
            )
    case2=copy.copy(caseID)
    case2["ITEM_CLASS"] = "其他"
    case2["ITEM_NAME"]={"$regex":"床位"}
    # case ["$and"].append({"ITEM_NAME":{"$regex":"床位"}})
    narcosisdata2 = costdetail.find(case2)
    for data2 in narcosisdata2:
        if data2 !={} and data2 != None:
            if "SETTLING_DATE" in data2 and data2["SETTLING_DATE"]!=None:
                pass
            else:
                data2["SETTLING_DATE"] = "无"
            if " ITEM_NAME" in data2 and data2["ITEM_NAME"]!=None:
                pass
            else:
                data2[" ITEM_NAME"] = "无"
            if " DOCTOR_NAME" in data2 and data2["DOCTOR_NAME"] != None:
                pass
            else:
                data2[" DOCTOR_NAME"] = "无"
            result.append(
                {
                    "date": data2["SETTLING_DATE"],  # 时间
                    "name": data2["ITEM_NAME"],  # 类型
                    "doctor":data2["DOCTOR_NAME"]
                }
            )
    if result == []:
        result = "无"
    return result
#膳食
def foodInformation(costdetail,caseID):
    result = []
    case = copy.copy(caseID)
    case["ITEM_CLASS"] = "膳食"
    narcosisdata = costdetail.find(case)
    for data in narcosisdata:
        if data != {} and data != None:
            if "SETTLING_DATE" in data and data["SETTLING_DATE"] != None:
                pass
            else:
                data["SETTLING_DATE"] = "无"
            if "ITEM_NAME" in data and data["ITEM_NAME"] != None:
                pass
            else:
                data["ITEM_NAME"] = "无"
            if "DOCTOR_NAME" in data and data["DOCTOR_NAME"] != None:
                pass
            else:
                data["DOCTOR_NAME"] = "无"
            result.append(
                {
                    "date": data["SETTLING_DATE"],  # 时间
                    "name": data["ITEM_NAME"],  # 类型
                    "doctor": data["DOCTOR_NAME"]
                }
            )
    if result == []:
        result = "无"
    print("膳食信息：%s" % result)
    return result
#材料
def materialInfomation(costdetail,caseID):
    foodresult = []
    materialresult = []
    case = copy.copy(caseID)
    case["ITEM_CLASS"] = "材料"
    narcosisdata=costdetail.find(case)
    for data in narcosisdata:
        # m = re.search("流质*",data["ITEM_NAME"])
        # n = re.search("普食*", data["ITEM_NAME"])
        # o = re.search("软食*", data["ITEM_NAME"])
        # p = re.search("半流*", data["ITEM_NAME"])
        if "SETTLING_DATE" in data and data["SETTLING_DATE"] != None:
            pass
        else:
            data["SETTLING_DATE"] = "无"
        if "DOCTOR_NAME" in data and data["DOCTOR_NAME"] != None:
            pass
        else:
            data["DOCTOR_NAME"] = "无"
        # if m or n or o or p :
        #     foodresult.append(
        #         {
        #             "date": data["SETTLING_DATE"],  # 时间
        #             "name": data["ITEM_NAME"],  # 类型
        #             "doctor":data["DOCTOR_NAME"]
        #         }
        #     )
        # else:
            materialresult.append(
                {
                    "date": data["SETTLING_DATE"],  # 时间
                    "name": data["ITEM_NAME"],  # 类型
                    "doctor": data["DOCTOR_NAME"]
                }
            )
    # if foodresult == []:
    #     foodresult = "无"
    if materialresult == []:
        materialresult = "无"
    # print("膳食信息：%s" % foodresult)
    # print("材料信息：%s"%materialresult)
    return materialresult
#其他
def otherInfomation(costdetail,caseID):
    result = []
    case = copy.copy(caseID)
    case["ITEM_CLASS"] = "其他"
    narcosisdata=costdetail.find(case)
    for data in narcosisdata:
        if data !={} and data != None:
            if "ITEM_NAME" in data and (data["ITEM_NAME"]=="一级护理"or
                                                data["ITEM_NAME"]=="二级护理"or
                                                data["ITEM_NAME"] == "三级护理"or
                                                data["ITEM_NAME"] == "I级护理" or
                                                data["ITEM_NAME"] == "II级护理" or
                                                data["ITEM_NAME"] == "III级护理" or
                                                data["ITEM_NAME"] == "普通病床" or
                                                data["ITEM_NAME"] == "普通床位" ):
                continue
            if "SETTLING_DATE" in data and data["SETTLING_DATE"]!=None:
                pass
            else:
                data["SETTLING_DATE"] = "无"
            if "ITEM_NAME" in data and data["ITEM_NAME"]!=None:
                pass
            else:
                data["ITEM_NAME"] = "无"
            if "DOCTOR_NAME" in data and data["DOCTOR_NAME"] != None:
                pass
            else:
                data["DOCTOR_NAME"] = "无"
            result.append(
                {
                    "date": data["SETTLING_DATE"],  # 时间
                    "name": data["ITEM_NAME"],  # 类型
                    "doctor":data["DOCTOR_NAME"]
                }
            )
    if result == []:
        result = "无"
    return result

