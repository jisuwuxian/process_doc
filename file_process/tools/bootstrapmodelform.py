from django.shortcuts import render, redirect
from process.models import ErrorCorrection, departments, employees, lianghao
from process.utils import extract_and_correct
from django import forms
from process.tools.pagination import Pagination
import copy
from django.http.request import QueryDict
import datetime


# Bootstrap样式的ModelForm基类，自动为表单字段添加Bootstrap的form-control类和占位符
class BootStrapModelForm(forms.ModelForm):
    # 初始化方法，为表单字段添加Bootstrap样式属性
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 遍历所有表单字段，为其添加Bootstrap样式和占位符
        for name, field in self.fields.items():
            if field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['placeholder'] = field.label
            else:
                field.widget.attrs = {'class': 'form-control', 'placeholder': field.label}


class BootStrapForm(forms.Form):
    # 初始化方法，为表单字段添加Bootstrap样式属性
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 遍历所有表单字段，为其添加Bootstrap样式和占位符
        for name, field in self.fields.items():
            if field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['placeholder'] = field.label
            else:
                field.widget.attrs = {'class': 'form-control', 'placeholder': field.label}