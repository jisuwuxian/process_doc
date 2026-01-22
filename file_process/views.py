# Create your views here.
from django.shortcuts import render, redirect
from process.models import ErrorCorrection, departments, employees, lianghao, Admin_user
from process.utils import extract_and_correct
from django import forms
from process.tools.pagination import Pagination
import copy
from django.http.request import QueryDict
import datetime
from process.tools.bootstrapmodelform import BootStrapModelForm, BootStrapForm
from process.tools.encrypt import md5


class employee_form(BootStrapModelForm):
    class Meta:
        model = employees
        fields = '__all__'
        # widgets = {
        #     'gender': forms.Select(),        # }

# 管理员用户添加表单
class admin_user_form(BootStrapModelForm):
    confirm_password = forms.CharField(
        label='确认密码',
        widget=forms.PasswordInput(render_value=True)
    )

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 6:
            raise forms.ValidationError('密码长度必须大于等于6位')
        return md5(password)

    def clean_confirm_password(self):
        """验证确认密码是否与密码一致"""
        # 获取用户输入的确认密码，表单验证通过后自动生成的字典对象，form.cleaned_data存储着 “经过清洗、验证合法” 的表单数据
        confirm_password = md5(self.cleaned_data.get('confirm_password'))
        # 获取用户输入的密码，表单验证通过后自动生成的字典对象，存储着 “经过清洗、验证合法” 的表单数据
        password = self.cleaned_data.get('password')
        # 检查两次输入的密码是否一致
        if confirm_password != password:
            # 如果两次密码不一致，抛出验证错误
            raise forms.ValidationError('两次密码不一致')
        # 验证通过，返回确认密码
        return confirm_password

    class Meta:
        model = Admin_user
        fields = '__all__'
        widgets = {
            'password': forms.PasswordInput(render_value=True),
        }

# 管理员用户编辑表单
class admin_edit_form(BootStrapModelForm):
    confirm_password = forms.CharField(
        label='确认密码',
        widget=forms.PasswordInput(render_value=True)
    )

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 6:
            raise forms.ValidationError('密码长度必须大于等于6位')
        md5_pwd = md5(password)
        if Admin_user.objects.filter(id=self.instance.pk, password=md5_pwd).exists():
            raise forms.ValidationError('不能使用与当前密码相同的密码')

        return md5_pwd

    def clean_confirm_password(self):
        """验证确认密码是否与密码一致"""
        # 获取用户输入的确认密码，表单验证通过后自动生成的字典对象，form.cleaned_data存储着 “经过清洗、验证合法” 的表单数据
        confirm_password = md5(self.cleaned_data.get('confirm_password'))
        # 获取用户输入的密码，表单验证通过后自动生成的字典对象，存储着 “经过清洗、验证合法” 的表单数据
        password = self.cleaned_data.get('password')
        # 检查两次输入的密码是否一致
        if confirm_password != password:
            # 如果两次密码不一致，抛出验证错误
            raise forms.ValidationError('两次密码不一致')
        # 验证通过，返回确认密码
        return confirm_password

    class Meta:
        model = Admin_user
        fields = '__all__'
        widgets = {
            'password': forms.PasswordInput(render_value=True),
        }


# 靓号添加表单
class lianghao_form(BootStrapModelForm):
    # 手机号验证 正则表达式 方法1
    # mobile = forms.CharField(
    #     label='手机号',
    #     validators=[RegexValidator(r'^1[3-9]\d{9}$', '请输入正确的手机号')],
    #     error_messages={'invalid': '请输入正确的手机号'}
    # )

    class Meta:
        model = lianghao
        fields = '__all__'


    # 手机号验证 方法2
    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        if lianghao.objects.filter(mobile=mobile).exists():
            raise forms.ValidationError('手机号已存在')
        if len(mobile) < 11:
            raise forms.ValidationError('手机号长度必须为11位')
        return mobile


# 靓号编辑表单
class lianghao_edit_form(BootStrapModelForm):

    mobile = forms.CharField(disabled=True, label='手机号')

    class Meta:
        model = lianghao
        fields = ['mobile', 'price', 'level', 'status']


# 登录表单
class login_form(BootStrapForm):
    username = forms.CharField(label='用户名', widget=forms.TextInput(attrs={'placeholder': '请输入用户名'}))
    password = forms.CharField(label='密码', widget=forms.PasswordInput(render_value=True, attrs={'placeholder': '请输入密码'}))

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 6:
            raise forms.ValidationError('密码长度必须大于等于6位')
        return md5(password)


def index(request):
    # 首页

    result = {"title": "", "number": "", "unit": ""}
    raw_input = ""
    if request.method == "POST":
        raw_input = request.POST.get("raw_text", "")
        if raw_input:
            result = extract_and_correct(raw_input)

    # 读取剪切板的内容
    clipboard_content = ""
    try:
        import pyperclip
        clipboard_content = pyperclip.paste()
    except:
        # 如果无法读取剪切板，保持为空
        clipboard_content = ""

    return render(request, 'index.html', {'result': result, 'raw_input': raw_input, 'clipboard_content': clipboard_content})
    # return HttpResponse("Hello, world. You're at the process index.")


def add_sample(request):
    # 添加样本

    if request.method == "POST":
        err = request.POST.get("error_word")
        cor = request.POST.get("correct_word")
        if err and cor:
            ErrorCorrection.objects.update_or_create(error_word=err, defaults={'correct_word': cor})

        full_text = request.POST.get("full_name")
        short_text = request.POST.get("short_name")
        if full_text and short_text:
            departments.objects.update_or_create(full_name=full_text, defaults={'short_name': short_text})
        return redirect('add_sample')

    samples = ErrorCorrection.objects.all().order_by('-id')
    units = departments.objects.all().order_by('-id')
    return render(request, 'add_sample.html', {'samples': samples, 'units': units})


def process_doc(request):
    # 处理文档

    result = {"title": "", "number": "", "unit": ""}
    raw_input = ""

    if request.method == "POST":
        raw_input = request.POST.get("raw_text", "")
        if raw_input:
            result = extract_and_correct(raw_input)

    return render(request, 'process_doc.html', {'result': result, 'raw_input': raw_input})
    # return HttpResponse("Hello, world. You're at the process index.")


# def department(request):
#     # 读取部门信息
#     units = departments.objects.all().order_by('-id')
#     if request.method == "POST":
#         full_text = request.POST.get("full_name")
#         short_text = request.POST.get("short_name")
#         if full_text and short_text:
#             departments.objects.update_or_create(full_name=full_text, defaults={'short_name': short_text})
#         return redirect('department')
#
#     return render(request, 'department.html', {'units': units})
def department(request):
    # 显示部门列表

    per_page = int(request.GET.get('per_page', 10))
    department_list = Pagination(request, departments, per_page=per_page)

    # 读取部门信息
    units = departments.objects.all().order_by('-id')
    if request.method == "POST":
        full_text = request.POST.get("full_name")
        short_text = request.POST.get("short_name")
        if full_text and short_text:
            departments.objects.update_or_create(full_name=full_text, defaults={'short_name': short_text})
        return redirect('department')

    return render(request, 'department.html', {
        'units': department_list.queryset, 'page_list_str': department_list.page_list_str
        })


def department_add(request):

    # 添加部门

    if request.method == "POST":

        full_text = request.POST.get("full_name")
        short_text = request.POST.get("short_name")
        if full_text and short_text:
            departments.objects.update_or_create(full_name=full_text, defaults={'short_name': short_text})
        return redirect('/department')

    return render(request, 'department_add.html')


def department_del(request):

    # 删除部门

    if request.method == "GET":
        nid = request.GET.get("nid")
        if nid:
            departments.objects.filter(id=nid).delete()
        return redirect('/department')


def department_edit(request, nid):
    # 编辑部门信息

    unit = departments.objects.filter(id=nid).first()
    if not unit:
        return redirect('/department')

    if request.method == 'POST':
        unit.full_name = request.POST.get("full_name")
        unit.short_name = request.POST.get("short_name")
        departments.objects.filter(id=nid).update(full_name=unit.full_name, short_name=unit.short_name)
        return redirect('/department')

    return render(request, 'department_edit.html', {'unit': unit})


def employee(request):
    # 显示员工列表

    # for i in range(300):  # 新增300条员工数据
    #     employees.objects.update_or_create(name=f"员工{i}", defaults={'gender': 1, 'age': 20, 'account': f"emp{i}", 'create_time': datetime.datetime.now(), 'department_id': 110})
    per_page = int(request.GET.get("per_page", 10))  # 每页显示条数

    employee_list = Pagination(request, employees, per_page=per_page)

    # 读取员工信息
    employees_list = employee_list.queryset
    # for emp in employees_list:
    #     print(emp.name, emp.gender, emp.get_gender_display(), emp.age, emp.account, emp.create_time, emp.create_time.strftime("%Y-%m-%d"), emp.department.short_name)
    return render(request, 'employee.html', {
        'employees': employees_list, 'page_list_str': employee_list.page_list_str
        })


def employee_add(request):
    # 添加员工

    # if request.method == "POST":
    #     name = request.POST.get("emp_name")
    #     gender = request.POST.get("emp_gender")
    #     # Fixed: Use the choices directly instead of calling undefined function
    #     gender_choices = dict(employees._meta.get_field('gender').choices)
    #     gender_display = gender_choices.get(int(gender), gender)  # Fallback to gender value if not found
    #     age = request.POST.get("emp_age")
    #     account = request.POST.get("emp_account")
    #     create_time = request.POST.get("emp_create_time")
    #     if create_time:
    #         create_time = datetime.datetime.strptime(create_time, "%Y-%m-%d")
    #     department_id = request.POST.get("emp_department")
    #     print(name, gender, gender_display, age, account, create_time, department_id)
    #     if name and gender and age and account and department_id:
    #         employees.objects.update_or_create(name=name, defaults={'gender': gender_display, 'age': age, 'account': account, 'create_time': create_time, 'department_id': department_id})
    #     return redirect('/employee')
    #
    # units = departments.objects.all().order_by('-id')
    # department = departments.objects.all().order_by('-id')
    # return render(request, 'employee_add.html', {'units': units, 'department': department})
    if request.method == "GET":
        form = employee_form()
        return render(request, 'employee_add.html', {'form': form})
    if request.method == "POST":
        form = employee_form(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('/employee')
        else:
            return render(request, 'employee_add.html', {'form': form})

def employee_model_edit(request, nid):
    # 编辑员工（modelform版本）

    # 根据ID获取员工对象
    emp = employees.objects.filter(id=nid).first()
    # 如果员工不存在，重定向到员工列表页面
    if not emp:
        return redirect('/employee')
    # 处理POST请求（表单提交）
    if request.method == "POST":
        # 使用提交的数据和员工实例创建表单
        form = employee_form(request.POST, instance=emp)
        # 检查表单数据是否有效
        if form.is_valid():
            # 保存表单数据（更新员工信息）
            form.save()
            # 保存成功后重定向到员工列表页面
            return redirect('/employee')
    # 处理GET请求（显示编辑表单）
    else:
        # 使用员工实例初始化表单（显示当前数据）
        form = employee_form(instance=emp)
    # 渲染员工编辑页面并传递表单数据
    return render(request, 'employee_model_edit.html', {'form': form})


def employee_del(request):
    # 删除员工

    if request.method == "GET":
        nid = request.GET.get("nid")
        if nid:
            employees.objects.filter(id=nid).delete()
        return redirect('/employee')


def lianghao_list(request):
    # 显示靓号列表

    per_page = int(request.GET.get("per_page", 10))  # 每页显示条数
    page_ination = Pagination(request, lianghao, field_contains='mobile__contains', per_page=per_page)
    return render(request, 'lianghao_list.html', {
        'form': page_ination.queryset,
        'page_list_str': page_ination.page_list_str
    })
# def lianghao_list(request):
#     # for i in range(300):
#     #     lianghao.objects.create(mobile=f"1380000{i:03d}", price=100, level=1, status=1)
#     # 搜索靓号 方法1
#     # search_text = request.GET.get("search_text")
#     # print(search_text)
#     # if search_text:
#     #     form = lianghao.objects.filter(mobile__contains=search_text).order_by('-id')
#     #     print(form)
#     # else:
#     #     form = lianghao.objects.all().order_by('-id')
#     # # form = lianghao_form(request.GET, instance=lianghao_list_all)
#     # return render(request, 'lianghao_list.html', {'form': form})
#
#     # 分页功能
#     # 获取总记录数，用于分页计算
#     total_count = lianghao.objects.all().count()
#     # 每页显示10条记录
#     per_page = 10
#
#     # Handle potential invalid page parameter values
#     page_param = request.GET.get("page", "1")  # 获取分页参数，默认值为1
#
#     try:
#         page = int(page_param)
#         if page > (total_count + per_page - 1) // per_page:
#             page = (total_count + per_page - 1) // per_page
#         if page < 1:
#             page = 1
#
#     except ValueError:
#         page = 1
#     if not page:
#         page = 1
#
#     # 计算偏移量，用于分页查询
#     offset = (page - 1) * per_page
#     # 计算总页数，用于分页导航 方法1
#     # total_page, remainder = divmod(total_count, per_page) # 计算总页数，remainder为余数，divmod()函数返回商和余数
#     # if remainder > 0:
#     #     total_page = total_page + 1
#     # 计算总页数，用于分页导航 方法2
#     total_page = (total_count + per_page - 1) // per_page
#     # 处理分页参数，确保页码为非负整数
#     page = max(1, page)
#     page = min(page, total_page)  # 确保页码不超过总页数
#     if page > total_page:
#         page = total_page
#     previous_page = page - 1 if page > 1 else 1  # 上一页，确保不小于1
#     next_page = page + 1 if page < total_page else total_page  # 下一页，确保不大于总页数
#
#     # 拼接分页导航链接
#     page_list = []   #分页导航链接列表
#     page_list.append(f"<li><a href='?page=1' name='page' value=1>首页</a></li>"
#                      f"<li><a href='?page={previous_page}' name='page' value='{previous_page}'><<</a></li>")
#     start_page = max(1, page - 5)
#     end_page = min(total_page, page + 5)
#     for i in range(start_page, end_page + 1):
#         page_list.append(f"<li><a href='?page={i}' name='page' value='{i}'>{i}</a></li>")
#
#     page_list.append(f"<li><a href='?page={next_page}' name='page' value='{next_page}'>>></a></li>"
#                      f"<li><a href='?page={total_page}' name='page' value={total_page}>尾页</a></li>")
#     page_list_str = mark_safe("".join(page_list))
#
#     # 搜索靓号 方法2
#     # 处理靓号搜索功能
#     # 初始化搜索条件字典，用于构建查询过滤条件
#     search_dictionary = {}
#     # 从GET请求参数中获取搜索文本，默认为空字符串
#     search_text = request.GET.get("search_text", "")
#
#     # 如果存在搜索文本，则构建搜索条件并执行过滤查询
#     if search_text:
#         # 添加手机号包含搜索文本的过滤条件（mobile__contains为Django ORM的模糊查询）
#         search_dictionary["mobile__contains"] = search_text
#         # 使用构建的搜索条件过滤靓号记录，并按ID降序排序
#         form = lianghao.objects.filter(**search_dictionary).order_by("-id")
#         # 将过滤结果传递给模板并渲染页面
#         return render(request, "lianghao_list.html", {"form": form, 'page_list': page_list_str})
#
#     # 如果没有搜索文本，则获取所有靓号记录并按ID降序排序
#     form = lianghao.objects.all().order_by('-id')[offset:offset+per_page]
#
#     # 将所有记录传递给模板并渲染页面
#     return render(request, 'lianghao_list.html', {'form': form, 'page_list_str': page_list_str})


def lianghao_edit(request, nid):
    # 编辑靓号信息

    unit = lianghao.objects.filter(id=nid).first()
    if not unit:
        return redirect('/lianghao_list')
    if request.method == "GET":
        form = lianghao_edit_form(instance=unit)
        return render(request, 'lianghao_edit.html', {'form': form})

    form = lianghao_edit_form(request.POST, instance=unit)
    if form.is_valid():
        form.save()
        return redirect('/lianghao_list')
    else:
        form = lianghao_edit_form(instance=unit)
        return render(request, 'lianghao_edit.html', {'form': form})


def lianghao_add(request):
    # 添加靓号

    # if request.method == "POST":
    #     mobile = request.POST.get("mobile")
    #     price = request.POST.get("price")
    #     level = request.POST.get("level")
    #     status = request.POST.get("status")
    #     if mobile and price and level and status:
    #         lianghao.objects.update_or_create(mobile=mobile, defaults={'price': price, 'level': level, 'status': status})
    #     return redirect('/lianghao_list')
    if request.method == "GET":
        form = lianghao_form()
        return render(request, 'lianghao_add.html', {'form': form})
    if request.method == "POST":
        form = lianghao_form(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('/lianghao_list')
        else:
            return render(request, 'lianghao_add.html', {'form': form})


def lianghao_del(request):

    # 从GET请求参数中获取要删除的靓号ID
    if request.method == "GET":
        nid = request.GET.get("nid")
        if nid:
            lianghao.objects.filter(id=nid).delete()
        return redirect('/lianghao_list')


# 管理员增删改查
def admin_user(request):
    # 管理员用户列表

    # 验证用户是否登录
    # if 'admin_user_id' not in request.session:
    #     return redirect('/login')
    # 从session中获取管理员用户ID
    # admin_user_id = request.session.get('admin_user_id')
    # if not admin_user_id:
    #     return redirect('/login')
    per_page = int(request.GET.get("per_page", 10))  # 每页显示条数
    page_ination = Pagination(request, Admin_user, field_contains='username__contains', per_page=per_page)
    return render(request, 'admin_user.html', {
        'form': page_ination.queryset,
        'page_list_str': page_ination.page_list_str
    })


def admin_user_add(request):
    # 添加管理员用户

    if request.method == "GET":
        form = admin_user_form()
        return render(request, 'admin_user_add.html', {'form': form})
    if request.method == "POST":
        form = admin_user_form(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/admin_user')
        else:
            return render(request, 'admin_user_add.html', {'form': form})


def admin_user_edit(request, nid):
    # 编辑管理员用户信息

    unit = Admin_user.objects.filter(id=nid).first()
    if not unit:
        return redirect('/admin_user')
    if request.method == "GET":
        form = admin_edit_form(instance=unit)
        return render(request, 'admin_user_edit.html', {'form': form})
    if request.method == "POST":
        form = admin_edit_form(request.POST, instance=unit)
        if form.is_valid():
            form.save()
            return redirect('/admin_user')
        else:
            return render(request, 'admin_user_edit.html', {'form': form})


def admin_user_del(request):
    # 删除管理员用户

    if request.method == "GET":
        nid = request.GET.get("nid")
        if nid:
            Admin_user.objects.filter(id=nid).delete()
        return redirect('/admin_user')


def login(request):
    """登录"""
    if request.method == "GET":
        form = login_form()
        return render(request, 'login.html', {'form': form})

    form = login_form(data=request.POST)
    if form.is_valid():
        # 验证成功，登录
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        admin_user = Admin_user.objects.filter(username=username, password=password).first()
        if admin_user:
            # 登录成功，将用户ID存储在session中
            request.session['admin_user_id'] = admin_user.id
            request.session['admin_user_name'] = admin_user.username
            return redirect('http://localhost:8000/')
        else:
            # 登录失败，返回登录页面
            form.add_error('username', '用户名或密码错误')
            return render(request, 'login.html', {'form': form})
    else:
        # 验证失败，返回登录页面
        return render(request, 'login.html', {'form': form})


def logout(request):
    """注销"""
    # 清除session中的用户ID
    request.session.pop('admin_user_id', None)
    return redirect('/login')
