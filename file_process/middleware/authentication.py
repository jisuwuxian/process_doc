from django.urls import reverse  # 反向解析 URL 的核心导入，作用是通过「URL 名称」动态生成对应的 URL 路径，而非硬编码字符串。
from django.shortcuts import HttpResponse, render, redirect # 导入 redirect 函数，用于重定向用户到其他页面。


def process_request(request):
    # 允许直接访问的地址
    login_url = reverse('login')  # 动态获取登录页面的 URL，避免硬编码。
    # 允许直接访问登录页面、静态文件和媒体文件
    if (request.path_info == login_url or
        request.path_info.startswith('/static/') or
        request.path_info.startswith('/media/')):
        return

    # 读取当前访问用户的session信息,
    info_dict = request.session.get('admin_user_id')
    if info_dict:
        return
    return redirect(login_url)  # 未登录用户，重定向到登录页面。


class AuthMiddleware:  # 自定义中间件类，用于处理用户认证和授权。
    def __init__(self, get_response):  # 初始化中间件，接收下一个中间件或视图函数。
        self.get_response = get_response

    def __call__(self, request):  # 定义中间件的调用逻辑，处理每个请求。
        response = process_request(request)  # 调用自定义方法处理请求，返回响应对象或 None。
        if response:
            return response
        return self.get_response(request)




