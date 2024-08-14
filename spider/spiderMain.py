from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import csv,json
import os,time
import django,random
import pandas as pd
os.environ.setdefault('DJANGO_SETTINGS_MODULE','Graduate.settings')
django.setup()
from app01.models import JobInfo
from selenium import webdriver




class spider(object):
    # 构造
    def __init__(self,type,page):
        # 岗位关键字
        self.type = type
        # 页面数 1
        self.page = page
        # 爬虫地址
        # query 搜索关键字
        # page 页数
        # 全国
        self.spiderUrl = 'https://www.zhipin.com/web/geek/job?query=%s&city=100010000&page=%s'


    # 打开浏览器

    # 爬取页面
    def main(self,page):
        # 爬取指定page
        if self.page > page:return
        brower = webdriver.Edge()
        # 提示正在爬取
        print("正在获取的页面路径：" + self.spiderUrl % (self.type,self.page)) # %s % 格式化
        # 输入网址
        brower.get(self.spiderUrl % (self.type,self.page)) # get网址
        # 等待20秒
        time.sleep(10)
        # 获取网站招聘列表
        job_list = brower.find_elements(by=By.XPATH,value='//ul[@class="job-list-box"]/li') # find 30个li
        # 招聘列表转索引序列
        for index,job in enumerate(job_list):
            try:
                # 用于添加爬取的招聘数据
                jobData = []
                # 提示
                print("正在爬取第%d条数据" % (index + 1))
                # self.status_message = "正在爬取第%d条数据" % (index + 1)
                #岗位名字   contains(@class,"job-title") class包含job-title
                title = job.find_element(by=By.XPATH,value='.//a[@class="job-card-left"]/div[contains(@class,"job-title")]/span[@class="job-name"]').text
                # 地址处理
                # 取出文字 地址分割
                addresses = job.find_element(by=By.XPATH,value='.//a[@class="job-card-left"]/div[contains(@class,"job-title")]/span[@class="job-area-wrapper"]/span').text.split('·')
                # 省份地址
                address = addresses[0]
                # 行政区
                if len(addresses) != 1:
                    # 长度不是1
                    dist = addresses[1]
                else:
                    # 长度是1
                    # 没有行政区
                    dist = ''
                #岗位
                type = self.type
                # 薪资旁边的几个标签
                tag_list = job.find_elements(by=By.XPATH,value='.//a[@class="job-card-left"]/div[contains(@class,"job-info")]/ul[@class="tag-list"]/li')
                # 标签处理
                if len(tag_list)==2:
                    # 非实习生  1-3年|本科
                    # 学历
                    educational = tag_list[1].text
                    # 工作经验
                    workExperience = tag_list[0].text
                else:
                    # 实习生标签 5天/周|3个月|学历不限
                    # 学历
                    educational = tag_list[2].text
                    # 工作经验 null
                    workExperience = tag_list[1].text

                # hr职位
                hrWork = job.find_element(by=By.XPATH,value='.//a[@class="job-card-left"]/div[contains(@class,"job-info")]/div[@class="info-public"]/em').text
                # hr名字
                hrName = job.find_element(by=By.XPATH,value='.//a[@class="job-card-left"]/div[contains(@class,"job-info")]/div[@class="info-public"]').text.strip(hrWork)

                # 工作标签 列表
                workTag = job.find_elements(by=By.XPATH,value='./div[contains(@class,"job-card-footer")]/ul[@class="tag-list"]/li')
                # 列表处理
                # 列表中的每一项进行处理
                # dumps python单引号 转成 json双引号 元素为字符串 存入数据库
                workTag = json.dumps(list(map(lambda x:x.text,workTag))) #中文会被转义 转json
                #实习生 0不是 1是
                pratice = 0
                #薪资
                salaries = job.find_element(by=By.XPATH,value='.//a[@class="job-card-left"]/div[contains(@class,"job-info")]/span[@class="salary"]').text
                if salaries.find('K') != -1: # 找不到返回 -1 不是实习
                    # 找到K ·分割成列表
                    salaries = salaries.split('·')# 10~15K ·13薪
                    if len(salaries) == 1:
                        # 列表长度1 无薪
                        # 去除K 分割-
                        # ['10','15']-[10,15]-[10000,15000]
                        salary = list(map(lambda x:int(x) * 1000,salaries[0].replace('K','').split('-')))
                        # 年底0薪
                        salaryMonth = "0薪"
                    else:
                        # 带薪
                        salary = list(map(lambda x: int(x) * 1000, salaries[0].replace('K', '').split('-')))
                        # 年底多薪
                        salaryMonth = salaries[1]
                else:
                    # 是实习
                    salary = list(map(lambda x: int(x), salaries.replace('元/天', '').split('-'))) #100-150
                    # 年底0薪
                    salaryMonth = "0薪"
                    # 是实习生
                    pratice=1

                # 公司名字
                companyTitle = job.find_element(by=By.XPATH,value='.//div[@class="job-card-right"]/div[@class="company-info"]/h3/a').text

                #公司头像
                # 获取img里的属性src
                companyAvatar = job.find_element(by=By.XPATH,value='.//div[@class="job-card-right"]/div[@class="company-logo"]/a/img').get_attribute("src")

                # 公司标签
                companyInfos = job.find_elements(by=By.XPATH,value='.//div[@class="job-card-right"]/div[@class="company-info"]/ul[@class="company-tag-list"]/li')
                if len(companyInfos) == 3:
                    #存在融资
                    # 公司性质
                    companyNature = companyInfos[0].text
                    # 公司状态
                    companyStatus = companyInfos[1].text
                    # 公司人数
                    companyPeople = companyInfos[2].text
                    # 人数处理
                    if companyPeople != '10000人以上':
                        # 100-499人
                        companyPeople = list(map(lambda x: int(x), companyInfos[2].text.replace('人', '').split('-')))
                    else:
                        # 10000人以上
                        companyPeople = [0,10000]
                else:
                    # 公司性质
                    companyNature = companyInfos[0].text
                    # 公司未融资状态
                    companyStatus = '未融资'
                    # 公司人数
                    companyPeople = companyInfos[1].text
                    # 人数处理
                    if companyPeople != '10000人以上':
                        companyPeople = list(map(lambda x: int(x), companyInfos[1].text.replace('人', '').split('-')))
                    else:
                        companyPeople = [0,10000]

                #公司福利标签
                # 取出文本
                companyTags = job.find_element(by=By.XPATH,value='./div[contains(@class,"job-card-footer")]/div[@class="info-desc"]').text
                if not companyTags:
                    # 没有福利
                    companyTags = '无'
                else:
                    # 有福利
                    # ['']-[""] 转JSON用于存数据库
                    companyTags = json.dumps(companyTags.split('，'))


                #详情页
                # 获取a的属性href
                detailUrl = job.find_element(by=By.XPATH,value='.//a[@class="job-card-left"]').get_attribute('href')

                #公司详情页
                companyUrl = job.find_element(by=By.XPATH,value='.//div[@class="job-card-right"]/div[@class="company-info"]/h3/a').get_attribute('href')
                # print(companyTitle,companyAvatar,companyNature,companyStatus,companyPeople,companyTags,detailUrl,companyUrl)
                # 每条招聘数据
                jobData.append(title)
                jobData.append(address)
                jobData.append(type)
                jobData.append(educational)
                jobData.append(workExperience)
                jobData.append(workTag)
                jobData.append(salary)
                jobData.append(salaryMonth)
                jobData.append(companyTags)
                jobData.append(hrWork)
                jobData.append(hrName)
                jobData.append(pratice)
                jobData.append(companyTitle)
                jobData.append(companyAvatar)
                jobData.append(companyNature)
                jobData.append(companyStatus)
                jobData.append(companyPeople)
                jobData.append(detailUrl)
                jobData.append(companyUrl)
                jobData.append(dist)
                # 每条招聘数据保存csv
                self.save_to_csv(jobData)

            except:
                pass
        # 下一页
        brower.close()
        self.page += 1
        # 执行爬取下一页
        self.main(page)

    def get_status_message(self):
        return self.status_message

    # 数据清洗
    def clean_csv(self):
        # 读取爬好的数据
        data = pd.read_csv('./jobtemp.csv')
        print("清理前总数据为%d" % data.shape[0])
        # 删除空值
        data.dropna(inplace=True)
        # 删除重复项
        data.drop_duplicates(['title','address','companyTitle'],inplace=True)
        # 年底多薪去除 薪
        # data['salaryMonth'] = data['salaryMonth'].map(lambda x: (x.replace('薪', '') if not isinstance(x,int) else x))
        data['salaryMonth'].map(lambda x: x.replace('薪', ''))
        print("清理后总数据为%d" % data.shape[0])
        return data.values

    def save_to_sql(self):
        # 1.数据清洗
        data = self.clean_csv()
        # 2.保存数据库
        for job in data:
            JobInfo.objects.get_or_create(
                title=job[0],
                address=job[1],
                type=job[2],
                educational=job[3],
                workExperience=job[4],
                workTag=job[5],
                salary=job[6],
                salaryMonth=job[7],
                companyTags=job[8],
                hrWork=job[9],
                hrName=job[10],
                pratice=job[11],
                companyTitle=job[12],
                companyAvatar=job[13],
                companyNature=job[14],
                companyStatus=job[15],
                companyPeople=job[16],
                detailUrl=job[17],
                companyUrl=job[18],
                dist=job[19]
            )

    # 保存csv
    def save_to_csv(self,rowData):
        # 每条招聘数据追加写入
        with open('jobtemp.csv','a',newline='',encoding='utf-8') as wf:
            # 写入的对象wf
            writer = csv.writer(wf)
            # 每条数据写入对象
            writer.writerow(rowData)

    # 初始新建
    def init(self):
        # 当前路径不存在jobtemp.csv文件
        if not os.path.exists('jobtemp.csv'):
            # 先写入标签
            with open('jobtemp.csv','a',newline='',encoding='utf-8') as wf:
                writer = csv.writer(wf)
                writer.writerow(["title","address","type","educational","workExperience",
                                 "workTag","salary","salaryMonth","companyTags","hrWork",
                                 "hrName","pratice","companyTitle","companyAvatar","companyNature",
                                 "companyStatus","companyPeople","detailUrl","companyUrl","dist"])

if __name__ == '__main__':
    # 搜索专业 默认全国 从1开始怕
    # 热门
    # 传媒 销售 服务业 运营 供应链 物流人力 财务 行政市场 金融 教育培训
    # 起始页
    spiderObj = spider('算法',1)
    # spiderObj = spider('传媒',1)
    # spiderObj = spider('python',1)
    # spiderObj = spider('供应链',1)
    spiderObj.init()
    # 爬几页
    spiderObj.main(2)
    # 保存数据库 里面有数据清洗
    spiderObj.save_to_sql()



