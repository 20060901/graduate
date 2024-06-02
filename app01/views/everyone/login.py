from captcha.fields import CaptchaField
from django import forms
from django.core.validators import RegexValidator
from django.shortcuts import render, redirect
from app01.models import Student
from app01.utils.bootstrap import BootStrapForm


class LoginForm(BootStrapForm):
    phone = forms.CharField(label='手机号:',
                            validators=[RegexValidator(r'^1\d{10}$', '手机号格式错误！')],
                            widget=forms.TextInput, required=True)
    password = forms.CharField(label='密码:',
                               widget=forms.PasswordInput, required=True)


def login(request):
    if request.method == "GET":
        form = LoginForm()
        return render(request, 'everyone/login.html', {"form": form})
    form = LoginForm(request.POST)
    if not form.is_valid():
        return render(request, 'everyone/login.html', {"form": form})
    phone = form.cleaned_data["phone"]
    password = form.cleaned_data["password"]
    try:
        student = Student.objects.get(phone=phone)
        if student.check_password(password) or password == student.password:
            # 登录成功
            # 判断：如果当前学生的avatar字段为空，则添加为app1/default_avatar.jpg使其拥有默认头像
            if student.avatar == '':
                student.avatar = 'app1/default_avatar.jpg'
                student.save()
            request.session['info'] = {
                'id': student.id,
                'username': student.username,
                'role': student.role,
                'avatar': student.avatar.url,
                'class': student.classs.id,
                'province': student.province
            }
            request.session.set_expiry(60 * 60 * 24 * 7)
            return redirect('/student/index/')
        else:
            # 密码错误
            return render(request, 'everyone/login.html', {"form": form, 'error_msg': '手机号或密码错误'})
    except Student.DoesNotExist:
        # 手机号未注册
        return render(request, 'everyone/login.html', {"form": form, 'error_msg': '手机号未注册'})
