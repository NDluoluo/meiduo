import re
from django.views import View
from django_redis import get_redis_connection

from djangoProject.utils.response_code import RETCODE
from django import http
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import User

# Create your views here.



class RegisterView(View):
    """用户注册"""

    def get(self, request):
        """
            提供注册界面
            :param request: 请求对象
            :return: 注册界面
        """

        return render(request, 'register.html')

    def post(self, request):
        """
        实现用户注册
        :param request: 请求对象
        :return: 注册结果
        """
        # 获取表单参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        allow = request.POST.get('allow')
        sms_code_client = request.POST.get('sms_code')

        # 校验参数

        # 判断参数是否齐全
        if not all([username, password, password2, mobile, allow]):
            return http.HttpResponseForbidden('缺少必传参数！')

        # 判断用户名是否是5-20个字符
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden('请输入5-20个字符的用户名')

        # 判断密码是否是8-20个数字
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('请输入8-20位的密码')

        # 判断两次密码是否一致
        if password != password2:
            return http.HttpResponseForbidden('两次输入的密码不一致')

        # 判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('请输入正确的手机号码')

        # 判断是否勾选用户协议
        if allow != 'on':
            return http.HttpResponseForbidden('请勾选用户协议')


        redis_conn = get_redis_connection('verify_code')
        sms_code_server = redis_conn.get('sms_%s' % mobile)
        if sms_code_server is None:
            return render(request, 'register.html', {'sms_code_errmsg': '无效的短信验证码'})
        if sms_code_client != sms_code_server.decode():
            return render(request, 'register.html', {'sms_code_errmsg': '输入短信验证码有误'})

        # 保存注册数据
        try:
            user = User.objects.create_user(
                username=username,
                password=password,
                mobile=mobile
            )
        except Exception:
            return render(
                request,
                'register.html',
                {'register_errmsg': '注册失败！'}
            )

        # 登入用户，实现状态保持
        login(request, user)
        return redirect(reverse('contents:index'))


class UsernameCountView(View):
    """判断用户名是否重复注册"""

    def get(self, request, username):
        """
              :param request: 请求对象
              :param username: 用户名
              :return: JSON
        """
        count = User.objects.filter(username=username).count()
        # 返回用户的数量
        return http.JsonResponse({
            'code': RETCODE.OK,
            'errmsg': 'OK',
            'count': count
        })


class MobileCountView(View):
    """判断手机号是否重复注册"""


    def get(self, request, mobile):
        """
            :param request: 请求对象
            :param mobile: 手机号
            :return: JSON
         """
        count = User.objects.filter(mobile=mobile).count()
        return http.JsonResponse({
            'code': RETCODE.OK,
            'errmsg': 'OK',
            'count': count
        })
