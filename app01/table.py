from django.forms.models import model_to_dict
from django.http import JsonResponse

from app01.utils import getDataView

from app01.utils.pagnition import PageInfo


def dataview(request):
    getAllJobInfos = getDataView.getAllJobInfos()
    # 招聘数据数量
    all_count = len(getAllJobInfos)
    # 分页
    page=request.GET.get('page')
    limit=request.GET.get('limit')
    page_info = PageInfo(page, all_count, '/dataView', per_page=limit, )
    # pager=page_info.pager()
    # 每页多少条
    job_list = getAllJobInfos[page_info.start_data():page_info.end_data()]

    job_list=list(map(lambda x:model_to_dict(x),job_list))
    data={
        'all_count':all_count,
        'job_list': job_list,
    }
    response_data = {
        'code': 0,
        'msg': 'ok',
        'data': data
    }
    return JsonResponse(response_data)
