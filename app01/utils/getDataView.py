from .getPublicData import *
from app01.models import JobInfo

def getAllJobInfos():
    # 获取招聘信息
    jobs = getAllJobs()
    for job in jobs:
        job.hrName=job.hrName.strip(job.hrWork)
        job.workTag=(eval(job.workTag))
        if job.workTag != '无':
            job.workTag = [i for i in job.workTag if i != '']
        if int(job.pratice) != 1:
            job.salary = '-'.join('%s'%int(i/1000) for i in eval(job.salary))+'K'
        else:
            job.salary = '-'.join('%s'%i for i in eval(job.salary)) + '元/天'

        if int(job.salaryMonth.replace('薪','')) != 0:
            job.salaryMonth = '·'+ job.salaryMonth
        else:
            job.salaryMonth = ''

        if job.companyTags != '无':
            job.companyTags= '，'.join('%s'%i for i in eval(job.companyTags) if i!='')
        else:
            job.companyTags=''

        if job.companyPeople[1]==10000:
            job.companyPeople = '10000人以上'
        else:
            job.companyPeople =('-'.join('%s'%i for i in eval(job.companyPeople)))+'人'

    return jobs






