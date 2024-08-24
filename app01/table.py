from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from app01.utils import getDataView
from app01.models import *
from app01.utils.pagnition import PageInfo


def dataview(request):
    getAllJobInfos = getDataView.getAllJobInfos()
    # 获取搜索参数
    search_query = request.GET.get('search', '')
    # 根据搜索参数进行过滤
    if search_query:
        getAllJobInfos = [job for job in getAllJobInfos if search_query.lower() in job.title.lower()]
    # 招聘数据数量
    all_count = len(getAllJobInfos)
    # 分页
    page = request.GET.get('page')
    limit = request.GET.get('limit')
    page_info = PageInfo(page, all_count, '/dataView', per_page=limit)
    job_list = getAllJobInfos[page_info.start_data():page_info.end_data()]
    job_list = list(map(lambda x: model_to_dict(x), job_list))
    data = {
        'all_count': all_count,
        'job_list': job_list,
    }
    response_data = {
        'code': 0,
        'msg': 'ok',
        'data': data
    }
    return JsonResponse(response_data)


@csrf_exempt
@require_POST
def delete_job(request):
    job_id = request.POST.get('jobId')
    if not job_id:
        return JsonResponse({'code': 1, 'msg': '信息不存在'}, status=400)

    try:
        job = JobInfo.objects.get(id=job_id)
        job.delete()
        return JsonResponse({'code': 0, 'msg': '删除成功'})
    except JobInfo.DoesNotExist:
        return JsonResponse({'code': 1, 'msg': '删除失败'}, status=404)


@csrf_exempt
@require_POST
def edit_job(request):
    job_id = request.POST.get('jobId')
    title = request.POST.get('title')
    address = request.POST.get('address')
    educational=request.POST.get('educational')
    workExperience=request.POST.get('workExperience')
    companyTitle=request.POST.get('companyTitle')
    companyNature=request.POST.get('companyNature')
    companyPeople=request.POST.get('companyPeople')
    companyPeople=companyPeople[:-1].split('-')
    companyPeople = list(map(int, companyPeople))

    if not job_id or not title or not address:
        return JsonResponse({'code': 1, 'msg': '职位不存在'}, status=400)

    try:
        job = JobInfo.objects.get(id=job_id)
        job.title = title
        job.address = address
        job.educational=educational
        job.workExperience=workExperience
        job.companyTitle=companyTitle
        job.companyNature=companyNature
        job.companyPeople=companyPeople
        job.save()
        return JsonResponse({'code': 0, 'msg': '修改成功'})
    except JobInfo.DoesNotExist:
        return JsonResponse({'code': 1, 'msg': '修改失败'}, status=404)
