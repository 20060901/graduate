from django.db.models import Count

from .getPublicData import *
import numpy as np
from collections import Counter

edu_x = {
    "学历不限": 0, "初中及以下": 1, "中专/中技": 2, "高中": 3, "大专": 4, "本科": 5, "硕士": 6, "博士": 7
}
exp_y = {
    "经验不限": 0, "在校/应届": 1, "1年以内": 2, "1-3年": 3, "3-5年": 4, "5-10年": 5, "10年以上": 6
}


def getWorkTags(type, limit=20):
    # 技术标签集
    if type != '':
        worktagset = getAllJobs().filter(type=type).values('workTag')
    else:
        worktagset = getAllJobs().values('workTag')
    # 工作类型集
    typeset = getAllJobs().values('type').distinct()
    # 工作类型数组
    wktype = []
    for type in typeset:
        wktype.append(type['type'])
    # 技术标签数组
    arr = []
    for wts in worktagset:
        for i in eval(wts['workTag']):
            if i != '':
                arr.append(i)

    data = np.array(arr)
    x = Counter(data)
    x = x.most_common()
    wkaxis = []
    wkdata = []
    for i in x[:limit]:
        wkaxis.append(i[0])
        wkdata.append(i[1])
    return wkaxis, wkdata, wktype


def getStatus(type):
    if type != '全部':
        typeset = getAllJobs().filter(type=type).values('companyStatus').distinct().annotate(c=Count("companyStatus"))
    else:
        typeset = getAllJobs().values('companyStatus').distinct().annotate(c=Count("companyStatus"))
    dist = {}
    for t in typeset:
        dist[t['companyStatus']] = t['c']
    # 倒序
    arrlt = sorted(dist.items(), key=lambda d: d[1], reverse=True)
    distresult = []
    for k, v in arrlt:
        distresult.append({
            'name': k,
            'value': v
        })
    return distresult


def get_Edu_Exp_heatmap_data(type):
    if type != '':
        data = getAllJobs().filter(type=type).values('educational', 'workExperience').annotate(count=Count('*'))
    else:
        data = getAllJobs().values('educational', 'workExperience').distinct().annotate(count=Count("*"))
    heatmap_data = []
    max = 0
    for d in data:
        try:
            item = [
                exp_y[d['workExperience']]
                , edu_x[d['educational']]
                , d['count']
            ]
            if d['count'] > max:
                max = d['count']
        except:
            continue
        heatmap_data.append(item)
    max = round(max / 10) * 10
    return heatmap_data, max

def get_type_num(type):
    if type != '':
        data = getAllJobs().filter(type=type).count()
    else:
        data = getAllJobs().count()

    item={'typename':type,'count':data}
    return item