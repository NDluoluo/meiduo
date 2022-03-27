from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """自定义用户模型类"""

    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')

    class Meta:

        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


'''
    Django自带用户认证系统，核心就是User对象，并封装了一系列可用的方法和属性
    Django用户认证系统包含了一系列对用户的操作，比如：模型类，认证，权限，分组，密码处理等
    Django用户认证系统中的用户模型类可以自定义，继承自AbstractUser
    User对象基本属性
        创建用户(注册用户)必选： username、password
        创建用户(注册用户)可选：email、first_name、last_name、last_login、date_joined、is_active 、is_staff、is_superuse
        判断用户是否通过认证(是否登录)：is_authenticated
    创建用户(注册用户)的方法
        user = User.objects.create_user(username, email, password, **extra_fields)
'''