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


class TeacherLoginForm(BootStrapForm):
    username = forms.CharField(label='用户名', widget=forms.TextInput,
                               required=True)
    phone = forms.CharField(label='手机号',
                            validators=[RegexValidator(r'^1\d{10}$', '手机号格式错误！')],
                            widget=forms.TextInput, required=True)
    password = forms.CharField(label='密码',
                               widget=forms.PasswordInput, required=True)


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
        save_image(request, teacher)
        teacher.save()
        teacher_info['username'] = teacher.username
        teacher_info['phone'] = teacher.phone
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
