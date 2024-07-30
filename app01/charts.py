from django.http import JsonResponse

from .utils import getChartsSala, getChartsComp, getChartsStatus, getChartsAddr, wordcount


def xingzi_qk(request):
    # 提交查询
    if request.method == 'POST':
        edu = request.POST['edu']
        if edu == '不限':
            edu = ''
        exp = request.POST['exp']
        if exp == '不限':
            exp = ''
    else:
        edu = ''
        exp = ''
    # 薪资分布
    wktype, salname, saldist = getChartsSala.salaryFenbu(edu, exp)
    # 实习生薪资
    pradata = getChartsSala.salaryPra(edu)
    # 年底多薪
    salMonthData = getChartsSala.getSalMonth(edu)

    data={
        'wktype': wktype,
        'salname': salname,
        'saldist': saldist,
        'pradata': pradata,
        'salMonthData': salMonthData
    }
    response_data = {
        'code': 0,
        'msg': 'ok',
        'data': data
    }
    return JsonResponse(response_data)


def gongsi_qk(request):
    if request.method == 'POST':
        type = request.POST["typetitle"]
    else:
        type = '全部'
    # 企业融资
    statusredu = getChartsStatus.getStatus(type)
    # 公司个数
    cnName, cnValue = getChartsComp.getComCount(type)
    # 公司地址
    cadata, citydata = getChartsComp.getComAddr(type)
    # 公司人数
    cpname, cpdata = getChartsComp.getComPeo(type)

    data={
        'cnName':cnName,
        'cnValue':cnValue,
        'cadata':cadata,
        'citydata':citydata,
        'cpname':cpname,
        'cpdata':cpdata,
        'statusredu':statusredu
    }
    response_data = {
        'code': 0,
        'msg': 'ok',
        'data':data

    }
    return JsonResponse(response_data)


def jineng_qk(request):
    if request.method == 'POST':
        type = request.POST['type']
        if type == '全部':
            type = ''
    else:
        type = ''
    # 当前岗位数量

    # 技能标签
    wkaxis, wkdata, wktype = getChartsStatus.getWorkTags(type)
    # 岗位的学历与经验热力图
    eduleg = [ "学历不限","初中及以下", "中专/中技", "高中","大专","本科",  "硕士" , "博士"]
    expleg = [ "经验不限","在校/应届", "1年以内", "1-3年","3-5年",  "5-10年", "10年以上"]

    heatmap_data,max=getChartsStatus.get_Edu_Exp_heatmap_data(type)
    typenums=getChartsStatus.get_type_num(type)

    data={
         'wkaxis':wkaxis,
        'wkdata':wkdata,
        'typenums':typenums,
        'eduleg':eduleg,
        'expleg':expleg,
        'max':max,
        'heatmap_data':heatmap_data
    }
    response_data = {
        'code': 0,
        'msg': 'ok',
        'data': data

    }
    return JsonResponse(response_data)


def chengshi_qk(request):
    if request.method=='POST':
        address=request.POST['address']
    else:
        address='北京'
    addrsel = getChartsAddr.AddrSelect()
    # 薪资分布
    salname, salvalue = getChartsAddr.salaryFenbu(address)
    # 公司人数分布
    cpeoresult = getChartsAddr.CPeopleFenbu(address)
    # 学历分布
    eduleg, edudata = getChartsAddr.eduFenbu(address)
    # 行政区分布
    distdata = getChartsAddr.distFenbu(address)
    # 福利词云
    # 福利文本
    fulitext = getChartsAddr.getComFuli(address)
    # 福利词云图片
    fuliimg = wordcount.getImagesByAddTags(address, fulitext)
    data={
        'AddrSelect': {
            'addrsel': addrsel
        },
        'address': address,
        'salaryFenbu': {
            'salname': salname,
            'salvalue': salvalue
        },
        'cpeoresult': cpeoresult,
        'eduFenbu': {
            'eduleg': eduleg,
            'edudata': edudata
        },
        'distdata': distdata,
        'fuliimg': fuliimg
    }
    response_data = {
        'code': 0,
        'msg': 'ok',
         'data':data
    }
    return JsonResponse(response_data)
