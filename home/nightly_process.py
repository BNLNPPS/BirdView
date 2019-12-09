from home import dbaccess
from email.headerregistry import Address
from email.message import EmailMessage
import os
import smtplib
from datetime import datetime, date, timedelta

def DescribeTable(table):
    query = "describe "+table
    result = dbaccess.dbexecute(query)
    column_name = []
    for line in result:
        column_name.append(line[0])
    return column_name

def fetch_Library_data(datasetid, para, chainid):
    query = "select path,LibTag,"+para+" from siteJobStatus where LibLevel='new' and chainOpt='"+chainid+"' and path like '%"+datasetid+"' order by createTime ASC"
    print(query)
    result = dbaccess.dbexecute(query)
    resultdict = {}
    for row in result:
        if datasetid.find("opt")>=0:
           if row[0].find("opt")>=0:
              resultdict[str(row)] = row
        else:
           if row[0].find("opt")<0:
              resultdict[str(row)] = row
    print(resultdict)
    return resultdict

def fetchPrecisionTable():
    query = "select * from DatasetPrecision"
    result = dbaccess.dbexecute(query)
    query1 = "describe DatasetPrecision"
    result1 = dbaccess.dbexecute(query1)
    dictionaryResult = { }
    dictionaryResult.clear()
    valuelist = []
    for line in result:
        for value in line:
            valuelist.append(value)
    parameterlist=[]
    for line in result1:
        parameterlist.append(line[0])

    for parameter in parameterlist:
        dictionaryResult[parameter]=valuelist[parameterlist.index(parameter)]

    dataset=dictionaryResult.pop('DatasetChainComboID')

    returndict = {
        "dataset":dataset,
        "dictionary":dictionaryResult
    }

    return returndict



def fetchDatasetChainCombo():
    query = "select * from DatasetChainCombo"
    resultdict = dbaccess.ExecuteQuery(query)
    result = resultdict.get("output")
    redict = { }
    redict.clear()

    for row in result:
        redict[row[0]]=row

    return redict

def fetchDataset(id):
    result = dbaccess.ExecuteQuery("select Dataset from DatasetChainCombo where ID="+id)
    if result.get("count")==1:
        resultdict= result.get("output");
        for line in resultdict:
            dataset = line[0]
            return dataset


def fetchDatasetlist():
    #query = "select ID,Dataset from DatasetChainCombo"
    #result = dbaccess.dbexecute(query)

    #resultdict = { }
    #resultdict.clear()

    #for row in result:
    #    resultdict[row[0]]=row[1]
    count = 0
    resultdict = dbaccess.ExecuteQuery("select distinct Dataset from DatasetChainCombo order by Dataset ASC")
    result = resultdict.get("output")
    redict = {}
    for row in result:
        redict[count]=row[0]
        count = count + 1

    return redict

def fetchYearlist():
    query = "select distinct Prodyear from DatasetChainCombo order by Prodyear ASC"
    result = dbaccess.dbexecute(query)

    resultdict = { }
    resultdict.clear()
    count = 0
    for row in result:
        resultdict[count]=row[0]
        count = count + 1

    return resultdict

def fetchChainlist():
    query = "select distinct ChainOpt from DatasetChainCombo order by ChainOpt ASC"
    result = dbaccess.dbexecute(query)

    resultdict = { }
    resultdict.clear()
    count = 0
    for row in result:
        resultdict[count]=row[0]
        count = count + 1

    return resultdict

def UpdateParameter(parameter,value,dataset=0):
    query = "update DatasetPrecision set "+parameter+"="+str(value)+" where DatasetChainComboID="+str(dataset)+""
    #result = dbaccess.dbexecute(query)
    result = dbaccess.ExecuteQuery(query)
    return result

def getComboID(datasetid,chainid,yearid):
    query = "select ID from DatasetChainCombo where Dataset='"+datasetid+"' and ChainOpt='"+chainid+"' and Prodyear="+yearid+""
    result = dbaccess.dbexecute(query)
    for id in result:
        dsid=id[0]
    return dsid

def gatherData(comboid,starttime,endtime,parameter):
    query = "select ID,DayTime1,DayTime2,"+parameter+" from DatasetResultChange where DatasetChainComboID="+str(comboid)+" and DayTime1>='"+starttime+"' and DayTime2<='"+endtime+"'"
    result = dbaccess.dbexecute(query)

    resultdict = {}
    resultdict.clear()
    for row in result:
        resultdict[row[0]]=row

    return resultdict

def fetchgraphdata(datasetid, parameter, starttime, endtime):
    # if starttime < endtime:
    #     time1 = starttime
    #     starttime = endtime
    #     endtime = time1
    #newstarttime = str(datetime.strptime(starttime,"%Y-%m-%d")-timedelta(7))
    #newendtime = str(datetime.strptime(endtime,"%Y-%m-%d")+timedelta(7))
    #print(starttime+"--"+newstarttime)
    #print(endtime+"--"+newendtime)
    query = "select createTime,"+parameter+" from JobStatus where DatasetChainID="+str(datasetid)+" and createTime>='"+starttime+"' and createTime<='"+endtime+"' and jobStatus='Done'"
    print(query)
    result = dbaccess.dbexecute(query)

    resultdict = {}
    resultdict.clear()

    for row in result:
            resultdict[str(row[0])]=row[1]
            #print(row)

    return resultdict


def reevaluatechange():
    #First update JobStatus table
    dbaccess.UpdateAllTables()
    #Flush the DatasetResultChange table
    dbaccess.FlushTable("DatasetResultChange")
    #Make ChangeConsider parameter to 'N'
    result2 = dbaccess.ExecuteQuery("Update JobStatus set ChangeConsider='N' where id>0")
    #Add the new results into DatasetResultChange
    changes = dbaccess.UpdateDatasetResultChange()
    return changes
    #return 0


def synchronise():
    # First update JobStatus table
    dbaccess.UpdateAllTables()
    # Add the new results into DatasetResultChange
    changes = dbaccess.UpdateDatasetResultChange()
    return changes

def SendNotifications():
    return 0

def SendEmail(subject, body, tolist):
    #email_address = "amol@bnl.gov"
    #tolist = ['asdf@bnl.gov','ert@bnl.gov','oupr@bnl.gov']
    #subject = "Notification for xyz"
    #body = "Please check the library, execution did not follow precision value"
    msg = EmailMessage()
    msg['From'] = ['amol@bnl.gov']
    msg['To'] = tolist
    msg['Subject'] = subject
    msg.set_content(body)

    with smtplib.SMTP('smtp.bnl.gov', port=25) as smtp_server:
        smtp_server.ehlo()
        # smtp_server.starttls()
        # smtp_server.login(email_address, email_password)
        smtp_server.send_message(msg)

    print('Email sent successfully')


