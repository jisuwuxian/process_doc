import hashlib
from django.conf import settings


def md5(password):
    # 对密码进行加密，使用SECRET_KEY作为盐值
    # 创建MD5哈希对象，并使用Django的SECRET_KEY作为盐值进行初始化
    obj = hashlib.md5(settings.SECRET_KEY.encode('utf-8'))
    # 更新哈希对象，将密码字符串编码为UTF-8后添加到哈希计算中
    obj.update(password.encode('utf-8'))
    # 返回计算得到的16进制哈希值
    return obj.hexdigest()
