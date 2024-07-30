

from django.db.models import Avg,Count,Min,Max,Sum

from .getPublicData import *
import time
import json
def getTypeSet():
    # 工作类型集
    typeset = getAllJobs().values('type').distinct()
    # 工作类型数组
    wktype = []
    for type in typeset:
        wktype.append(type['type'])
    return wktype



def getComCount(type):

    if type == '全部' :
        jobs = getAllJobs()
    else:
        jobs=getAllJobs().filter(type=type)
    cnset=jobs.values('companyNature').distinct().annotate(c=Count('companyNature'))[:25]
    dist={}
    for cn in cnset:
       dist[cn['companyNature']]=cn['c']
    sorted_dict=dict(sorted(dist.items(),key=lambda x:x[1],reverse=False))
    cnName=[]
    cnValue=[]
    for k,v in sorted_dict.items():
        cnName.append(k)
        cnValue.append(v)
    return cnName[-10:],cnValue[-10:]



def getComAddr(type):
    if type == '全部':
        jobs = getAllJobs()
    else:
        jobs = getAllJobs().filter(type=type)
    caset=jobs.values('address').distinct().annotate(c=Count('address'))
    cadata=[]
    citydata=[]
    for ca in caset:
        dist = {}
        dist['name']=ca['address']
        dist['value']=ca['c']
        citydata.append(ca['address'])
        cadata.append(dist)
    return cadata,citydata

def getComPeo(type):
    if type == '全部':
        jobs = getAllJobs()
    else:
        jobs = getAllJobs().filter(type=type)
    cpset=jobs.values('companyPeople').distinct().annotate(c=Count('companyPeople'))
    cpname=['20人以下','100人以下','500人以下','1000人以下','1万人以下','1万人以上']
    cpdata=[]
    for cp in cpset:
        dist={}
        cpeoplemax=eval(cp['companyPeople'])[1]
        if cpeoplemax >= 0 and cpeoplemax <= 20:
            dist['name']='20人以下'
            dist['value']=cp['c']
        elif cpeoplemax > 20 and cpeoplemax < 100:
            dist['name'] = '100人以下'
            dist['value'] = cp['c']
        elif cpeoplemax >= 100 and cpeoplemax < 500:
            dist['name'] = '500人以下'
            dist['value'] = cp['c']
        elif cpeoplemax >= 500 and cpeoplemax < 1000:
            dist['name'] = '1000人以下'
            dist['value'] = cp['c']
        elif cpeoplemax >= 1000 and cpeoplemax < 10000:
            dist['name'] = '1万人以下'
            dist['value'] = cp['c']
        elif cpeoplemax >=10000:
            dist['name'] = '1万人以上'
            dist['value'] = cp['c']
        cpdata.append(dist)

    return cpname,cpdata