from django import forms
from django.contrib import messages
from django.core.validators import RegexValidator
from django.shortcuts import render, redirect

from app01.models import Student, Class
from app01.utils.bootstrap import BootStrapModelForm


class StudentRegisterModelForm(BootStrapModelForm):
    phone = forms.CharField(
        label="手机号",
        validators=[RegexValidator(r'^1\d{10}$', '手机号格式错误！')]
    )
    password = forms.CharField(label='密码', widget=forms.PasswordInput())

    class Meta:
        model = Student
        exclude = ['avatar', 'role', 'status', 'classs', 'is_read']
        widgets = {
            'password': forms.PasswordInput(attrs={'class': 'form-control'})
        }


def register(request):
    classes = Class.objects.all()
    if request.method == 'GET':
        form = StudentRegisterModelForm()
    else:
        form = StudentRegisterModelForm(request.POST)
        if form.is_valid():
            # 保存表单数据到数据库
            user = form.save(commit=False)  # 先不保存到数据库
            # 从表单中获取班级信息，并设置到用户对象上
            user.classs = Class.objects.get(id=request.POST.get('class'))
            user.set_password(form.cleaned_data['password'])  # 设置加密的密码
            user.save()  # 保存用户对象到数据库
            messages.success(request, '注册成功，请登录')  # 添加成功消息
            return redirect('/')  # 重定向到登录页面

    context = {
        'form': form,
        'classes': classes,
    }
    return render(request, 'everyone/register.html', context)  # 渲染并返回注册页面
