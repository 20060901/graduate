from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin


class Interceptor(MiddlewareMixin):
    """ 中间件 """

    def process_request(self, request):
        # 0、排除不需要登陆就可以访问的页面
        # request.path_info   获取当前用户访问的URL地址
        if request.path_info.startswith(
                ('/', 'register/', 'logout/', 'admin/', 'teacher/login/', 'error/', 'captcha/')):
            return None
        # 1、读取当前session信息
        # 如果能读到session,说明已登录过,可以放行
        info_dict = request.session.get('info')
        if info_dict:
            user_role = info_dict.get('user_role')
            # 2、根据用户角色进行权限控制
            if user_role == 0:  # 0代表老师
                # 老师只能访问 /teacher/* 开头的页面
                if request.path_info.startswith('/teacher/') or request.path_info.startswith('/media/'):
                    return None
                else:
                    return redirect('/error/')
            else:  # 1代表学生
                # 学生只能访问 /student/* 开头的页面
                if request.path_info.startswith('/student/') or request.path_info.startswith('/media/'):
                    return None
                else:
                    return redirect('/error/')
        else:
            # 没有找到session信息, 说明未登录, 拦截访问
            return redirect('/')
