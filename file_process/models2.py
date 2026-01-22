from django.db import models


class ErrorCorrection(models.Model):
    error_word = models.CharField(max_length=100, unique=True, verbose_name="错误词语")
    correct_word = models.CharField(max_length=100, verbose_name="正确词语")

    def __str__(self):
        return f"{self.error_word} -> {self.correct_word}"


class departments(models.Model):
    full_name = models.CharField(max_length=100, verbose_name="部门名称")
    short_name = models.CharField(max_length=100, verbose_name="部门简称")

    def __str__(self):
        return self.full_name


class employees(models.Model):
    name = models.CharField(max_length=100, verbose_name="员工姓名")
    gender_choices = [
        (1, '男'),
        (2, '女'),
    ]
    gender = models.CharField(max_length=10, verbose_name="员工性别", choices=gender_choices)
    age = models.IntegerField(verbose_name="员工年龄")
    account = models.CharField(max_length=10, verbose_name="员工账号", default="0")
    create_time = models.DateTimeField(verbose_name="创建时间")
    department = models.ForeignKey(to=departments, to_field="id", verbose_name="部门", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.create_time})"


class lianghao(models.Model):
    # 靓号-手机号
    mobile = models.CharField(max_length=11, verbose_name="手机号")
    price = models.IntegerField(verbose_name="价格")

    level_choices = (
        (1, '一级'),
        (2, '二级'),
        (3, '三级'),
    )
    level = models.SmallIntegerField(verbose_name="等级", choices=level_choices)

    status_choices = (
        (1, '未占用'),
        (2, '已占用'),
    )
    status = models.SmallIntegerField(
        verbose_name="状态",
        choices=status_choices,
        default=1,  # Added default value to resolve migration error
    )

    def save(self, *args, **kwargs):
        # Convert empty string to default value if present
        if self.status == '':
            self.status = self._meta.get_field('status').default
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.mobile}"
