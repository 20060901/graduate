import os
from django import forms
from django.core.validators import RegexValidator
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from app01.utils.pagination_kaoyan import Pagination
from Graduate.settings import MEDIA_ROOT
from app01.models import *
from app01.utils.bootstrap import BootStrapModelForm
from app01.views.tools.tools import getNewName
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from app01.utils import getChartsSala, getChartsComp, getChartsTags
from app01.utils import getHomeData, wordcount



class StudentEditModelForm(BootStrapModelForm):
    phone = forms.CharField(
        label="手机号",
        validators=[RegexValidator(r'^1\d{10}$', '手机号格式错误！')]
    )

    class Meta:
        model = Student
        exclude = ['role', 'teacher', 'password']
        widgets = {
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
            'classs': forms.Select(attrs={'class': 'form-control select2', 'data-toggle': 'select2'}),
        }


def stu_index(request):
    # 从 session 中获取学生信息
    stu_info = request.session.get('info')  # 使用 get 方法以防 key 不存在
    # 查询当前登陆的学生信息
    queryset = Student.objects.filter(id=stu_info['id'])
    # 查询当前学生所在班级的其他同学
    classmates = Student.objects.filter(classs=queryset[0].classs)
    # 获取所有班级
    # 创建表单实例,并将当前学生信息传入
    form = StudentEditModelForm(instance=Student.objects.get(id=stu_info['id']))
    # 获取到当前学生的老师
    teacher_id = Class.objects.filter(id=stu_info['class']).values('teacher_id')[0]['teacher_id']
    # 获取该学生的老师所发布的通知，并且让通知按照时间最新进行倒序
    teacher_issues_notice = Notice.objects.filter(teacher_id=teacher_id).order_by('-created_at')

    # 判断当前老师是否有发布通知，如果没有，则不显示红点：
    if teacher_issues_notice.count() == 0:
        Student.objects.filter(id=stu_info['id']).update(is_read=1)

    # 将学生读取通知的状态存储
    is_read = Student.objects.filter(id=stu_info['id']).values('is_read')[0]['is_read']
    stu_info['is_read'] = is_read
    context = {
        'stu_info': stu_info,
        'queryset': queryset,
        'form': form,
        'classmates': classmates,
        'notices': teacher_issues_notice,
    }

    if request.method == 'POST':
        # 更新学生信息
        student = Student.objects.get(id=stu_info['id'])
        phone = request.POST.get('phone')
        if phone != student.phone:
            # 手机号码被修改,检查是否已被注册
            if Teacher.objects.filter(phone=phone).exists() or Student.objects.filter(phone=phone).exists():
                # 手机号码已被注册
                messages.warning(request, '该手机号已被注册！')
                return redirect('/student/index/')
        student.username = request.POST.get('username')
        # 对密码进行加密
        student.phone = request.POST.get('phone')
        student.status = request.POST.get('status')
        student.province = request.POST.get('province')
        if 'pic' in request.FILES:
            pic = request.FILES['pic']
            new_name = getNewName('avatar')
            save_path = os.path.join(MEDIA_ROOT, "app1", new_name)
            # 确保目录存在
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, 'wb') as f:
                for content in pic.chunks():
                    f.write(content)
            student.avatar = ('app1/%s' % new_name)
        else:
            # 如果没有上传图片,则使用默认值或保留原有值
            student.avatar = student.avatar
        student.save()
        stu_info['username'] = student.username
        # 将加密后的密码保存到session
        stu_info['phone'] = student.phone
        stu_info['avatar'] = student.avatar.url
        stu_info['status'] = student.status
        stu_info['province'] = student.province
        request.session['info'] = stu_info
        return redirect('/student/index/')
    return render(request, 'student/student_index.html', context)


# 学生端修改密码
def student_edit_password(request):
    stu_info = request.session.get('info')  # 获取当前学生信息
    password = request.POST.get('password')
    repassword = request.POST.get('repassword')
    if password == repassword:
        if (password == '') or (repassword == ''):
            return JsonResponse({'status': False, 'error': '密码不能为空'})
        else:
            Student.objects.filter(id=stu_info['id']).update(password=make_password(repassword))
            return JsonResponse({'status': True})
    else:
        return JsonResponse({'status': False, 'error': '两次输入的密码不一致'})


# 清除小红点方法
def student_clear_notice(request):
    stu_info = request.session.get('info')
    Student.objects.filter(id=stu_info['id']).update(is_read=1)
    stu_info['is_read'] = 1
    return JsonResponse({'status': True})


# 显示所有通知
def student_notice(request):
    stu_info = request.session.get('info')
    teacher_id = Class.objects.filter(id=stu_info['class']).values('teacher_id')[0]['teacher_id']
    laoshi_info = Teacher.objects.filter(id=teacher_id)
    teacher_issues_notice = Notice.objects.filter(teacher_id=teacher_id).order_by('-created_at')
    context = {
        "stu_info": stu_info,
        'laoshi_info': laoshi_info,
        'notices': teacher_issues_notice
    }
    return render(request, 'student/student_notice.html', context)


# 当点击通知时，显示更为详细的通知页面
def student_get_notice(request):
    sid = request.GET.get('sid')
    notice_data = Notice.objects.filter(id=sid).values('title', 'content', 'created_at')[0]
    notice_data['created_at'] = notice_data['created_at'].strftime('%Y-%m-%d %H:%M:%S')
    # print(notice_data)
    context = {
        'status': True,
        'data': notice_data
    }
    return JsonResponse(context)

# 求职信息
def xinzi(request):
    stu_info = request.session.get('info')
    eduleg = getChartsSala.eduSelect()
    expleg = getChartsSala.expSelect()
    context = {
        "stu_info": stu_info,
        'eduleg': eduleg,
        'expleg': expleg,
    }
    return render(request, 'student/job_xinzi.html', context)

def dataTable(request):
    stu_info = request.session.get('info')
    context = {
        "stu_info": stu_info,
    }
    return render(request, "student/job.html",context)



def dataView(request):
    stu_info = request.session.get('info')
    context = {
        "stu_info": stu_info,
    }
    return render(request, 'student/data_view.html', context)


def chartsSkill(request):
    stu_info = request.session.get('info')
    wktype = getChartsComp.getTypeSet()
    context = {
        "stu_info": stu_info,
        'type': type,
        'wktype': wktype,
    }
    return render(request, 'student/charts_skill.html', context)


def chartsTags(request):
    stu_info = request.session.get('info')
    # 公司福利
    tagtext=getChartsTags.getAllTags()
    # 公司性质
    naturetext=getChartsTags.getAllNature()
    # 福利词云
    tagimg= wordcount.getImageByTags(tagtext)
    # 性质词云
    natureimg= wordcount.getImageByNature(naturetext)
    return render(request, 'student/charts_tags.html', {
         "stu_info": stu_info,
        'wordcount':{
            'tagimg':tagimg,
            'natureimg':natureimg
        }
    })


def chartsAddr(request):
    stu_info = request.session.get('info')
    if request.method=='POST':
        address=request.POST['address']

    else:
        address='北京'
    #选择框
    return render(request, 'student/charts-address.html', {
        "stu_info": stu_info,
    })


def chartsCompany(request):
    stu_info = request.session.get('info')
    jobsLen, usersLen, educationsTop, salaryTop, addressTop, salaryMonthTop, praticeMax = getHomeData.getAllTags()
    print(jobsLen, usersLen, educationsTop, salaryTop, addressTop, salaryMonthTop, praticeMax)
    wktype=getChartsComp.getTypeSet()
    return render(request, 'student/charts-company.html', {
         "stu_info": stu_info,
        'wktype':wktype
    })


def kaoyan(request):
    search_data = request.GET.get('q', "")
    queryset = School.objects.all()
    if search_data:
        queryset = School.objects.filter(
            Q(name__icontains=search_data) | Q(location__icontains=search_data)
        )
    location = request.GET.get('location', '')
    if location:
        queryset = School.objects.filter(location=location)
    stu_info = request.session.get('info')
    loctions = [i.get('location') for i in School.objects.all().values('location').distinct()]
    page_object = Pagination(request, queryset)
    context = {
        "stu_info": stu_info,
        "locations":loctions,
        "link": "https://yz.chsi.com.cn",
        "a0": "active",
        "search_data": search_data,
        "queryset": page_object.page_queryset,  # 分完页的数据
        "page_string": page_object.html()  # 页码
    }
    return render(request, 'student/kaoyan.html', context)
