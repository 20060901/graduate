from app01.models import *
# 月份名称 索引为数字
monthList = ['1','2','3','4','5','6','7','8','9','10','11','12']
# 学历  索引为字符串
educations = {'博士':1,'硕士':2,'本科':3,'大专':4,'高中':5,'中专/中技':6,'初中及以下':7,'学历不限':8}

def getAllUsers():
    # User from models.py
    # 获取所有用户信息
    return Student.objects.all()

def getAllJobs():
    # JobInfo from models.py
    # 获取所有爬取的招聘信息
    return JobInfo.objects.all()

# def getAllHist():
#     return History.objects.all()
