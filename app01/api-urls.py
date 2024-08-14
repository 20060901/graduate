from django.urls import path

from app01 import charts, table

urlpatterns = [
    #路由 视图函数 别名（url反编译）
    path('dataview/',table.dataview),
    path('get_xingzi_qk/',charts.xingzi_qk),
    path('get_gongsi_qk/',charts.gongsi_qk),
    path('get_jineng_qk/',charts.jineng_qk),
    path('get_chengshi_qk/',charts.chengshi_qk),

    path('delete_job/', table.delete_job, name='delete_job'),
    path('edit_job/', table.edit_job, name='edit_job'),


]
