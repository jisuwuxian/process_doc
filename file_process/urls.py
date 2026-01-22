"""
URL configuration for file_process project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
# Import views from the parent directory (where models.py is located)
from process import views

urlpatterns = [
    path('', views.index, name='index'),
    # Fix redundant "views." reference
    path('process_doc/', views.process_doc, name='process_doc'),
    path('add_sample/', views.add_sample, name='add_sample'),
    path('department/', views.department, name='process_excel'),
    path('department_add/', views.department_add, name='department_add'),
    path('department_del/', views.department_del, name='department_del'),
    path('department/<int:nid>/edit/', views.department_edit, name='department_edit'),
    # 员工管理
    path('employee/', views.employee, name='employee'),
    path('employee_add/', views.employee_add, name='employee_add'),
    path('employee/<int:nid>/edit/', views.employee_model_edit, name='employee_model_edit'),
    path('employee_del/', views.employee_del, name='employee_del'),
    # path('employee/<int:nid>/edit/', views.employee_edit, name='employee_edit'),
    # 靓号管理
    path('lianghao_list/', views.lianghao_list, name='lianghao_list'),
    path('lianghao_add/', views.lianghao_add, name='lianghao_add'),
    path('lianghao/<int:nid>/edit/', views.lianghao_edit, name='lianghao_edit'),
    path('lianghao_del/', views.lianghao_del, name='lianghao_del'),
    # 管理员用户管理
    path('admin_user/', views.admin_user, name='admin_user'),
    path('admin_user_add/', views.admin_user_add, name='admin_user_add'),
    path('admin_user/<int:nid>/edit/', views.admin_user_edit, name='admin_user_edit'),
    path('admin_user_del/', views.admin_user_del, name='admin_user_del'),
    # 登录注册
    path('login', views.login, name='login'),
    # path('register/', views.register, name='register'),
    path('logout', views.logout, name='logout'),
]

