import os
from django import forms
from django.core.validators import RegexValidator
from django.http import JsonResponse, HttpResponse
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


from django.contrib.auth import update_session_auth_hash
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator


def student_forgetpasswd(request):
    if request.method == 'GET':
        return render(request, 'student/student_forgetpasswd.html')
    email = request.POST.get('email')
    if Student.objects.filter(email=email).exists():
        # 发送重置密码链接
        user = Student.objects.get(email=email)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        link = request.build_absolute_uri(reverse('reset-student-password', kwargs={'uidb64': uid, 'token': token}))
        message = f"""
                                <html>
                                    <head>
                                        <style>
                                            body {{
                                                font-family: Arial, sans-serif;
                                                background-color: #f2f2f2;
                                            }}

                                            .container {{
                                                position: relative;
                                                max-width: 600px;
                                                margin: 0 auto;
                                                padding: 20px;
                                                background-color: #fff;
                                                border-radius: 5px;
                                                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                                            }}

                                            h1 {{
                                                color: #333;
                                                font-size: 24px;
                                                margin-bottom: 20px;
                                            }}

                                            p {{
                                                color: #555;
                                                font-size: 16px;
                                                line-height: 1.5;
                                            }}

                                            a {{
                                                color: #007bff;
                                                text-decoration: none;
                                            }}

                                            a:hover {{
                                                text-decoration: underline;
                                            }}

                                            p.signature {{
                                                position: absolute;
                                                bottom: 10px;
                                                right: 30px;
                                                color: #555;
                                                font-size: 16px;
                                                line-height: 1.5;
                                            }}
                                        </style>
                                    </head>
                                    <body>
                                        <div class="container">
                                            <h1>请重置您的密码！</h1>
                                            <p>点击链接开始重置：</p>
                                            <p><a href="{link}">点击重置</a></p>
                                            <p>如果链接不可用，请复制以下内容到浏览器重置密码：</p>
                                            <p>{link}</p>
                                            <br>
                                            <br>
                                            <p class="signature">原宝</p>
                                        </div>
                                    </body>
                                </html>
                                """

        send_mail(
            '学生端密码找回',
            message='',
            html_message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email, ],
        )
        messages.error(request, '邮件已发送!!!')
        return redirect('/student/forgetpasswd/')
    else:
        messages.error(request, '该邮箱不存在!!!')
        return redirect('/student/forgetpasswd/')

def reset_password(request, uidb64, token):
    try:
        uid = force_bytes(urlsafe_base64_decode(uidb64))
        user = Student.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Teacher.DoesNotExist):
        user = None
    context_data = {}
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password1 = request.POST.get('new_password1')
            password2 = request.POST.get('new_password2')
            if password1 == password2:
                user.set_password(password1)
                user.save()
                update_session_auth_hash(request, user)
                messages.error(request, '重置成功')
                return redirect('/')
            else:
                messages.error(request, '两次密码不一致')
                return render(request, 'student/student_reset_password.html', context=context_data)
        else:
            context_data.update({
                'uidb64': uidb64,
                'token': token,
                'email': user.email
            })
            return render(request, 'student/student_reset_password.html', context=context_data)
    else:
        messages.error(request, '链接失效')
        return render(request, 'student/student_reset_password.html', context=context_data)




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
        email=request.POST.get('email')
        print(email)
        if email != student.email:
            if Teacher.objects.filter(email=email).exists() or Student.objects.filter(email=email).exists():
                messages.warning(request, '该邮箱已被注册！')
                return redirect('/student/index/')
        student.email = request.POST.get('email')
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
        messages.success(request, '修改成功！')
        stu_info['username'] = student.username
        # 将加密后的密码保存到session
        stu_info['phone'] = student.phone
        stu_info['avatar'] = student.avatar.url
        stu_info['status'] = student.status
        stu_info['province'] = student.province
        stu_info['email'] = student.email
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
    # 从session中获取学生信息
    stu_info = request.session.get('info')

    # 获取学生所关联的班级
    student_classes = Class.objects.filter(id=stu_info['class'])

    # 过滤出与学生班级相关的通知
    notices = Notice.objects.filter(classes__in=student_classes).order_by('-created_at')

    # 获取与学生相关的老师信息，可以根据需要获取
    # 假设学生的class有teacher信息，这里可以直接获取
    teacher_ids = student_classes.values_list('teacher_id', flat=True).distinct()
    laoshi_info = Teacher.objects.filter(id__in=teacher_ids)

    context = {
        "stu_info": stu_info,
        'laoshi_info': laoshi_info,
        'notices': notices
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

from spider.spiderMain import spider

def dataTable(request):
    stu_info = request.session.get('info')
    if request.method == 'POST':
        job=request.POST.get('occupation')
        job=str(job)
        startPage=request.POST.get('startPage')
        startPage=int(startPage)
        endPage=request.POST.get('endPage')
        endPage=int(endPage)
        spiderObj = spider(job, startPage)
        spiderObj.init()
        spiderObj.main(endPage)
        spiderObj.save_to_sql()
        context = {
            "stu_info": stu_info,
        }
        return render(request, "student/job.html", context)

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
    print(stu_info)
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

def calendar(request):
    stu_info = request.session.get('info')
    return render(request, 'student/calendar.html', {
        "stu_info": stu_info,
    })
