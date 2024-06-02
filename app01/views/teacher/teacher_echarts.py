from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render

from app01.models import Student, Class, provinces


# 班级人数详情图
def students_echarts(request):
    teacher_info = request.session['info']
    context = {
        'teacher_info': teacher_info,
    }
    return render(request, 'teacher/teacher_echarts.html', context)


# 传入图表所需要的参数 ====== 当前老师所管理的班级名称
def teacher_manage_classes(request):
    teacher_info = request.session['info']
    classes = Class.objects.filter(teacher=teacher_info.get('id')).values('name', 'id')
    class_data = {}
    for class_info in classes:
        student_count = Student.objects.filter(classs_id=class_info['id']).count()
        class_data[class_info['name']] = student_count
    result = {
        'status': True,
        'classes': class_data
    }
    return JsonResponse(result)


def teacher_classes_status(request):
    teacher_info = request.session['info']
    # 老师管理的所有班级
    classes = Class.objects.filter(teacher=teacher_info.get('id'))
    class_data = {}
    # 遍历所有班级
    for class_obj in classes:
        # 获取到当前班级下的所有人数
        students = class_obj.students.all()
        employed = students.filter(status=0).count()
        enrolled = students.filter(status=1).count()
        class_data[class_obj.name] = {
            'total': students.count(),
            'employed': employed,
            'enrolled': enrolled
        }
    result = {
        'status': True,
        'classes': class_data
    }
    return JsonResponse(result)


def teacher_china(request):
    # 获取当前登录教师的信息
    teacher_info = request.session['info']
    context = {
        'teacher_info': teacher_info
    }
    return render(request, 'teacher/teacher_china.html', context)


def teacher_get_china_data(request):
    # 获取当前登录教师的信息
    teacher_info = request.session['info']
    # 获取当前教师管理的所有班级
    classes = Class.objects.filter(teacher=teacher_info.get('id'))
    # 统计每个省份的学生数量和学生姓名
    province_stats = Student.objects.filter(classs__in=classes) \
        .values('province') \
        .annotate(count=Count('province'))

    # 获取每个省份的学生姓名和班级信息
    student_info_by_province = {}
    for student in Student.objects.filter(classs__in=classes).values('province', 'phone', 'username', 'classs__name',
                                                                     'status'):
        province = student['province']
        if province not in student_info_by_province:
            student_info_by_province[province] = {'students': [], 'classes': []}
        # 添加学生姓名
        student_info_by_province[province]['students'].append({
            'username': student['username'],
            'phone': student['phone'],
            'class': student['classs__name'],
            'status': student['status'],
        })
        # 添加学生班级

    # 省份编码到名称的映射
    provinces_dict = {p[0]: p[1] for p in provinces}

    # 结果列表
    result = []
    for stat in province_stats:
        province_code = stat['province']
        province_name = provinces_dict[province_code]
        count = stat['count']
        # 获取该省份的学生姓名和班级信息
        students = student_info_by_province.get(province_code, {'students': [], 'classes': []})

        # 将省份名称、学生数量、学生姓名列表和学生班级信息添加到结果中
        result.append({
            'name': province_name,
            'value': count,
            'student': students['students'],
        })

    # 现在 result 包含了每个省份的学生姓名和班级信息
    print(result)
    return JsonResponse(result, safe=False)
