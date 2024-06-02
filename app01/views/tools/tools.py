import time

import numpy as np
from django.core.cache import cache
from django.shortcuts import render
from django.http import JsonResponse
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url


def class_cache_callback(mode, key, value=None):
    """
    缓存回调函数,在缓存条目失效时被调用
    mode: 操作类型, 可以是 'set', 'delete' 或 'invalidate'
    key: 缓存条目的 key
    value: 当 mode 为 'set' 时, 是缓存的值
    """
    if mode == 'delete' or mode == 'invalidate':
        # 当缓存条目被删除或失效时, 清空与 Class 相关的缓存
        cache.delete_many([
            'all_classes',
        ])
    elif mode == 'set':
        # 当缓存条目被设置时, 更新与 Class 相关的缓存
        if key == 'all_classes':
            cache.set('all_classes', value, 60 * 5)  # 缓存 5 分钟


def getNewName(file_type):
    # 前面是file_type+年月日时分秒
    new_name = time.strftime(file_type + '-%Y%m%d%H%M%S', time.localtime())
    # 最后是5个随机数字
    # Python中的numpy库中的random.randint(a, b, n)表示随机生成n个大于等于a，小于b的整数
    ranlist = np.random.randint(0, 10, 5)
    for i in ranlist:
        new_name += str(i)
    # 加后缀名
    new_name += '.jpg'
    # 返回字符串
    return new_name


def logout(request):
    request.session.clear()
    return render(request, 'everyone/logout.html')


def error(request):
    return render(request, 'everyone/error.html')


def refresh_captcha(request):
    # 生成新的验证码
    new_key = CaptchaStore.generate_key()
    # 获取新验证码的 URL
    new_captcha_image_url = captcha_image_url(new_key)

    # 返回 JSON 数据
    return JsonResponse({
        'key': new_key,
        'image_url': new_captcha_image_url
    })
