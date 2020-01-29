# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import date, timedelta, datetime
from django.shortcuts import render
from home import nightly_process,dbaccess,production_process
from django.contrib import messages
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.models import User
from django.shortcuts import redirect
import _thread
import time
import numpy

# import json
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.renderers import TemplateHTMLRenderer
# from django.views.generic import TemplateView
# from django.shortcuts import HttpResponse

from django.template.defaulttags import register

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)




def UpdateAllTableThread(delay):
    print("--------------------------------------------------------------")
    print("Update All Tables started at: "+str(time.ctime(time.time())))
    dict = dbaccess.UpdateAllTables()
    print("--------------------------------------------------------------")
    time.sleep(delay)

def NotificationThread(delay):
    print("--------------------------------------------------------------")
    print("Notification started at: "+str(time.ctime(time.time())))
    nightly_process.SendNotifications()
    print("--------------------------------------------------------------")
    time.sleep(delay)



def userlogout(request):
      logout(request)
      #return render(request, "login.html")
      return redirect('/')

def userLogin(request):
    if request.method == "POST" and 'signin' in request.POST:
       userid = request.POST['inputEmail']
       userpass = request.POST['inputPassword']
       user = authenticate(username=userid, password=userpass)
       if user is not None:
           login(request,user)
           return render(request, "index.html")
       else:
           messages.error(request, 'Please verify credentials !!!', extra_tags='danger')
           return render(request, "login.html")
    else:
       return render(request, "login.html")


def index(request):
      # if request.method == "POST" and 'signin' in request.POST:
      #        userid = request.POST['inputEmail']
      #        userpass = request.POST['inputPassword']
      #        user = authenticate(username=userid, password=userpass)
      #        if user is not None:
      #            login(request,user)
      #            return render(request, "index.html")
      #        else:
      #            messages.error(request, 'Please verify credentials !!!', extra_tags='danger')
      #            return render(request, "login.html")
      #
      # if request.user.is_authenticated:
      #       return render(request, "index.html")
      # else:
      #       return render(request, "login.html" )
      # try:
      #     _thread.start_new_thread(UpdateAllTableThread, (2,)) # Every 2 hour
      #     _thread.start_new_thread(NotificationThread, (4,)) # Every 24 hour
      # except:
      #     print("Error: unable to start thread")
      return render(request,"index.html")


def datarequest(request):
    if request.user.is_authenticated:
        return render(request, "datarequest.html")
    else:
        return render(request,"login.html")

def datarequest_search(request):
    return render(request,"searchdata.html")



def production(request):
    # if not request.user.is_authenticated:
    #     #return render(request, "login.html")
    #     return redirect('/login')
    # else:
        details = production_process.GetCRSdetails()
        triglist = details.get("trig")
        prodlist = details.get("prod")
        statlist = details.get("stat")
        numblist = details.get("numb")
        datelist = details.get("date")
        length = details.get("leng")
        dict = {}
        for count in range(length):
            value = []
            value.append(datelist[count])
            value.append(triglist[count])
            value.append(prodlist[count])
            value.append(statlist[count])
            value.append(numblist[count])
            dict[count]= value


        if request.method == "POST":
            # print(request.POST)
            if 'add' in request.POST:
                return production_add(request)
        return render(request,"production.html", locals())


def production_add(request):
    return render(request, "production_new.html", locals())

def production_disks(request):
    # if not request.user.is_authenticated:
    #     #return render(request, "login.html")
    #     return redirect('/login')
    # else:
        dict = production_process.GetDiskDetails()
        return render(request, "production_disk.html", locals())

def production_pred(request):
    #SELECT date_format(outputCreateTime, '%Y-%m-%d'), count(*) FROM Embedding_job_stats.jobs_prod_2019
    # where datasetName="production_pp200trans_2015" and recoStatus="completed" group by date_format(outputCreateTime, '%Y-%m-%d') ASC;

    #get_file_list.pl -distinct -keys filename -cond trgsetupname=production_pp200trans_2015,production=P16id,filetype=daq_reco_MuDst,storage=hpss,sanity=1 -limit 0 | wc -l

    yesterday = str(date.today()- timedelta(1))
    year = yesterday.split("-")[0]
    files = 190298
    dict_output = production_process.GetPicoPred(year,yesterday, files)

    labels = dict_output.get("datelist")
    datas1 = dict_output.get("jobcount")
    datasetlist = dict_output.get("datasetlist")
    datas2 = dict_output.get("predjobcount")
    datas3 = dict_output.get("predjobcount4")
    datasetid1 = datasetlist[0]
    datasetid2 = "Prediction"
    datasetid3 = "Prediction(4 days avg)"
    length = len(labels)
    paraid1 = "No of files completed"

    return render(request, "production_pred.html", locals())


def production_pico(request):
    # if not request.user.is_authenticated:
    #     # messages.success(request, "This action requires to authenticate..")
    #     return redirect('/login')
    # else:
        tablelist = production_process.GetTables()
        starttime = str(date.today() - timedelta(7))
        endtime = str(date.today())
        year = starttime.split("-")[0]

        if request.method == "POST" and 'submit' in request.POST:
            # print("Yor are in the POST")
            starttime = request.POST['starttime']
            endtime = request.POST['endtime']
            year = request.POST['year']

            if year.find("Choose the ") >= 0 or len(starttime) == 0 or len(endtime) == 0:
                messages.error(request, 'Choose all options correctly!!!', extra_tags='danger')
                return render(request, "production_pico.html", locals())

        dict_output = production_process.GetPicoStatus(year, starttime, endtime)
        #print(dict_output)
        labels = dict_output.get("datelist")
        datasetlist = dict_output.get("datasetlist")
        datas = dict_output.get("jobcountmatrix")
        paraid1 = "No of jobs"
        length = len(datasetlist)
        dataformat = []
        for z in range(len(datasetlist)):
             data = []
             for x in range(len(labels)):
                data.append(datas[x][z])

             dataformat.append(data)
        #print(dataformat)
        return render(request, "production_pico.html", locals())

def production_chains(request):
    # if not request.user.is_authenticated:
    #     #return render(request, "login.html")
    #     return redirect('/login')
    # else:
        dict = production_process.GetChainDetails()
        collist = []
        # chainlist = []
        for row in dict:
            arow = dict.get(row)
            # chainlist.append(arow)
            if arow[1] not in collist:
               collist.append(arow[1])

        collist.sort()
        return render(request,"production_chains.html", locals())

def notification(request):
    query = "select * from Notification"
    result = dbaccess.ExecuteQuery(query)
    dictresult = {}
    if result.get("count") > 0:
        cur = result.get("output")
        for line in cur:
            valarray = []
            for val in line:
                if type(val) is datetime:
                    strd = ""
                    strd = strd + str(val.year) + "-" + str(val.month) + "-" + str(val.day)
                    valarray.append(strd)
                else:
                    if type(val) is str and "," in val:
                        valarray.append(val.count(","))
                    else: valarray.append(val)
            valarray.pop(0) # removing id from the list
            dictresult[line[0]] = valarray
    else:
        messages.error(request, 'There are no notifications!!!', extra_tags='danger')
    if request.method == "POST":
        # print(request.POST)
        if 'add' in request.POST:
            return notification_add(request)
        if 'update' in request.POST:
            return notification_modify(request)
        if 'remove' in request.POST:
            return notification_remove(request)
    return render(request,"notification.html", locals())

def notification_add(request):
    if not request.user.is_authenticated:
        #messages.success(request, "This action requires to authenticate..")
        #messages.error(request, 'Need to login...!!!', extra_tags='danger')
        return redirect('/login')
    else:
        if request.method == "POST" and 'submit' in request.POST:
            notename = request.POST['note']
            userlist = request.POST.getlist('users')
            query = "select * from Notification"
            result = dbaccess.ExecuteQuery(query)
            flag = 0
            if result.get("count") > 0:
                cur = result.get("output")
                for line in cur:
                    if line[1] == notename:
                        messages.error(request, 'Name is duplicated!!!', extra_tags='danger')
                        flag = 1
            if flag == 0:
                query = "select * from BirdViewUsers"
                result = dbaccess.ExecuteQuery(query)
                ids = ""
                if result.get("count") > 0:
                    cur = result.get("output")
                    for line in cur:
                        if line[3] in userlist:
                            ids = ids+str(line[0])+ ","
                today = str(date.today())
                query = "insert into Notification (Name, CreatedDate, UserList) values ('"+notename+"', '"+today+"', '"+ids+"')"
                result = dbaccess.ExecuteQuery(query)
                messages.success(request, 'Notification is added successfully', extra_tags='success')

        query = "select * from BirdViewUsers"
        result = dbaccess.ExecuteQuery(query)
        dictresult = {}
        if result.get("count") > 0:
            cur = result.get("output")
            #dict of email ids
            for line in cur:
                dictresult[line[1]] = line[3]

        return render(request,"note_add.html", locals())

def notification_modify(request):
    if not request.user.is_authenticated:
        # messages.success(request, "This action requires to authenticate..")
        return redirect('/login')
    else:
        if request.method == "POST" and 'modify' in request.POST:
            notename = request.POST['notename']
            userlist = request.POST.getlist('users')
            query = "select * from BirdViewUsers"
            result = dbaccess.ExecuteQuery(query)
            ids = ""
            if result.get("count") > 0:
                cur = result.get("output")
                for line in cur:
                    if line[3] in userlist:
                        ids = ids + str(line[0]) + ","
            query = "update Notification set UserList='"+ids+"' where Name='"+notename+"' and ID>0"
            result = dbaccess.ExecuteQuery(query)
            messages.success(request, 'Notification is updated successfully', extra_tags='success')

        query = "select * from Notification"
        result = dbaccess.ExecuteQuery(query)
        notelist = {}
        if result.get("count") > 0:
            cur = result.get("output")
            for line in cur:
                notelist[line[0]] = line[1]
        query = "select * from BirdViewUsers"
        result = dbaccess.ExecuteQuery(query)
        userlist = {}
        if result.get("count") > 0:
            cur = result.get("output")
            # dict of email ids
            for line in cur:
                userlist[line[1]] = line[3]
        return render(request,"note_modify.html", locals())

def notification_remove(request):
    if not request.user.is_authenticated:
        # messages.success(request, "This action requires to authenticate..")
        return redirect('/login')
    else:
        if request.method == "POST" and 'remove1' in request.POST:
            notename = request.POST['notename']
            query = "delete from Notification where Name='"+notename+"' and ID>0"
            result = dbaccess.ExecuteQuery(query)
            messages.success(request, 'Notification is deleted successfully', extra_tags='success')

        query = "select * from Notification"
        result = dbaccess.ExecuteQuery(query)
        notelist = {}
        if result.get("count") > 0:
            cur = result.get("output")
            for line in cur:
                notelist[line[0]] = line[1]
        return render(request,"note_remove.html", locals())



def infra(request):
  return render(request,"infra.html")

def infra_storage(request):
  return render(request,"storage.html")

def infra_status(request):
  return render(request,"infrastatus.html")

def nightly(request):
      if request.method == "POST" and 'submitjob' in request.POST:
          return render(request, "nightly.html", locals())
      if request.method == "POST" and 'synch' in request.POST:
          if not request.user.is_authenticated:
             #messages.success(request, "This action requires to authenticate..")
             return redirect('/login')
          else:
             dict = dbaccess.UpdateAllTables()
             if dict.get("jobstatus") > 0:
                messages.success(request, str(dict.get("jobstatus"))+" rows updated successfully")
             if dict.get("datachaincombo") > 0:
                messages.success(request, str(dict.get("datachaincombo")) + " rows updated successfully")
      return render(request,"nightly.html")

def nightly_add(request):
      if not request.user.is_authenticated:
        # messages.success(request, "This action requires to authenticate..")
          return redirect('/login')
      else:
          return render(request,"nightly_add.html")

def nightly_status(request):
      dictionaryResult = nightly_process.fetchPrecisionTable()
      dict = dictionaryResult.get("dictionary")
      parameters = dict

      if request.method == "POST" and 'graph' in request.POST:
              #print(request.POST)
              datasetid = request.POST['datasetid']
              paraid1 = request.POST['para']
              if paraid1.find('Choose the Parameter')>=0:
                  messages.error(request, 'Need to select the paramter!!!', extra_tags='danger')
              else:
                  time1 = request.POST['starttime']
                  time2 = request.POST['endtime']
                  datasetinfo = nightly_process.fetchDatasetChainYear(datasetid)
                  datasetid1 = datasetinfo.get("dataset")
                  chainid1 = datasetinfo.get("chain")
                  yearid1 = datasetinfo.get("year")
                  newstarttime = str(datetime.strptime(time1, "%Y-%m-%d") - timedelta(7))
                  newendtime = str(datetime.strptime(time2, "%Y-%m-%d") + timedelta(7))
                  wtime = newstarttime.split(" ")[0] + " ~ " + newendtime.split(" ")[0]
                  result = nightly_process.fetchgraphdata(datasetid, paraid1, newstarttime, newendtime)
                  labels = []
                  datas = []
                  for value in result:
                      labels.append(value.split(" ")[0])
                      datas.append(result[value])
                  return render(request, "nightly_plot_graph2.html", locals())

      if request.method == "POST" and 'graph1' in request.POST:
              datasetid1 = request.POST['datasetid']
              paraid1 = request.POST['paraid']
              chainid1 = request.POST['chainid']
              yearid1 = request.POST['yearid']
              wtime = request.POST['wtime']
              timelist = wtime.split(" ~ ")
              comboid = nightly_process.getComboID(datasetid1, chainid1, yearid1)
              result = nightly_process.fetchgraphdata(comboid, paraid1, timelist[0], timelist[1])
              labels = []
              datas = []
              for value in result:
                  labels.append(value.split(" ")[0])
                  datas.append(result[value])
              return render(request, "nightly_plot_graph2.html", locals())

      ############ to show the details of ID on status page ################
      Combolist = dbaccess.ExecuteQuery("select * from DatasetChainCombo")
      combolistdict = Combolist.get("output")
      idlist = []
      dclist = []
      chainlist = []
      yearlist = []
      for line in combolistdict:
            idlist.append(line[0])
            dclist.append(line[1])
            chainlist.append(line[2])
            yearlist.append(line[3])


      weekeback = getWeekbackDate()
      query = "select * from DatasetResultChange where DayTime1>"+"'"+weekeback+"'"
      #print(query)
      # dictionaryResult = nightly_process.fetchPrecisionTable()
      # dict = dictionaryResult.get("dictionary")
      # print(dict)
      column_names = nightly_process.DescribeTable("DatasetResultChange")
      # print(column_names)
      result = dbaccess.ExecuteQuery(query)
      dictresult = CreateTableContent(result,idlist,dclist,yearlist)
      except_list = ["DatasetChainComboID", "DayTime1", "DayTime2","Dataset-year"]
      return render(request,"nightly_status.html", locals())

def CreateTableContent(result,idlist,dclist,yearlist):
    column_names = nightly_process.DescribeTable("DatasetResultChange")
    #print(column_names)
    column_names.insert(2,"Dataset-year")
    #print(column_names)
    dictresult = {}
    if result.get("count") > 0:
        cur = result.get("output")
        for line in cur:
            dict_array = {}
            index = 0
            dcid = 0
            #print(line)
            for val in line:
                if index==1:
                    dcid = val
                    #print("DCID="+str(dcid)+" Val="+str(val))
                if index==2:
                    point = idlist.index(dcid)
                    dsstr = dclist[point]
                    yrstr = yearlist[point]
                    totalstr = str(dsstr)+"-"+str(yrstr)
                    dict_array[column_names[2]] = totalstr
                    #print("Dataset-year="+totalstr)
                    index = index + 1
                if type(val) is datetime:
                       strd = ""
                       strd = strd + str(val.year) + "-" + str(val.month) + "-" + str(val.day)
                       dict_array[column_names[index]] = strd
                else:
                       dict_array[column_names[index]] = val

                index = index + 1
            #print(dict_array)
            dict_array.pop("ID")
            dict_array.pop("ChangeDescription")
            dictresult[line[0]] = dict_array
    return dictresult

def nightly_pre(request):
      dictionaryResult = nightly_process.fetchPrecisionTable()
      dict = dictionaryResult.get("dictionary")
      datasetid = dictionaryResult.get("dataset")
      # print(request.POST)
      if request.method == "POST" and 'update' in request.POST:
          if not request.user.is_authenticated:
              return redirect('/login')
          else:
              return render(request, "nightly_premod.html", locals())

      if request.method == "POST" and 'update1' in request.POST:
          parameter = request.POST['para']
          value = request.POST['val']
          result = nightly_process.UpdateParameter(parameter, value)
          if result.get("count") == 1:
              messages.success(request, 'Value is updated successfully', extra_tags='success')
          else:
              messages.error(request, 'Value is not updated!!!', extra_tags='danger')
          return render(request, "nightly_premod.html", locals())

      return render(request,"nightly_precision.html",locals())

def nightly_premod(request):
    if not request.user.is_authenticated:
        # messages.success(request, "This action requires to authenticate..")
        return redirect('/login')
    else:
        if request.method == "POST" and 'update'in request.POST:
              parameter = request.POST['para']
              value = request.POST['val']
              result = nightly_process.UpdateParameter(parameter,value)
              if result.get("count")==1:
                    messages.success(request, 'Value is updated successfully', extra_tags='success')
              else:
                    messages.error(request, 'Value is not updated!!!', extra_tags='danger')


        if request.method == "POST" and 'reval' in request.POST:
              changes = nightly_process.reevaluatechange()
              if changes > 0:
                  messages.success(request, str(changes)+" changes are updated", extra_tags='success')

        if request.method == "POST" and 'synch' in request.POST:
              changes = nightly_process.synchronise()
              if changes > 0:
                  messages.success(request, str(changes)+" changes are updated", extra_tags='success')

        resultdict = nightly_process.fetchPrecisionTable()
        dict = resultdict.get("dictionary")
        datasetid = resultdict.get("dataset")
        return render(request,"nightly_premod.html",locals())

def nightly_plot(request):
      resultdict = nightly_process.fetchPrecisionTable()
      parameters = resultdict.get("dictionary")
      datasetid = resultdict.get("dataset")

      if request.method == "POST" and 'search' in request.POST:
              datasetid1 = request.POST['datasetid']
              chainid1 = request.POST['chainid']
              yearid1 = request.POST['yearid']
              starttime = request.POST['starttime']
              endtime = request.POST['endtime']
              para = request.POST['paraid']

              if datasetid1.find("Choose the ")>=0 or chainid1.find("Choose the ")>=0 or yearid1.find("Choose the ")>=0 or para.find("Choose the ")>=0 \
                 or len(starttime)==0 or len(endtime)==0:
                  messages.error(request, 'Choose all options correctly!!!', extra_tags='danger')
              else:
                  comboid = nightly_process.getComboID(datasetid1,chainid1,yearid1)
                  #result = nightly_process.gatherData(comboid,starttime,endtime,para)
                  query = "select * from DatasetResultChange where DatasetChainComboID="+str(comboid)+" and DayTime1>'" + starttime + "' and DayTime2<'"+endtime+"'"
                  #print(query)
                  dictionaryResult = nightly_process.fetchPrecisionTable()

                  dict = dictionaryResult.get("dictionary")
                  result = dbaccess.ExecuteQuery(query)
                  dictresult = CreateTableContent(result)
                  except_list = ["DatasetChainComboID", "DayTime1", "DayTime2"]
                  if result.get("count")==0:
                      messages.error(request, 'There is no violation of precision within this period!!!', extra_tags='danger')
                  return render(request, "nightly_plot_details.html", locals())

      if request.method == "POST" and 'graph' in request.POST:
              #print(request.POST)
              datasetid1 = request.POST['dataset']
              paraid1 = request.POST['para']
              time1 = request.POST['time1']
              time2 = request.POST['time2']
              chainid1 = request.POST['chain']
              yearid1 = request.POST['year']
              #print(datasetid1+"--"+paraid1+"--"+time1+"--"+time2)
              comboid = nightly_process.getComboID(datasetid1, chainid1, yearid1)

              newstarttime = str(datetime.strptime(time1,"%Y-%m-%d")-timedelta(7))
              newendtime = str(datetime.strptime(time2,"%Y-%m-%d")+timedelta(7))
              wtime = newstarttime.split(" ")[0] + " ~ " + newendtime.split(" ")[0]
              # print(wtime)
              result = nightly_process.fetchgraphdata(comboid,paraid1,newstarttime,newendtime)
              #print(result)
              labels = []
              datas = []
              for value in result:
                  labels.append(value.split(" ")[0])
                  datas.append(result[value])
              #print(labels)
              #print(datas)
              return render(request, "nightly_plot_graph2.html", locals())

      if request.method == "POST" and 'graph1' in request.POST:
              datasetid1 = request.POST['datasetid']
              paraid1 = request.POST['paraid']
              chainid1 = request.POST['chainid']
              yearid1 = request.POST['yearid']
              wtime = request.POST['wtime']
              timelist = wtime.split(" ~ ")
              comboid = nightly_process.getComboID(datasetid1, chainid1, yearid1)
              result = nightly_process.fetchgraphdata(comboid, paraid1, timelist[0], timelist[1])
              labels = []
              datas = []
              for value in result:
                  labels.append(value.split(" ")[0])
                  datas.append(result[value])
              return render(request, "nightly_plot_graph2.html", locals())


      datasets = nightly_process.fetchDatasetlist()
      #chains = nightly_process.fetchChainlist()
      #years = nightly_process.fetchYearlist()
      combodictnew = nightly_process.fetchDatasetChainCombo()
      combodict = combodictnew.get("dict")
      yearlist = combodictnew.get("yearlist")

      return render(request,"nightly_plot.html",locals())



def nightly_compare(request):
        datasets = nightly_process.fetchDatasetlist()
        # print(datasets.values())

        resultdict = nightly_process.fetchPrecisionTable()
        combodictnew = nightly_process.fetchDatasetChainCombo()
        combodict = combodictnew.get("dict")
        yearlist = combodictnew.get("yearlist")
        parameters = resultdict.get("dictionary")
        datasetid = resultdict.get("dataset")

        if request.method == "POST" and 'graph1' in request.POST:
                #print(request.POST)
                datasets = request.POST['datasets']
                chainid = request.POST['chain']
                wtime = request.POST['wtime']
                year = request.POST['year']
                para = request.POST['para']

                datalist = datasets.split(" , ")
                timelist = wtime.split(" ~ ")
                datasetid1 = datalist[0]
                datasetid2 = datalist[1]
                comboid1 = nightly_process.getComboID(datalist[0], chainid, year)
                comboid2 = nightly_process.getComboID(datalist[1], chainid, year)

                result1 = nightly_process.fetchgraphdata(comboid1, para, timelist[0], timelist[1])

                result2 = nightly_process.fetchgraphdata(comboid2, para, timelist[0], timelist[1])

                dict = getGraphData(result1, result2)
                # print(dict)
                labels1 = dict.get("labels")
                length = len(labels1)
                datas1 = dict.get("datas1")
                datas2 = dict.get("datas2")
                yearid1 = year
                chainid1 = chainid
                paraid1 = para
                return render(request, "nightly_plot_graph.html", locals())

        if request.method == "POST" and 'graph' in request.POST:
                #print(request.POST)
                datasetid1 = request.POST['datasetid1']
                chainid1 = request.POST['chainid1']
                yearid1 = request.POST['yearid1']


                datasetid2 = request.POST['datasetid2']
                chainid2 = request.POST['chainid2']
                yearid2 = request.POST['yearid2']


                time1 = request.POST['starttime']
                time2 = request.POST['endtime']
                paraid1 = request.POST['paraid']

                if datasetid1.find("Choose the ") >= 0 or chainid1.find("Choose the ") >= 0 or yearid1.find("Choose the ") >= 0 or paraid1.find("Choose the ") >= 0 \
                        or len(time1) == 0 or len(time2) == 0 or \
                   datasetid2.find("Choose the ") >= 0 or chainid2.find("Choose the ") >= 0 or yearid2.find("Choose the ") >= 0:
                    messages.error(request, 'Choose all options correctly!!!', extra_tags='danger')
                else:
                    comboid1 = nightly_process.getComboID(datasetid1, chainid1, yearid1)
                    result1 = nightly_process.fetchgraphdata(comboid1, paraid1, time1, time2)
                    comboid2 = nightly_process.getComboID(datasetid2, chainid2, yearid2)
                    result2 = nightly_process.fetchgraphdata(comboid2, paraid1, time1, time2)

                    dict = getGraphData(result1,result2)
                    # print(dict)
                    labels1 = dict.get("labels")
                    length = len(labels1)
                    datas1 = dict.get("datas1")
                    datas2 = dict.get("datas2")
                    datasets = datasetid1+" , "+datasetid2
                    wtime = time1+" ~ "+time2
                    return render(request, "nightly_plot_graph.html", locals())


        return render(request, "nightly_compare.html", locals())

def getGraphData(result1, result2):
    labels1 = list(result1.keys())
    result11 = {}
    # print(len(labels1))
    for label in labels1:
        day = label.split(" ")[0]
        result11[day] = result1[label]
        labels1[labels1.index(label)] = day

    labels2 = list(result2.keys())
    result22 = {}
    # print(len(labels2))
    for label in labels2:
        day = label.split(" ")[0]
        result22[day] = result2[label]
        labels2[labels2.index(label)] = label.split(" ")[0]
    datas1 = []
    datas2 = []
    labels = list(dict.fromkeys(labels1 + labels2))
    labels.sort()
    # print(len(labels))
    for label in labels:
        if label in labels1:
            datas1.append(result11[label])
        else:
            datas1.append(0)
        if label in labels2:
            datas2.append(result22[label])
        else:
            datas2.append(0)

    dict1 ={}
    dict1["labels"]=labels
    dict1["datas1"]=datas1
    dict1["datas2"]=datas2
    return dict1;

def getWeekbackDate():
        weekback = str(date.today() - timedelta(7))
        #print(weekback)
        return weekback

def nightly_library(request):
    resultdict = nightly_process.fetchPrecisionTable()
    parameters = resultdict.get("dictionary")

    if request.method == "POST" and 'graph' in request.POST:
        datasetid = request.POST['datasetid']
        chainid = request.POST['chainid']
        yearid = request.POST['yearid']
        paraid = request.POST['paraid']
        if datasetid.find("Choose the ") >= 0 or chainid.find("Choose the ") >= 0 or yearid.find("Choose the ") >= 0 or paraid.find("Choose the ") >= 0:
            messages.error(request, 'Choose all options correctly!!!', extra_tags='danger')
        else:
        #comboid = nightly_process.getComboID(datasetid, chainid, yearid)
            result = nightly_process.fetch_Library_data(datasetid, paraid, chainid)
            if bool(result):
               labels = []
               datas = []
               for value in result:
                   labels.append(result[value][0])
                   datas.append(result[value][1])

               return render(request, "nightly_library_graph.html", locals())
            else:
               messages.error(request, 'Choosen dataset does not have result!!!', extra_tags='danger')


    if request.method == "POST" and 'graph1' in request.POST:
        # print(request.POST)
        datasetid = request.POST['datasetid']
        chainid = request.POST['chainid']
        yearid = request.POST['yearid']
        paraid = request.POST['paraid']

        result = nightly_process.fetch_Library_data(datasetid, paraid, chainid)
        if bool(result):
            labels = []
            datas = []
            for value in result:
                labels.append(result[value][0])
                datas.append(result[value][1])

            # print(labels)
            # print(datas)
            return render(request, "nightly_library_graph.html", locals())
        else:
            messages.error(request, 'Choosen dataset does not have result!!!', extra_tags='danger')

    #datasets = nightly_process.fetchDatasetlist()
    #datasetid = resultdict.get("dataset")
    #combodict = nightly_process.fetchDatasetChainCombo()
    selectionlist = nightly_process.fetch_Library_dataset()
    yearlist = selectionlist.get("years")
    datasetlist = selectionlist.get("rows")
    #print(combodict)
    return render(request, "nightly_library.html", locals())


# def getYesterdayDate():
#       yesterday = str(date.today()-timedelta(1))
#       return yesterday



# def getChartData(request):
#     renderer_classes = [TemplateHTMLRenderer]
#     template_name = 'nightly_plot_graph.html'
#     labels_list = ["Red", "Blue", "Yellow", "Green", "Purple", "Orange"]
#     data_list = [12, 19, 3, 5, 2, 3]
#     defaultdata = {
#         "labels": labels_list,
#         "datas": data_list
#     }
#     #return JsonResponse(data)
#     return render(request, "nightly_plot_graph.html", locals())

