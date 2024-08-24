from django.conf.urls.static import static
from django.contrib import admin
from django.views.static import serve
from django.urls import path, include, re_path
from Graduate import settings
from Graduate.settings import MEDIA_ROOT
from app01.views.everyone import login, register
from app01.views.student import student, student_echarts
from app01.views.teacher import teacher, teacher_echarts, teacher_notice
from app01.views.tools import tools
from app01.views.tools import *

urlpatterns = [
                  path('', login.login),
                  re_path(r'^api/', include('app01.api-urls')),
                  path("admin/", admin.site.urls),
                  path('register/', register.register),
                  path('error/', tools.error),
                  path('captcha/', include('captcha.urls')),
                  path('refresh_captcha/', tools.refresh_captcha, name='refresh_captcha'),
                  # 学生登录页面
                  path('student/index/', student.stu_index),
                  path('student/edit/password/', student.student_edit_password),
                  path("student/forgetpasswd/", student.student_forgetpasswd),
                  path('reset-student-password/<str:uidb64>/<str:token>/', student.reset_password,
                       name='reset-student-password'),
                  path('logout/', tools.logout),
                  path('student/china/', student_echarts.student_china),
                  path('student/get/china/data/', student_echarts.student_get_china_data),
                  path('student/notice/', student.student_notice),
                  path('student/get/notice/', student.student_get_notice),
                  path('student/xinzi/', student.xinzi),
                  path('student/dataTable/', student.dataTable),
                  path("student/dataView/", student.dataView),
                  path('student/chartsSkill/', student.chartsSkill),
                  path('student/chartsTags/', student.chartsTags),
                  path('student/chartsAddr/', student.chartsAddr),
                  path('student/chartsCompany/', student.chartsCompany),
                  path('student/kaoyan/', student.kaoyan),
                  path('student/calendar/', student.calendar),

                  # 学生清除红点
                  path('student/clear_notice/', student.student_clear_notice),
                  # 教师登陆
                  path('teacher/login/', teacher.teacher_login),
                  path("teacher/forgetpasswd/", teacher.teacher_forgetpasswd),
                  path('reset-teacher-password/<str:uidb64>/<str:token>/', teacher.reset_password,
                       name='reset-teacher-password'),
                  path('teacher_index/', teacher.teacher_index),
                  # 教师查看学生信息
                  path('teacher_student_views/', teacher.teacher_student_views),
                  path('teacher/edit/password/', teacher.teacher_edit_password),
                  path('teacher/add/', teacher.add_student),
                  path('teacher/delete/', teacher.delete_student),
                  path('get/edit_detail/', teacher.get_edit_detail),
                  path('teacher/student_edit/', teacher.teacher_student_edit),
                  # 教师管理班级信息
                  path('teacher_classes_views/', teacher.teacher_classes_views),
                  path('teacher/add/class/', teacher.add_class),
                  path('teacher/classes/delete/', teacher.delete_class),
                  path('get/classes/edit_detail/', teacher.get_classes_edit_detail),
                  path('teacher/classes_edit/', teacher.teacher_classes_edit),
                  # 教师页面查看班级以及学生的详情表
                  path('students/echarts/', teacher_echarts.students_echarts),
                  path('teacher_manage_classes/', teacher_echarts.teacher_manage_classes),
                  path('teacher_classes_status/', teacher_echarts.teacher_classes_status),
                  path('teacher/china/', teacher_echarts.teacher_china),
                  path('teacher/get/china/data/', teacher_echarts.teacher_get_china_data),
                  # 教师发布通知和管理通知
                  path('teacher/add/notice/', teacher_notice.add_notice),
                  path('teacher_manage/notice/', teacher_notice.manage_notice),
                  path('teacher/get/notice/edit_detail/', teacher_notice.get_notice_edit_detail),
                  path('teacher/notice/edit/', teacher_notice.teacher_notice_edit),
                  path('teacher/notice/delete/', teacher_notice.teacher_notice_delete),
                  # path(r'^static/(?P<path>.*)$', serve, {'document_root': MEDIA_ROOT})
                  path('static/<path:path>', serve, {'document_root': MEDIA_ROOT})
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = register.page_not_found
