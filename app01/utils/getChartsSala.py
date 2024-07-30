# public数据
from django.db.models import Avg, Count, Min, Max, Sum

from .getPublicData import *
import time
import json


def eduSelect():
    eduset = getAllJobs().values('educational').distinct().annotate(c=Count("educational"))
    dist = {}
    for edu in eduset:
        dist[edu['educational']] = edu['c']
    # 倒序
    arrlt = sorted(dist.items(), key=lambda d: d[1], reverse=True)
    # 学历标签
    eduleg = []
    for k, v in arrlt:
        eduleg.append(k)
    return eduleg


def expSelect():
    jobs = getAllJobs().filter(pratice=0)
    expset = jobs.values('workExperience').distinct().annotate(c=Count("workExperience"))
    dist = {}
    for exp in expset:
        if exp['workExperience']!='在校/应届':
             dist[exp['workExperience']] = exp['c']
    arrlt = sorted(dist.items(), key=lambda d: d[1], reverse=True)
    # 经验标签
    expleg = []
    for k, v in arrlt:
        expleg.append(k)
    return expleg


#
def salaryFenbu(edu, exp):
    if edu != '' and exp != '':
        jobs = getAllJobs().filter(educational=edu, workExperience=exp)
    elif edu == '' and exp == '':
        jobs = getAllJobs()
    elif edu == '' and exp != '':
        jobs = getAllJobs().filter(workExperience=exp)
    else:
        jobs = getAllJobs().filter(educational=edu)
    # 类型分类 5种
    typeset = jobs.values('type').distinct()
    # 工作类型标签
    wktype = []
    # 薪资标签
    salarr = ['0-10k', '10-20k', '20-30k', '30-40k', '40k及以上']
    #
    dist = {}
    for type in typeset:
        arr = [0, 0, 0, 0, 0]
        wktype.append(type['type'])
        jobset = jobs.filter(type=type['type'])
        for job in jobset:
            if job.pratice == 0:
                salarymax = eval(job.salary)[1]
                if salarymax >= 0 and salarymax <= 10000:
                    arr[0] += 1
                elif salarymax > 10000 and salarymax <= 20000:
                    arr[1] += 1
                elif salarymax > 20000 and salarymax <= 30000:
                    arr[2] += 1
                elif salarymax > 30000 and salarymax <= 40000:
                    arr[3] += 1
                elif salarymax > 40000:
                    arr[4] += 1

        dist[type['type']] = arr

    return wktype,salarr,dist


def salaryPra(edu):
    typeset = getAllJobs().values('type').distinct()
    pradata = []

    for type in typeset:
        jobset = getAllJobs().filter(type=type['type'], pratice=1)
        dist = {}
        dist['name'] = type['type']
        sum = 0
        for job in jobset:
            # 薪资和
            sum += eval(job.salary)[1]
        salavg = sum // len(jobset)
        dist['value'] = salavg
        pradata.append(dist)
    return pradata


def getSalMonth(edu):
    if edu != '':
        jobs = getAllJobs().filter(educational=edu)
    elif edu == '':
        jobs = getAllJobs()

    salmonthdata = []

    smset = jobs.values('salaryMonth').distinct().annotate(c=Count('salaryMonth'))
    for s in smset:
        if int(s['salaryMonth'].replace('薪','')) != 0:
            dist = {}
            dist['name'] = s['salaryMonth']
            dist['value'] = s['c']
            salmonthdata.append(dist)

    return salmonthdata
