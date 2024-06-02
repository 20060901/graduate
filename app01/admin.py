from django.contrib import admin
from django.core.paginator import Paginator

from .models import Teacher, Class, Student, Notice


class TeacherAdmin(admin.ModelAdmin):
    # 设置管理员可看到的字段
    list_display = ['id', 'username',  'avatar', 'role', 'phone']
    list_per_page = 15
    # 分页控件，使用django默认控件
    paginator = Paginator


class ClassAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'teacher_id']
    list_per_page = 20
    # 分页控件，使用django默认控件
    paginator = Paginator


class StudentAdmin(admin.ModelAdmin):
    list_display = ['id', 'student_no', 'username', 'avatar', 'role', 'classs_id', 'phone', 'status', 'province']
    list_per_page = 20
    # 分页控件，使用django默认控件
    paginator = Paginator


class NoticeAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'content', 'teacher_id']
    list_per_page = 20
    # 分页控件，使用django默认控件
    paginator = Paginator


# 注册数据库模型以及类
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Class, ClassAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Notice, NoticeAdmin)
admin.site.site_header = '应届生去向系统后台'  # 设置header
admin.site.site_title = '应届生去向系统 | 管理员'  # 设置title
admin.site.index_title = '应届生去向系统后台'
