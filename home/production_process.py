from home import dbaccess
from datetime import date, timedelta, datetime
import numpy


def GetPicoStatus(year, starttime, endtime):
    # print("Yor are in the function")
    tablename = "jobs_prod_"+year
    query = "SELECT count(*),concat(datasetName,'(' ,prodTag,')'),cast(outputCreateTime as date) FROM "+tablename+ \
            " where outputCreateTime>='"+starttime+"' and outputCreateTime<='"+endtime+"' " \
            "group by prodTag, datasetName, outputCreateTime" \
            " order by outputCreateTime"
    result = dbaccess.db_execute("Embedding_job_stats",query)
    #print(query)
    output = result.get("output")
    datelist = []
    datasetlist = []
    ddlist = []
    jobcount = []
    dict = {}
    for row in output:
        #print(row)
        if str(row[2]) not in datelist:
           datelist.append(str(row[2]))
        if row[1] not in datasetlist:
           datasetlist.append(row[1])
        dd = row[1]+"#"+str(row[2])
        if dd not in ddlist:
           ddlist.append(dd)
           jobcount.append(int(row[0]))
        else:
           index = ddlist.index(dd)
           jobcount[index] = jobcount[index]+int(row[0])

    matrix = numpy.zeros((len(datelist), len(datasetlist)))

    for dt in datelist:
        for dd in ddlist:
            if dd.find(dt)>=0:
                parts = dd.split("#")
                x = datelist.index(parts[1])
                y = datasetlist.index(parts[0])
                index = ddlist.index(dd)
                matrix[x][y] = jobcount[index]


    dict["datelist"] = datelist
    dict["datasetlist"] = datasetlist
    dict["jobcountmatrix"] = matrix

    #print(matrix)
    return dict

def GetPicoPred(year, yesterday, files):
    tablename = "jobs_prod_" + year

    query ="SELECT distinct datasetName FROM "+tablename+ \
           " where outputCreateTime >= '"+yesterday+"'"
    result = dbaccess.db_execute("Embedding_job_stats", query)

    output = result.get("output")
    datasetlist =[]
    for row in output:
        #print(row[0])
        datasetlist.append(row[0])
    dataset_name = datasetlist[0]

    query ="SELECT date_format(outputCreateTime, '%Y-%m-%d'), count(*) FROM "+tablename+ \
     " where datasetName='"+dataset_name+"' and recoStatus='completed' group by date_format(outputCreateTime, '%Y-%m-%d') ASC"
    result = dbaccess.db_execute("Embedding_job_stats", query)

    output = result.get("output")
    datelist = []
    jobcout = []
    dayjobs = []
    pred_jobcount = []
    pred_jobcount4 = []
    total_jobs = 0
    for row in output:
        datelist.append(str(row[0]))
        total_jobs = total_jobs + row[1]
        dayjobs.append(row[1])
        jobcout.append(total_jobs)
        pred_jobcount.append(0)
        pred_jobcount4.append(0)
    ###############################################
    avg_jobs_day = int(total_jobs/len(datelist))
    avg_jobs_4days = int((dayjobs[-1]+dayjobs[-2]+dayjobs[-3]+dayjobs[-4])/4)
    remaining_files = files - total_jobs
    remaining_days = int(remaining_files/avg_jobs_day)
    remaining_4days = int(remaining_files/avg_jobs_4days)
    if remaining_4days>remaining_days:
        rday = remaining_4days
    else:  rday = remaining_days
    total_jobs4 = total_jobs
    for i in range(1,rday+1):
        dt = str(date.today() + timedelta(i))
        datelist.append(dt)
        jobcout.append(0)
        if i < (remaining_days+1):
            total_jobs = total_jobs + avg_jobs_day
            pred_jobcount.append(total_jobs)
        else: pred_jobcount.append(0)
        if i < (remaining_4days + 1):
            total_jobs4 = total_jobs4 + avg_jobs_4days
            pred_jobcount4.append(total_jobs4)
        else: pred_jobcount4.append(0)
    ###############################################
    dict = {}
    dict["datelist"] = datelist
    dict["jobcount"] = jobcout
    dict["datasetlist"] = datasetlist
    dict["predjobcount"] = pred_jobcount
    dict["predjobcount4"] = pred_jobcount4
    return dict

def GetTables():
    # --Get the table list--
    query = "show tables"
    result = dbaccess.db_execute("Embedding_job_stats", query)
    output = result.get("output")
    tablelist = []
    for row in output:
        row1 = str(row)
        if row1.find("jobs_prod_") >= 0:
            temp = row1
            temp = temp.split("_prod_")
            tablelist.append(temp[1].split("'")[0])

    return tablelist


def GetCRSdetails():
    # --Get the table list--
    query = "SELECT count(*), status, trigset, prodtag, runDate FROM CRSJobsInfo group by status, trigset, prodtag, runDate order by runDate"
    result = dbaccess.db_execute("operation", query)
    output = result.get("output")
    triglist = []
    prodlist = []
    statlist = []
    numblist = []
    datelist = []
    length = 0
    for row in output:
        if len(row[1])>0:
            length = length + 1
            triglist.append(row[2])
            prodlist.append(row[3])
            statlist.append(row[1])
            numblist.append(row[0])
            datelist.append(row[4])

    dict = {}
    dict["trig"] = triglist
    dict["prod"] = prodlist
    dict["stat"] = statlist
    dict["numb"] = numblist
    dict["date"] = datelist
    dict["leng"] = length
    return dict

def GetChainDetails():
    query =  "select trgsetName,collision,yearData,prodTag,chainOpt from ProductionChains"
    result = dbaccess.db_execute("operation", query)
    output = result.get("output")
    dict = {}
    count = 1
    for row in output:
        dict[count]=row
        count = count + 1

    return dict

def GetDiskDetails():
    dict = {}
    return dict