from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render

from app01.models import Student, Class, provinces


def student_china(request):
    # 获取当前登录学生的信息
    stu_info = request.session['info']
    # 把已读或者未读重新加入到session中
    stu_info['is_read'] = Student.objects.get(id=stu_info['id']).is_read

    context = {
        'stu_info': stu_info,
    }
    return render(request, 'student/student_china.html', context)


def student_get_china_data(request):
    stu_info = request.session['info']
    # 获取当前学生管理的所有班级
    classes = Class.objects.filter(id=stu_info.get('class'))
    # 统计所有学生的意向省份分布
    province_stats = Student.objects.filter(classs__in=classes) \
        .values('province') \
        .annotate(count=Count('province'))
    student_details = {}
    for student in Student.objects.filter(classs__in=classes).values('username', 'student_no', 'phone', 'status',
                                                                     'province'):
        province = student['province']
        # 初始化省份对应的学生信息列表
        if province not in student_details:
            student_details[province] = []
        # 将学生信息添加到对应省份的列表中
        student_details[province].append({
            'username': student['username'],
            'student_no': student['student_no'],
            'phone': student['phone'],
            'status': student['status'],
            'province': student['province']
        })

    result = [
        {
            'name': provinces[p['province']][1],
            'value': p['count'],
            'students': student_details.get(p['province'], [])  # 该省份的学生详细信息列表
        }
        for p in province_stats
    ]

    all_provinces = [
        "北京市",
        "天津市",
        "河北省",
        "山西省",
        "内蒙古自治区",
        "辽宁省",
        "吉林省",
        "黑龙江省",
        "上海市",
        "江苏省",
        "浙江省",
        "安徽省",
        "福建省",
        "江西省",
        "山东省",
        "河南省",
        "湖北省",
        "湖南省",
        "广东省",
        "广西壮族自治区",
        "海南省",
        "重庆市",
        "四川省",
        "贵州省",
        "云南省",
        "西藏自治区",
        "陕西省",
        "甘肃省",
        "青海省",
        "宁夏回族自治区",
        "新疆维吾尔自治区",
        "台湾省",
        "香港特别行政区",
        "澳门特别行政区"
    ]
    # 创建一个包含所有省份名称的集合，用于检查省份是否已在结果中
    result_provinces = {item['name'] for item in result}
    for province in all_provinces:
        if province not in result_provinces:
            # 如果省份不在结果中，添加一个带有默认值的新字典
            result.append({
                'name': province,
                'value': 0,
                'student': []
            })
    print(result)
    return JsonResponse(result, safe=False)
