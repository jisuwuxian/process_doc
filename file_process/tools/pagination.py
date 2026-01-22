"""
Created on
应用举例：
from process.pagination import Pagination
def lianghao_list(request):
    page_ination = Pagination(request, lianghao, field_contains='mobile__contains')
    return render(request, 'lianghao_list.html', {
        'form': page_ination.queryset,
        'page_list_str': page_ination.page_list_str
    })
"""
from django.shortcuts import render, redirect, HttpResponse
from process.models import ErrorCorrection, departments, employees, lianghao
from process.utils import extract_and_correct
import datetime
from django import forms
from django.core.validators import RegexValidator
from django.utils.safestring import mark_safe
import copy
from django.http.request import QueryDict


class Pagination(object):
    """
    分页功能
    database_total: 数据库表名称，用于计算总记录数
    page_param: 分页参数，默认值为"page"
    field_contains: 搜索字段，默认值为"name__contains"
    per_page: 每页显示记录数，默认值为10
    """

    # Fixed syntax error in method definition
    def __init__(self, request, database_total, page_param="page", field_contains="name__contains", per_page=10):
        # 深拷贝请求中的查询参数，避免直接修改原始QueryDict
        query_dict = copy.deepcopy(request.GET)
        # 设置查询字典为可修改状态，以便后续添加/修改分页参数
        query_dict._mutable = True
        # 将可修改的查询参数字典保存为实例属性
        self.query_dict = query_dict
        # 保存分页参数名称（默认为'page'）到实例属性
        self.page_param = page_param

        self.request = request
        # 获取总记录数，用于分页计算
        self.total_count = database_total.objects.all().count()


        # Get page parameter from request properly
        self.page_param = page_param
        page = request.GET.get(page_param, 1)

        # 每页显示记录数
        self.per_page = per_page

        try:
            page = int(page)
            if page > (self.total_count + self.per_page - 1) // self.per_page:
                page = (self.total_count + self.per_page - 1) // self.per_page
            if page < 1:
                page = 1
        except ValueError:
            page = 1
        if not page:
            page = 1

        # 计算偏移量，用于分页查询
        self.offset = (page - 1) * self.per_page

        # 计算总页数，用于分页导航
        self.total_page = (self.total_count + self.per_page - 1) // self.per_page
        # 处理分页参数，确保页码为有效整数
        page = max(1, min(page, self.total_page))
        self.current_page = page
        self.previous_page = page - 1 if page > 1 else 1
        self.next_page = page + 1 if page < self.total_page else self.total_page

        # 拼接request.get

        self.query_dict.setlist(page_param, [1])  # 首页 url地址拼接
        # 拼接分页导航链接
        page_list = []
        page_list.append(f"<li><a href='?{self.query_dict.urlencode()}'>首页</a></li>")
        self.query_dict.setlist(page_param, [self.previous_page])  # 上一页 url地址拼接
        page_list.append(f"<li><a href='?{self.query_dict.urlencode()}'><<</a></li>")
        start_page = max(1, page - 5)
        end_page = min(self.total_page, page + 5)
        for i in range(start_page, end_page + 1):
            # Add active class for current page
            active = "active" if i == page else ""
            self.query_dict.setlist(page_param, [i])  # 分页 url地址拼接
            page_list.append(f"<li class='{active}'><a href='?{self.query_dict.urlencode()}'>{i}</a></li>")

        self.query_dict.setlist(page_param, [self.total_page])  # 尾页 url地址拼接
        page_list.append(f"<li><a href='?{self.query_dict.urlencode()}'>共{self.total_page}页</a></li>")
        self.query_dict.setlist(page_param, [self.next_page])  # 下一页 url地址拼接
        page_list.append(f"<li><a href='?{self.query_dict.urlencode()}'>></a></li>")
        self.query_dict.setlist(page_param, [self.total_page])  # 尾页 url地址拼接
        page_list.append(f"<li><a href='?{self.query_dict.urlencode()}'>尾页</a></li>")

        html_turn_per_page = f"""
        <li>
                    <div class="input-group" style="float: left; width: 140px;">
                        <form method="get" class="input-group">
                            <input type="text" class="form-control" name="page" placeholder="跳转页码">
                            <span class="input-group-btn">
                                <button class="btn btn-default" type="submit">跳转</button>
                            </span>
                        </form>
                    </div>
                </li>

                <li>
                    <div class="input-group" style="float: left; width: 140px;">
                        <form method="get" class="input-group">
                            <input type="text" class="form-control" name="per_page" placeholder="每页条数">
                            <span class="input-group-btn">
                                <button class="btn btn-default" type="submit">设置</button>
                            </span>
                        </form>
                    </div>
                </li>
        """
        page_list.append(html_turn_per_page)
        self.page_list_str = mark_safe("".join(page_list))  # 分页导航链接字符串

        # Get base queryset with search support
        search_text = request.GET.get('search_text', '')
        field_contains_dict = {field_contains: search_text}

        if search_text:
            self.queryset = (
                database_total.objects.filter(**field_contains_dict).order_by('-id')
            )[self.offset:self.offset + self.per_page]
        else:
            self.queryset = database_total.objects.all().order_by('-id')[self.offset:self.offset + self.per_page]

