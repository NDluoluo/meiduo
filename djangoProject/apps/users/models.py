from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import AbstractUser
from djangoProject.utils.models import BaseModel


class User(AbstractUser):
    """自定义用户模型类"""

    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')
    default_address = models.ForeignKey('Address', related_name='users', null=True, blank=True,
                                        on_delete=models.SET_NULL, verbose_name='默认地址')

    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


class Address(BaseModel):
    """用户地址"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name='用户')
    title = models.CharField(max_length=20, verbose_name='地址名称')
    receiver = models.CharField(max_length=20, verbose_name='收货人')
    province = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='province_addresses', verbose_name='省')
    city = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='city_addresses', verbose_name='市')
    district = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='district_addresses', verbose_name='区')
    place = models.CharField(max_length=50, verbose_name='地址')
    mobile = models.CharField(max_length=11, verbose_name='手机')
    tel = models.CharField(max_length=20, null=True, blank=True, default='', verbose_name='固定电话')
    email = models.CharField(max_length=30, null=True, blank=True, default='', verbose_name='电子邮箱')
    is_deleted = models.BooleanField(default=False, verbose_name='逻辑删除')

    class Meta:
        db_table = 'tb_address'
        verbose_name = '用户地址'
        verbose_name_plural = verbose_name
        ordering = ['-update_time']



# Address模型类中的外键指向areas/models里面的Area。指明外键时，可以使用应用名.模型类名来定义。
# ordering 表示在进行Address查询时，默认使用的排序方式。
# ordering = ['-update_time'] : 根据更新的时间倒叙。

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
