import datetime

from django import forms
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from app01 import models
from app01.models import Student, Class, Notice
from app01.utils.bootstrap import BootStrapModelForm


class NoticesModelForm(BootStrapModelForm):
    class Meta:
        model = models.Notice
        exclude = ['teacher']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control'}),
        }


def manage_notice(request):
    teacher_info = request.session['info']
    form = NoticesModelForm
    notices = Notice.objects.filter(teacher_id=teacher_info['id']).order_by('-id')
    today = timezone.now().date()
    yesterday = today - datetime.timedelta(days=1)

    context = {
        'teacher_info': teacher_info,
        'notices': notices,
        'form': form,
    }
    return render(request, 'teacher/manage_notice.html', context)


@csrf_exempt
def add_notice(request):
    teacher_info = request.session['info']
    form = NoticesModelForm(data=request.POST)
    if form.is_valid():
        # 当前登录的是哪个老师，则发布通知的时候就，发布人就是当前登录系统的老师的【id】
        form.instance.teacher_id = teacher_info['id']
        form.save()
        # 获取当前登陆老师管理的所有班级
        classes = Class.objects.filter(teacher=teacher_info['id'])
        # 老师所管理的所有学生的【id】
        student_ids = list(Student.objects.filter(classs__in=classes).values_list('id', flat=True))
        # 循环将他们的状态设置为【未读】通知。因为每次当老师发布新的通知的时候，学生们的状态应该都要变成【未读】
        for i in student_ids:
            Student.objects.filter(id=i).update(is_read=0)
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'error': form.errors})
