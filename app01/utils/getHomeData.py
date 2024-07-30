# public数据
from .getPublicData import *
import time
import json

def getNowTime():
    # 秒数转换为本地时间
    timeFormat = time.localtime()
    # 年月日
    yer = timeFormat.tm_year
    mon = timeFormat.tm_mon
    day = timeFormat.tm_mday
    # 年月份日
    return yer,monthList[mon - 1],day

# getAllUsers from getPublicData.py
# 获取用户创建时间
def getUserCreateTime():
    # 获取所有用户信息
    users=getAllUsers()
    # 用于存入信息
    data={}
    result=[]
    for k,v in data.items():
        result.append({
            'name':k,
            'value':v
        })
    return result

def getUserTop():
    # 获取所有用户 list
    users = getAllUsers()
    users=list(map(lambda x:{'id':x.id,
                             'gender':x.gender,
                             'username':x.username,
                             'educational':x.educational,
                             'workExperience':x.workExperience,
                             'address':x.address,
                             'work':x.work,
                             'is_admin':x.is_admin,
                             'avatar':x.avatar.url,
                             'createTime':x.createTime,
                             },users))

    def sort_fn(item):

        # time.strptime 格式化时间字符
        return time.mktime(time.strptime(str(item['createTime']),"%Y-%m-%d"))
    # 用户按照创建时间倒序排序后
    # 取前六个
    users=list(sorted(users,key=sort_fn,reverse=True))
    return users

def getAllTags():
    # 数据总量 len
    jobs=JobInfo.objects.all()
    # 用户数量 len
    users=Student.objects.all()
    # 默认最高学历 8
    educationsTop='学历不限'
    # 默认最高薪资
    salaryTop = 0
    # 默认最高年底多薪
    salaryMonthTop = 0
    # 默认优势城市
    address = {}
    pratice = {}
    for job in jobs:
        # 学历高
        if educations[job.educational] < educations[educationsTop]:
            # 替换最高学历
            educationsTop = job.educational
        # 正常岗位
        if job.pratice == 0:
            # 从数据库取出的json
            # json字符串转py字典 网页使用
            salary = json.loads(job.salary)[1]
            if salaryTop < salary:
                # 替换最高薪资 [100,200]
                salaryTop = salary

        if int(job.salaryMonth.replace('薪','')) > salaryMonthTop:
            # 替换最高年底多薪 字符转整型
            salaryMonthTop = int(job.salaryMonth.replace('薪',''))
        # 处理城市
        if address.get(job.address,-1) == -1:
            address[job.address] = 1
        else:
            address[job.address] += 1
        if pratice.get(job.pratice,-1) == -1:
            pratice[job.pratice] = 1
        else:
            pratice[job.pratice] += 1


    # 城市按薪资倒序排序 前三个
    addressStr = sorted(address.items(),key=lambda x:x[1],reverse=True)[:3]
    # 默认优势城市
    addressTop = ''

    praticeMax = sorted(pratice.items(),key=lambda x:x[1],reverse=True)


    for index,item in enumerate(addressStr):
        if index == len(addressStr) - 1:
            addressTop += item[0]
        else:
            addressTop += item[0] + ','

    if praticeMax:  # 检查 praticeMax 是否为空
        try:
            praticeMax = praticeMax[0][0]
        except:
            praticeMax = praticeMax[0]
    else:
        praticeMax = None
    return len(jobs),len(users),educationsTop,salaryTop,addressTop,salaryMonthTop,praticeMax

def getAllJobs():
    # 获取招聘信息
    jobs = JobInfo.objects.all()

    for job in jobs:

        job.workTag='/'.join(eval(job.workTag))
        job.salary = (eval(job.salary))
        if int(job.pratice) != 1:
            job.salary=str(job.salary[1])+'/月'
            job.pratice = '普通岗位'
        else:
            job.salary = str(job.salary[1]) + '元/天'
            job.pratice = '实习岗位'
        if int(job.salaryMonth) == 0:
            job.salaryMonth = '无'
        else:
            job.salaryMonth = job.salaryMonth + '薪'
        if job.companyTags != '无':
            job.companyTags= '/'.join(eval(job.companyTags))
        if job.companyPeople[1]==10000:
            job.companyPeople = '10000人以上'
        else:
            job.companyPeople =('人-'.join('%s'%i for i in eval(job.companyPeople)))+'人'
    return jobs
