import re
from QQLoginTool.QQtool import OAuthQQ
from django import http
from django.conf import settings
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.views import View
import logging
from django_redis import get_redis_connection
from .utils import generate_access_token, check_access_token
from .models import OAuthQQUser
from djangoProject.utils.response_code import RETCODE

# Create your views here.

# 创建日志输出器
from users.models import User

logger = logging.getLogger('django')


class QQAuthURLView(View):
    """
        提供QQ登录扫码页面
        https://graph.qq.com/oauth2.0/authorize?response_type=code&client_id=xxx&redirect_uri=xxx&state=xxx

    """

    def get(self, request):
        # next表示从哪个页面进入到的登录页面，将来登录成功后，就自动回到那个页面
        next = request.GET.get('next')

        # 创建工具对象
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI, state=next)

        # 生成QQ登录扫码链接地址
        login_url = oauth.get_qq_url()

        # 响应
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'login_url': login_url})


class QQAuthUserView(View):
    """用户扫码登录的回调处理"""

    def get(self, request):
        """Oauth2.0认证"""
        # 使用code向QQ服务器请求access_token
        # 使用access_token向QQ服务器请求openid

        code = request.GET.get('code')
        if not code:
            return http.HttpResponseForbidden('缺少code')

        # 创建工具对象
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI)

        try:
            # 使用code向QQ服务器请求access_token
            access_token = oauth.get_access_token(code)

            # 使用access_token向QQ服务器请求openid
            openid = oauth.get_open_id(access_token)

        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('OAuth2.0认证失败')

        try:
            oauth_user = OAuthQQUser.objects.get(openid=openid)
        except Exception as e:
            # 如果openid没绑定美多商城用户
            # 为了能够在后续的绑定用户操作中前端可以使用openid，在这里将openid签名后响应给前端。
            # openid属于用户的隐私信息，所以需要将openid签名处理，避免暴露。

            access_token_openid = generate_access_token(openid)
            context = {
                'access_token_openid': access_token_openid
            }
            return render(request, 'oauth_callback.html', context)

        else:
            # 如果openid已绑定美多商城用户，直接生成状态保持信息，登录成功，并重定向到首页。
            qq_user = oauth_user.user
            # 登录
            login(request, qq_user)

            # 响应结果
            next = request.GET.get('state')
            response = redirect(next)

            # 登录时用户名写入到cookie，有效期1天
            response.set_cookie('username', qq_user.username, max_age=3600 * 24 * 1)

            return response

    def post(self, request):
        """美多商城用户绑定到openid"""

        # 接收参数
        mobile = request.POST.get('mobile')
        pwd = request.POST.get('password')
        sms_code_client = request.POST.get('sms_code')
        access_token = request.POST.get('access_token')

        # 判断参数是否齐全
        if not all([mobile, pwd, sms_code_client]):
            return http.HttpResponseForbidden('缺少必传参数')

        # 判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('请输入正确的手机号码')

        # 判断密码是否合格
        if not re.match(r'^[0-9A-Za-z]{8,20}$', pwd):
            return http.HttpResponseForbidden('请输入8-20位的密码')

        # 判断短信验证码是否一致
        redis_conn = get_redis_connection('verify_code')
        sms_code_server = redis_conn.get('sms_%s' % mobile)
        if sms_code_server is None:
            return render(request, 'oauth_callback.html', {'sms_code_errmsg': '无效的短信验证码'})
        if sms_code_client != sms_code_server.decode():
            return render(request, 'oauth_callback.html', {'sms_code_errmsg': '输入短信验证码有误'})

        # 判断openid是否有效：错误提示放在sms_code_errmsg位置
        openid = check_access_token(access_token)
        if not openid:
            return render(request, 'oauth_callback.html', {'openid_errmsg': '无效的openid'})

        # 保存注册数据
        try:
            user = User.objects.get(mobile=mobile)
        except Exception:
            # 用户不存在,新建用户
            user = User.objects.create_user(username=mobile, password=pwd, mobile=mobile)
        else:
            # 如果用户存在，检查用户密码
            if not user.check_password(pwd):
                return render(request, 'oauth_callback.html', {'account_errmsg': '用户名或密码错误'})

        # 将用户绑定到openid
        try:
            OAuthQQUser.objects.create(openid=openid, user=user)
        except Exception:
            return render(request, 'oauth_callback.html', {'qq_login_errmsg': 'QQ登录失败'})

        # 实现状态保持
        login(request, user)

        # 响应绑定结果
        next = request.GET.get('state')
        response = redirect(next)

        # 登录时用户名写入到cookie，有效期1天
        response.set_cookie('username', user.username, max_age=3600 * 24 * 11)

        return response
