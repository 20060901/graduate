import os
from django import forms
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from django.core.validators import RegexValidator
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from Graduate.settings import MEDIA_ROOT
from app01 import models
from app01.models import Student, Class, Teacher
from app01.utils.bootstrap import BootStrapModelForm, BootStrapForm
from app01.views.tools.tools import getNewName, class_cache_callback

from django.contrib.auth import update_session_auth_hash
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

class TeacherLoginForm(BootStrapForm):
    username = forms.CharField(label='用户名', widget=forms.TextInput,
                               required=True)
    phone = forms.CharField(label='手机号',
                            validators=[RegexValidator(r'^1\d{10}$', '手机号格式错误！')],
                            widget=forms.TextInput, required=True)
    password = forms.CharField(label='密码',
                               widget=forms.PasswordInput, required=True)


def teacher_forgetpasswd(request):
    if request.method == 'GET':
        return render(request, 'teacher/teacher_forgetpasswed.html')
    email = request.POST.get('email')
    if Teacher.objects.filter(email=email).exists():
        # 发送重置密码链接
        user = Teacher.objects.get(email=email)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        link = request.build_absolute_uri(reverse('reset-teacher-password', kwargs={'uidb64': uid, 'token': token}))
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
            '教师端密码找回',
            message='',
            html_message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email, ],
        )
        messages.error(request, '邮件已发送!!!')
        return redirect('/teacher/forgetpasswd/')
    else:
        messages.error(request, '该邮箱不存在!!!')
        return redirect('/teacher/forgetpasswd/')



def reset_password(request, uidb64, token):
    try:
        uid = force_bytes(urlsafe_base64_decode(uidb64))
        user = Teacher.objects.get(pk=uid)
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
                return render(request, 'teacher/teacher_reset_password.html', context=context_data)
        else:
            context_data.update({
                'uidb64': uidb64,
                'token': token,
                'email': user.email
            })
            return render(request, 'teacher/teacher_reset_password.html', context=context_data)
    else:
        messages.error(request, '链接失效')
        return render(request, 'teacher/teacher_reset_password.html', context=context_data)










def teacher_login(request):
    if request.method == "GET":
        form = TeacherLoginForm()
        return render(request, 'everyone/teacher_login.html', {"form": form})
    form = TeacherLoginForm(request.POST)
    if not form.is_valid():
        return render(request, 'everyone/teacher_login.html', {"form": form})
    username = form.cleaned_data["username"]
    phone = form.cleaned_data["phone"]
    password = form.cleaned_data["password"]
    # 判断手机号是否存在：
    if not models.Teacher.objects.filter(phone=phone).exists():
        return render(request, 'everyone/teacher_login.html', {"form": form, 'error_msg': '手机号不存在！'})
    teacher = models.Teacher.objects.get(phone=phone, username=username)
    if teacher.check_password(password) or password == teacher.password:
        # 判断：如果当前教师avatar字段为空，则添加为app1/default_avatar.jpg使其拥有默认头像
        if not teacher.avatar:
            teacher.avatar = 'app1/default_avatar.jpg'
            teacher.save()
    else:
        return render(request, 'everyone/teacher_login.html', {"form": form, 'error_msg': '信息填写有误！'})

    # 将用户信息存入session
    request.session['info'] = {'id': teacher.id, 'username': teacher.username, 'role': teacher.role,
                               'avatar': teacher.avatar.url, 'phone': teacher.phone}
    # print(request.session['info'])
    request.session.set_expiry(60 * 60 * 24 * 7)
    return redirect('/teacher_index/')


def save_image(request, name):
    if 'pic' in request.FILES:
        pic = request.FILES['pic']
        new_name = getNewName('avatar')
        save_path = os.path.join(MEDIA_ROOT, "app1", new_name)
        # 确保目录存在
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'wb') as f:
            for content in pic.chunks():
                f.write(content)
        name.avatar = ('app1/%s' % new_name)
    else:
        # 如果没有上传图片,则使用默认值或保留原有值
        name.avatar = name.avatar


def teacher_index(request):
    teacher_info = request.session.get('info')

    queryset = Teacher.objects.filter(id=teacher_info['id'])
    # 获取当前登陆老师所管理的所有班级
    manage_class = Class.objects.filter(teacher_id=teacher_info['id'])
    # 获取当前登陆老师的所有同事
    colleagues = Teacher.objects.all()
    # 获取老师管理的班级的学生人数 学生和班级存在外键关联
    context = {
        'teacher_info': teacher_info,
        'queryset': queryset,
        'manage_class': manage_class,
        'colleagues': colleagues,
    }
    if request.method == 'POST':
        teacher = Teacher.objects.get(id=teacher_info['id'])
        phone = request.POST.get('phone')
        if phone != teacher.phone:
            # 手机号码被修改,检查是否已被注册
            if Teacher.objects.filter(phone=phone).exists() or Student.objects.filter(phone=phone).exists():
                # 手机号码已被注册
                messages.warning(request, '该手机号已被注册！')
                return redirect('/teacher_index/')
        teacher.username = request.POST.get('username')
        teacher.phone = request.POST.get('phone')
        email=request.POST.get('email')
        if email != teacher.email:
            if Teacher.objects.filter(email=email).exists() or Student.objects.filter(email=email).exists():
                messages.warning(request, '该邮箱已被注册！')
                return redirect('/teacher_index/')
        teacher.email = request.POST.get('email')
        save_image(request, teacher)
        teacher.save()
        messages.success(request, '修改成功！')
        teacher_info['username'] = teacher.username
        teacher_info['phone'] = teacher.phone
        teacher_info['email'] = teacher.email
        teacher_info['avatar'] = teacher.avatar.url
        request.session['info'] = teacher_info
        return redirect('/teacher_index/')
    return render(request, 'teacher/teacher_index.html', context)


def teacher_edit_password(request):
    # 获取当前登陆教师信息
    teacher_info = request.session.get('info')
    password = request.POST.get('password')
    repassword = request.POST.get('repassword')
    if password == repassword:
        if (password == '') or (repassword == ''):
            return JsonResponse({'status': False, 'error': '密码不能为空'})
        else:
            Teacher.objects.filter(id=teacher_info['id']).update(password=make_password(repassword))
            return JsonResponse({'status': True})
    else:
        return JsonResponse({'status': False, 'error': '两次输入的密码不一致'})


class StudentModelForm(BootStrapModelForm):
    phone = forms.CharField(
        label="手机号",
        validators=[RegexValidator(r'^1\d{10}$', '手机号格式错误！')]
        #   RegexValidator(r'^1\d{10}$', '手机号格式错误！') 前面是正则表达式，后面是报错提示信息
    )

    class Meta:
        model = Student
        exclude = ['id', 'role', 'avatar', 'is_read']
        widgets = {
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': "current-password"})
        }

    def save(self, commit=True):
        student = super().save(commit=False)
        student.set_password(self.cleaned_data['password'])
        if commit:
            student.save()
        return student


def teacher_student_views(request):
    teacher_info = request.session['info']
    # 获取当前登陆老师所管理的所有班级
    classes = Class.objects.filter(teacher=teacher_info.get('id'))
    form = StudentModelForm()
    # 新增学生信息的时候，让可选择的班级为当前老师所管理的班级
    form.fields['classs'].queryset = classes
    # 准备一个列表来保存所有学生
    students_list = []
    # 遍历每个班级，获取学生信息
    for class_ in classes:
        students = Student.objects.filter(classs=class_)
        students_list.extend(students)
    context = {
        'teacher_info': teacher_info,
        'students': students_list,
        'form': form
    }
    return render(request, 'teacher/teacher_student_views.html', context)


@csrf_exempt
def add_student(request):
    form = StudentModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        return JsonResponse({'status': True})
    else:
        return JsonResponse({'status': False, 'error': form.errors})


def get_edit_detail(request):
    eid = request.GET.get('eid')
    data_object = Student.objects.filter(id=eid).values('student_no', 'username', 'phone', 'password',
                                                        'classs', 'status', 'province').first()
    data_dict = {
        'status': True,
        'data': data_object
    }
    # print(data_dict)
    return JsonResponse(data_dict)


def teacher_student_edit(request):
    """ ajax请求"""
    eid = request.GET.get('eid')
    data_object = Student.objects.filter(id=eid).first()
    if not data_object:
        return JsonResponse({'status': False, 'tips': '数据不存在'})
    form = StudentModelForm(data=request.POST, instance=data_object)
    if form.is_valid():
        form.save()
        return JsonResponse({'status': True})

    return JsonResponse({'status': False, 'error': form.errors})


def delete_student(request):
    did = request.GET.get('did')
    Student.objects.filter(id=did).delete()
    return JsonResponse({'status': True})


class ClassesModelForm(BootStrapModelForm):
    name = forms.CharField(label='班级名称', widget=forms.TextInput,
                           required=True)

    class Meta:
        model = Class
        exclude = ['teacher']


from django.views.decorators.cache import cache_control


def teacher_classes_views(request):
    teacher_info = request.session['info']
    all_classes = Class.objects.filter(teacher_id=teacher_info['id'])
    form = ClassesModelForm()
    context = {
        'teacher_info': teacher_info,
        'classes': all_classes,
        'form': form
    }
    return render(request, 'teacher/teacher_classes_views.html', context)


@csrf_exempt
def add_class(request):
    teacher_info = request.session['info']
    form = ClassesModelForm(data=request.POST)
    if form.is_valid():
        form.instance.teacher_id = teacher_info['id']
        form.save()
        return JsonResponse({'status': True})
    else:
        return JsonResponse({'status': False, 'error': form.errors})


def delete_class(request):
    did = request.GET.get('did')
    Class.objects.filter(id=did).delete()
    return JsonResponse({'status': True})


def get_classes_edit_detail(request):
    eid = request.GET.get('eid')
    data_object = Class.objects.filter(id=eid).values('name', 'teacher_id').first()
    data_dict = {
        'status': True,
        'data': data_object
    }
    return JsonResponse(data_dict)


def teacher_classes_edit(request):
    eid = request.GET.get('eid')
    data_object = Class.objects.filter(id=eid).first()
    if not data_object:
        return JsonResponse({'status': False, 'tips': '数据不存在'})
    form = ClassesModelForm(data=request.POST, instance=data_object)
    if form.is_valid():
        form.save()
        return JsonResponse({'status': True})

    return JsonResponse({'status': False, 'error': form.errors})
