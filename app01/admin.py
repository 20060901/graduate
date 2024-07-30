from django.contrib import admin
from django.core.paginator import Paginator
from django.utils.html import format_html
from .models import *
from django.utils.safestring import mark_safe

class TeacherAdmin(admin.ModelAdmin):
    # 设置管理员可看到的字段
    list_display = ['id', 'username',  'avatar_display', 'role', 'phone']
    list_per_page = 15
    # 分页控件，使用django默认控件
    paginator = Paginator
    def avatar_display(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" width="40" height="40" style="border-radius: 20px;">'.format(obj.avatar.url))
        return ''
    avatar_display.short_description = '头像'


class ClassAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'teacher_id']
    list_per_page = 20
    # 分页控件，使用django默认控件
    paginator = Paginator


class StudentAdmin(admin.ModelAdmin):
    list_display = ['id', 'student_no', 'username', 'avatar_display', 'role', 'classs_id', 'phone', 'status', 'province']
    list_per_page = 20
    # 分页控件，使用django默认控件
    paginator = Paginator
    def avatar_display(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" width="40" height="40" style="border-radius: 20px;">'.format(obj.avatar.url))
        return ''
    avatar_display.short_description = '头像'


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
