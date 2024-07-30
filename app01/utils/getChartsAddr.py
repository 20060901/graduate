# public数据
from django.db.models import Avg, Count, Min, Max, Sum

from .getPublicData import *
import time
import json


def AddrSelect():
    selset = getAllJobs().values('address').annotate(c=Count("address"))
    dist = {}
    for sel in selset:
        dist[sel['address']] = sel['c']
    # 倒序
    arrlt = sorted(dist.items(), key=lambda d: d[1], reverse=True)[:8]
    # 选项
    selarr = []
    for k, v in arrlt:
        selarr.append(k)
    return selarr


def salaryFenbu(address):
    jobs = getAllJobs().filter(address=address)
    arr = {}
    arr['0-10k'] = 0
    arr['10-20k'] = 0
    arr['20-30k'] = 0
    arr['30-40k'] = 0
    arr['40k及以上'] = 0
    for job in jobs:
        if job.pratice == 0:
            salarymax = eval(job.salary)[1]
            if salarymax >= 0 and salarymax <= 10000:
                arr['0-10k'] += 1
            elif salarymax > 10000 and salarymax <= 20000:
                arr['10-20k'] += 1
            elif salarymax > 20000 and salarymax <= 30000:
                arr['20-30k'] += 1
            elif salarymax > 30000 and salarymax <= 40000:
                arr['30-40k'] += 1
            elif salarymax > 40000:
                arr['40k及以上'] += 1
    name = []
    value = []
    for k, v in arr.items():
        name.append(k)
        value.append(v)
    return name, value


def CPeopleFenbu(address):
    jobs = getAllJobs().filter(address=address)
    arr = {}
    arr['0-20人'] = 0
    arr['20-99人'] = 0
    arr['100-499人'] = 0
    arr['500-999人'] = 0
    arr['1000-9999人'] = 0
    arr['1万人以上'] = 0
    for job in jobs:
        cpeoplemax = eval(job.companyPeople)[1]
        if cpeoplemax >= 0 and cpeoplemax <= 20:
            arr['0-20人'] += 1
        elif cpeoplemax > 20 and cpeoplemax < 100:
            arr['20-99人'] += 1
        elif cpeoplemax >= 100 and cpeoplemax < 500:
            arr['100-499人'] += 1
        elif cpeoplemax >= 500 and cpeoplemax < 1000:
            arr['500-999人'] += 1
        elif cpeoplemax >= 1000 and cpeoplemax < 10000:
            arr['1000-9999人'] += 1
        elif cpeoplemax >= 10000:
            arr['1万人以上'] += 1
    result = []
    for k, v in arr.items():
        result.append({
            'name': k,
            'value': v
        })
    return result


def eduFenbu(address):
    jobs = getAllJobs().filter(address=address)
    eduset = jobs.values('educational').distinct().annotate(c=Count("educational"))
    dist = {}
    for edu in eduset:
        dist[edu['educational']] = edu['c']
    # 倒序
    arrlt = sorted(dist.items(), key=lambda d: d[1], reverse=True)
    eduleg = []
    edudata = []
    for k, v in arrlt:
        eduleg.append(k)
        edudata.append({
            'name': k,
            'value': v
        })
    return eduleg, edudata


def distFenbu(address):
    # 过滤
    jobs = getAllJobs().filter(address=address)
    # 获取字段 去重 分类 计数
    distset = jobs.values('dist').distinct().annotate(c=Count("dist"))
    dist = {}
    for d in distset:
        dist[d['dist']] = d['c']
    # 倒序
    arrlt = sorted(dist.items(), key=lambda d: d[1], reverse=True)
    distresult = []
    for k, v in arrlt:
        distresult.append({
            'name': k,
            'value': v
        })
    return distresult

# 词云
def getComFuli(address):
    if address != '':
        fuliset = getAllJobs().filter(address=address).values('companyTags')
    else:
        fuliset = getAllJobs().values('companyTags')
    text = ""
    for fulis in fuliset:
        if fulis['companyTags'] != '无':
            for fuli in eval(fulis['companyTags']):
                text += fuli+" "
    return text
