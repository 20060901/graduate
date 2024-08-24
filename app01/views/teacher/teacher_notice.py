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
        model = Notice
        exclude = ['teacher']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control','style': 'height: 100px;'}),
             'classes': forms.SelectMultiple()
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
        # 获取用户选择的班级
        selected_classes = form.cleaned_data['classes']
        # 获取这些班级的学生ID列表
        student_ids = list(Student.objects.filter(classs__in=selected_classes).values_list('id', flat=True))
        # 将这些学生的状态设置为未读
        Student.objects.filter(id__in=student_ids).update(is_read=0)
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'error': form.errors})


def get_notice_edit_detail(request):
    eid = request.GET.get('eid')
    data_object = Notice.objects.filter(id=eid).values('title', 'content').first()
    if not data_object:
        return JsonResponse({'status': False, 'error': '通知不存在'})

    # 确保data_object存在后，获取关联的班级ID列表
    related_class_ids = []
    if data_object:
        notice = Notice.objects.get(id=eid)
        related_class_ids = list(notice.classes.values_list('id', flat=True))

    # 将关联的班级ID列表添加到data_dict中
    data_dict = {
        'status': True,
        'data': data_object,
        'class_ids': related_class_ids  # 添加关联班级ID列表
    }
    return JsonResponse(data_dict)


def teacher_notice_edit(request):
    eid = request.GET.get('eid')
    data_object = Notice.objects.filter(id=eid).first()
    if not data_object:
        return JsonResponse({'status': False, 'tips': '数据不存在'})
    form = NoticesModelForm(data=request.POST, instance=data_object)
    if form.is_valid():
        notice = form.save(commit=False)
        # 手动设置更新时间为当前时间
        notice.created_at = timezone.now()
        notice.save()  # 保存通知实例

        # 清除现有的班级关联，并设置新的班级关联
        notice.classes.clear()  # 清除现有的班级
        selected_classes = form.cleaned_data['classes']
        notice.classes.set(selected_classes)  # 设置新的班级
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'error': form.errors})


def teacher_notice_delete(request):
    did = request.GET.get('did')
    Notice.objects.filter(id=did).delete()
    return JsonResponse({'status': True})
