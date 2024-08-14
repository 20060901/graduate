import os
import jieba
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from django.conf import settings
from wordcloud import WordCloud


# 假设字体文件STHUPO.TTF位于项目的根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_PATH = os.path.join(BASE_DIR,'utils', 'STHUPO.TTF')

def getImageByTags(text):
    # 分词
    text_jieba = "".join(jieba.cut(text))
    # 蒙版
    img = Image.open(os.path.join(settings.BASE_DIR, 'F:\\graduates-master\\app01\\static\\img\\china.png'))
    img_arr = np.array(img)
    wordcount = WordCloud(
        background_color='white',
        mask=img_arr,
        font_path=FONT_PATH,
    ).generate_from_text(text_jieba)
    if not os.path.exists(os.path.join(settings.BASE_DIR, 'F:\\graduates-master\\app01\\static\\img\\tagscloud.png')):
        # 绘制图片
        plt.figure(1)
        plt.imshow(wordcount)
        plt.axis("off")

        # os.remove('D:/.vs/djangoProject1/static/img/100.png')
        plt.savefig(os.path.join(settings.BASE_DIR, 'F:\\graduates-master\\app01\\static\\img\\tagscloud.png'))

    return '/static/img/tagscloud.png'


def getImageByNature(text):
    # 分词
    text_jieba = "".join(jieba.cut(text))

    # 蒙版
    img = Image.open(os.path.join(settings.BASE_DIR, 'F:\\graduates-master\\app01\\static\\img\\nature.png'))
    img_arr = np.array(img)
    wordcount = WordCloud(
        background_color='white',
        mask=img_arr,
        font_path=FONT_PATH
    ).generate_from_text(text_jieba)
    if not os.path.exists(os.path.join(settings.BASE_DIR, 'F:\\graduates-master\\app01\\static\\img\\naturecloud.png')):
        # 绘制图片
        plt.figure(1)
        plt.imshow(wordcount)
        plt.axis("off")

        # os.remove('D:/.vs/djangoProject1/static/img/200.png')
        plt.savefig(os.path.join(settings.BASE_DIR, 'F:\\graduates-master\\app01\\static\\img\\naturecloud.png'))

    return '/static/img/naturecloud.png'


def getImagesByAddTags(address, text):
    # 分词
    text_jieba = "".join(jieba.cut(text))
    if not os.path.exists(os.path.join(settings.BASE_DIR, 'F:\\graduates-master\\app01\\static\\img\\' + address + 'cloud.png')):
        # 蒙版
        # img = Image.open(os.path.join(settings.BASE_DIR, 'F:\\graduates-master\\app01\\static\\img\\true.jpg'))
        # img_arr = np.array(img)
        wordcount = WordCloud(
            background_color='white',
            # mask=img_arr,
            font_path=FONT_PATH
        ).generate_from_text(text_jieba)

        # 绘制图片
        plt.figure(1)
        plt.imshow(wordcount)
        plt.axis("off")

        # os.remove('D:/.vs/djangoProject1/static/img/china.png')
        plt.savefig(os.path.join(settings.BASE_DIR, 'F:\\graduates-master\\app01\\static\\img\\' + address + 'cloud.png'))

    return '/static/img/' + address + 'cloud.png'
