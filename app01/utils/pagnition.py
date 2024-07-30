# 导入django模块
# from django.core.paginator import Paginator,Page

class PageInfo(object):
    def __init__(self,current_page,all_count,base_url,per_page=10,show_page=11):
        """

        :param current_page: 当前页
        :param all_count: 总页数
        :param base_url: 模板
        :param per_page: 每页显示数据条数
        :param show_page: 显示链接页个数
        """
        # 若 url错误，默认显示第一页（错误类型可能是：空页面编号，非整数型页面编号）
        try:
            self.current_page=int(current_page)
            self.per_page=int(per_page)
        except Exception as e:
            self.current_page = 1
            self.per_page=10

        # 根据数据库信息条数得出总页数
        a,b=divmod(all_count,self.per_page)
        if b:
            a+=1
        self.all_page=a
        self.base_url=base_url
        self.show_page=show_page

    # 当前页起始数据id
    def start_data(self):
        return (self.current_page-1)*self.per_page

    def end_data(self):
        return self.current_page * self.per_page

    # 动态生成前端html
    def pager(self):
        page_list=[]
        half=int((self.show_page-1)/2)
        #
        if self.all_page<self.show_page:
            start_page=1
            end_page=self.all_page+1

        else:
            if self.current_page<=half:
                start_page=1
                end_page=self.show_page+1
            else:
                if self.current_page+half>self.all_page:
                    end_page=self.all_page+1
                    start_page=end_page-self.show_page
                else:
                    start_page=self.current_page-half
                    end_page=self.current_page+half+1
        # 上一页（若当前页等于第一页，则上一页无链接，否则链接为当前页减1）
        if self.current_page<=1:
            prev_page="<li class='prev'><a href='#'><i class='entypo-left-open'></i></a></li>"
        else:
            prev_page="<li class='prev'><a href='%s?page=%s'><i class='entypo-left-open'></i></a></li>"%(self.base_url,self.current_page-1)
        page_list.append(prev_page)
        # 动态生成中间页数链接
        for i in range(start_page,end_page):
            if i == self.current_page:
                temp="<li class='active'><a href='%s?page=%s'>%s</a></li>"% (self.base_url, i, i)
            else:
                temp="<li><a href='%s?page=%s'>%s</a></li>"% (self.base_url, i, i)
            page_list.append(temp)
        # 下一页（若当前页等于最后页，则下一页无链接，否则链接为当前页加1）
        if self.current_page >= self.all_page:
            next_page = "<li class='next'><a href='#'><i class='entypo-right-open'></i></a></li>"
        else:
            next_page = "<li class='next'><a href='%s?page=%s'><i class='entypo-right-open'></i></a></li>"%(self.base_url,self.current_page+1)
        page_list.append(next_page)

        return ''.join(page_list)