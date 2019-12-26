#import MySQLdb
#import mysql.connector
import pymysql.cursors
import sys

def db_connect(dbname):
    try:
        #db = MySQLdb.connect(host="127.0.0.1", port=1234, user="starreco", passwd="", db=dbname)
        db = pymysql.connect(host="127.0.0.1", port=1234, user="starreco", passwd="", db=dbname)
    except:
        print("Can't connect to database!!!")
        return 0
    #print("Connected to database")
    try:
        cur = db.cursor()
    except:
        print("Can't have cursor!!!")
        return 0
    # print("Got the cursor")
    dbretrun = {}
    dbretrun["db"]=db
    dbretrun["cursor"]=cur
    return dbretrun

def db_execute(dbname,query):
    # print("Yor are in the db")
    dbreturn = db_connect(dbname)
    cur = dbreturn.get("cursor")
    db = dbreturn.get("db")
    try:
        result = cur.execute(query)
        resultD = {
            "count": result,
            "output": cur
        }
        db.close()
        return resultD
    except:
        print("Can't execute SQL query: " + query)
        db.close()
        return 0


def dbexecute(query, dbstr="LibraryJobs"):
        try:
            #db = MySQLdb.connect(host="127.0.0.1",port=1234,user="starreco",passwd="",db=dbstr)
            db = pymysql.connect(host="127.0.0.1", port=1234, user="starreco", passwd="", db=dbstr)
        except:
            print("Can't connect to database!!!")
            return 0
        #print("Connected to database")
        try:
            cur = db.cursor()
        except:
            print("Can't have cursor!!!")
            return 0
        #print("Got the cursor")
        try:
            cur.execute(query)
        except:
            print("Unable to execute the query!!!")
            return 0
        db.close()
        return cur


def ExecuteQuery(query):
        try:
            #db = MySQLdb.connect(host="127.0.0.1", port=1234, user="starreco", passwd="", db="LibraryJobs")
            db = pymysql.connect(host="127.0.0.1", port=1234, user="starreco", passwd="", db="LibraryJobs")
            #db = mysql.connector.connect(host="duvall.star.bnl.gov",port=3306,user="starreco",passwd="",db="LibraryJobs")
        except:
            print("Can't connect to database!!!")
            return 0
        #print("Connected to database")
        try:
            cur = db.cursor()
        except:
            print("Can't have cursor!!!")
            db.close()
            return 0
        try:
            result = cur.execute(query)
            resultD = {
                "count":result,
                "output":cur
            }
            db.close()
            return resultD
        except:
            print("Can't execute SQL query: "+query)
            db.close()
            return 0

def TableDescribe(table):
        try:
            #db = MySQLdb.connect(host="127.0.0.1", port=1234, user="starreco", passwd="", db="LibraryJobs")
            db = pymysql.connect(host="127.0.0.1", port=1234, user="starreco", passwd="", db="LibraryJobs")
            #db = MySQLdb.connect(host="duvall.star.bnl.gov", port=3306, user="starreco", passwd="", db="LibraryJobs")
        except:
            print("Can't connect to database!!!")
            return 0
        #print("Connected to database")
        try:
            cur = db.cursor()
        except:
            print("Can't get cursor!!!")
            return 0
        try:
            cur.execute("describe " + table)
        except:
            print("Can't execute describe table for:"+table)
        columns = []
        # columns.clear()
        for line in cur:
            columns.append(line[0])

        return columns

        # columns = TableDescribe("DatasetChainCombo")
        # for column in columns:
        #	print(column)
        # print(columns.index("ID"))


# def FetchChangePercent(parameter, dataset=0):
def FetchChangePercent(dataset=0):
        # result = ExecuteQuery("select "+parameter+" from DatasetPrecision where DatasetChainComboID="+str(dataset))
        result = ExecuteQuery("select * from DatasetPrecision where DatasetChainComboID=" + str(dataset))
        percentlist = []
        for percent in result.get("output"):
            for value in percent:
                percentlist.append(value)
        return percentlist


# def Compare(tableclmnsjs,first,second,parameter,percent):
def Compare(tableclmnsjs, tableclmnsdp, first, second, precisionlist):
        first_time = first[tableclmnsjs.index("createTime")]
        second_time = second[tableclmnsjs.index("createTime")]
        # Check the time difference before executing parameter difference
        change3 = 0
        if abs((first_time - second_time).days) < 60:
            start = 0
            percentlist = []
            for parameter in tableclmnsdp:
                if start != 0:
                    first_para = first[tableclmnsjs.index(parameter)]
                    second_para = second[tableclmnsjs.index(parameter)]
                    # percent = FetchChangePercent(parameter)
                    percent = precisionlist[tableclmnsdp.index(parameter)]
                    percent = percent / 100.0
                    greater = first_para + percent * float(first_para)
                    lesser = first_para - percent * float(first_para)
                    if second_para > greater or second_para < lesser:
                        # print("DatasetID:"+str(first[tableclmnsjs.index("DatasetChainID")])+"-->"+parameter
                        # +":Time="+str(first_time)+" Value="+str(first[tableclmnsjs.index(parameter)])
                        # +" Time="+str(second_time)+" Value="+str(second[tableclmnsjs.index(parameter)])
                        # +"  "+str(greater)+"  "+str(lesser)+"  "+str(percent))
                        change3 = change3 + 1

                    if first_para == second_para:
                        percentlist.append(0.0)
                    else:
                        if first_para != 0 and second_para != 0:
                            minus = abs(float(second_para) - float(first_para))
                            # if second_para > first_para:
                            #	percentlist.append((minus/float(second_para))*100.0)
                            # else:
                            percentlist.append((minus / float(first_para)) * 100.0)
                        else:
                            percentlist.append(100.0)

                start = start + 1
            # insert the change into DatasetResultChange table
            makestring = ""
            for num in percentlist:
                makestring = makestring + ", "
                makestring = makestring + str(num)
            listtoinsert = ""
            track = 0
            for data in tableclmnsdp:
                if track != 0:
                    listtoinsert = listtoinsert + ", " + data
                track = track + 1
            if change3 >= 1:
                # check the existance of the record
                # search = ExecuteQuery("select * from DatasetResultChange where DatasetchainCombo="+
                #			str(first[tableclmnsjs.index("DatasetChainID")])+
                #			"and DayTime1='"+str(first_time)+"' and DayTime2='"+str(second_time)+"'")
                # if search.get("count")>0:
                insert = ExecuteQuery(
                    "insert into DatasetResultChange (DatasetChainComboID, DayTime1, DayTime2 " + listtoinsert + ") values(" +
                    str(first[tableclmnsjs.index("DatasetChainID")])
                    + ", '" + str(first_time) + "', '" + str(second_time) + "'" + makestring + ")")

        return change3


# def PointoutDifference(dcyid,result2,tableclmnsjs,parameter):
def PointoutDifference(dcyid, result2, tableclmnsjs, tableclmnsdp, precisionlist):
        count1 = 0
        cur2 = result2.get("output")
        # percent = FetchChangePercent(parameter)
        # count3 = 0 (for knowing how many records)
        for row2 in cur2:
            if count1 == 0:
                first = row2
                # print("First="+str(first))
            else:
                second = row2
                count1 = count1 + Compare(tableclmnsjs, tableclmnsdp, first, second, precisionlist)
                # if Compare(tableclmnsjs,first,second,parameter,percent)==1:
                #        count3 = count3 + 1
                # number of changes within datasetid
                # print("Second="+str(second))
                first = second
            count1 = count1 + 1

        return count1


def UpdateDatasetResultChange():
        count = 0
        tableclmnsdcc = TableDescribe("DatasetChainCombo")
        tableclmnsjs = TableDescribe("JobStatus")
        tableclmnsdp = TableDescribe("DatasetPrecision")
        precisionlist = FetchChangePercent()
        result1 = ExecuteQuery("select * from DatasetChainCombo")
        cur1 = result1.get("output")

        for row1 in cur1:
            dcyid = row1[tableclmnsdcc.index("ID")]
            # Gather information based on Dataset
            result2 = ExecuteQuery("select * from JobStatus where DatasetChainID=" + str(
                dcyid) + " and ChangeConsider = 'N' and jobStatus='Done' and LibLevel='dev'")

            count = count + PointoutDifference(dcyid, result2, tableclmnsjs, tableclmnsdp, precisionlist)
            print("Completed for DatasetChainID:" + str(dcyid))
            # Now you have to update the ChangeConsider from N to Y of JobStatus
            result2 = ExecuteQuery("update JobStatus set ChangeConsider = 'Y' where DatasetChainID=" + str(
                dcyid) + " and ChangeConsider = 'N' and jobStatus='Done' and LibLevel='dev'")

        print("Total no of changes:" + str(count))
        return count

def FlushTable(table):
        result = ExecuteQuery("truncate table "+table)
        #sqlquery = "Update JobStatus set ChangeConsider='N' where id>0"
        #new = ExecuteQuery(sqlquery)
        return 1


def UpdateAllTables():
            check = True
            count = 0
            count2 = 0
            dict = {
                "jobstatus": count,
                "datachaincombo": count2,
            }
            while check==True:
              count = 0
              count2 = 0
              #Gather the data
              result1 = ExecuteQuery("select path,chainOpt,prodyear from JobStatus where DatasetChainID is null")
              row_count = result1.get("count")
              cur = result1.get("output")
              print("Gather new data successfuly from JobStatus.." + str(row_count))
              if row_count > 0:
                dc = {"datasetchain", "chain"}
                dc.clear()
                for line in cur:
                    opt = -1
                    opt = line[0].find("_opt") #Find Optimized or not
                    dataname = line[0].split("/")
                    dataname.reverse()
                    if opt >= 0:
                        dataname[0] = dataname[0] + "_opt"
                    dcstr = dataname[0] + "$" + line[1] + "$" + str(line[2])
                    dcid = 0
                    if dcstr not in dc:
                        dc.add(dcstr)
                        # Search the DatssetChainCombo table before updating JobStatus
                        searchstmnt = "select * from DatasetChainCombo where Dataset='" + dataname[
                                0] + "' and ChainOpt='" + line[1] + "' and Prodyear=" + str(line[2]) + ""
                        result1 = ExecuteQuery(searchstmnt)
                        row_count = result1.get("count")
                        # If the dataset is not present in DatasetChainCombo
                        if row_count == 0:
                                # First update DatasetChainCombo
                                sqlstmnt = "insert into DatasetChainCombo (Dataset, ChainOpt, Prodyear) values('" + dataname[
                                           0] + "','" + line[1] + "'," + str(line[2]) + ")"
                                new = ExecuteQuery(sqlstmnt)
                                count2 = count2 + 1
                                # Get the DatasetChainID
                                searchstmnt = "select * from DatasetChainCombo where Dataset='" + dataname[
                                    0] + "' and ChainOpt='" + line[1] + "' and Prodyear=" + str(line[2]) + ""
                                new = ExecuteQuery(searchstmnt)
                                cur = new.get("output")
                                for rowid in cur:
                                    dcid = rowid[0]
                        else:
                            cur = result1.get("output")
                            for rowid in cur:
                                dcid = rowid[0]

                        # Second update JobStatus
                        sqlstmnt = "update JobStatus set Dataset='" + dataname[0] + "', DatasetChainID=" + str(
                            dcid) + " where path='" + line[0] + "' and chainOpt='" + line[1] + "' and prodyear="+str(line[2])+""
                        new = ExecuteQuery(sqlstmnt)
                        count = count + new.get("count")

                dict["jobstatus"] = dict.get("jobstatus")+count
                dict["datachaincombo"] = dict.get("datachaincombo") + count2

              else:
                check=False

            return dict


def ResetAllFramework():
        #clear the JobStatus table
        sqlquery = "Update JobStatus set DatasetChainID=NULL, Dataset=NULL, ChangeConsider='N' where id>0"
        new = ExecuteQuery(sqlquery)
        #clear the DatasetChainCombo table
        sqlquery = "truncate DatasetChainCombo"
        new = ExecuteQuery(sqlquery)
        #clear the DatasetResultChange
        sqlquery = "truncate DatasetResultChange"
        new = ExecuteQuery(sqlquery)
        #Update the DatasetChainCombo and JobStatus table
        UpdateAllTables();
        #Update the DatasetResultChange table
        UpdateDatasetResultChange();
        return 1;