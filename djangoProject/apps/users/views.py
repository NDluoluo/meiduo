import json
import re
from . import constants
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django_redis import get_redis_connection
from djangoProject.utils.response_code import RETCODE
from django import http
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import User, Address
from djangoProject.utils.views import LoginRequiredJSONMixin
import logging
from djangoProject.celery_tasks.email.tasks import send_verify_email
from .utils import generate_verify_email_url, check_verify_email_token

# Create your views here.
# 创建日志输出器


logger = logging.getLogger('django')


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

        # 响应注册结果
        response = redirect(reverse('contents:index'))

        # 注册时用户名写入到cookie，有效期15天
        response.set_cookie('username', user.username, max_age=3600 * 24 * 1)

        return response


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


class LoginView(View):
    """用户名登录"""

    def get(self, request):
        """
        提供登录界面
        :param request: 请求对象
        :return: 登录界面
        """

        return render(request, 'login.html')

    def post(self, request):
        """
        实现登录逻辑
        :param request: 请求对象
        :return: 登录结果
        """
        # 接受参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        remembered = request.POST.get('remembered')

        # 校验参数
        # 判断参数是否齐全
        if not all([username, password]):
            return http.HttpResponseForbidden('缺少必传参数')

        # 判断用户名是否是5-20个字符
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden('请输入正确的用户名或手机号')

        # 判断密码是否是8-20个数字
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('密码最少8位，最长20位')

        # 认证登录用户账户是否正确
        user = authenticate(username=username, password=password)
        if user is None:
            return render(request, 'login.html', {'account_errmsg': '用户名或密码错误'})

        # 实现状态保持
        login(request, user)
        # 设置状态保持的周期
        if remembered != 'on':
            # 没有记住用户：浏览器会话结束就过期
            request.session.set_expiry(0)
        else:
            # 记住用户：None表示两周后过期
            request.session.set_expiry(None)

        # 响应登录结果
        # 由Django用户认证系统提供，搭配login_required装饰器使用。
        # 记录了用户未登录时访问的地址信息，可以帮助我们实现在用户登录成功后直接进入未登录时访问的地址。
        next = request.GET.get('next')
        if next:
            response = redirect(next)
        else:
            response = redirect(reverse('contents:index'))

        # 登录时用户名写入到cookie，有效期15天
        response.set_cookie('username', user.username, max_age=3600 * 24 * 1)

        return response


class LogoutView(View):
    """退出登录"""

    def get(self, request):
        """实现退出登录逻辑"""

        # 清理session
        logout(request)

        # 退出登录，重定向到登录页
        response = redirect(reverse('contents:index'))

        # 退出登录时清除cookie中的username
        response.delete_cookie('username')

        return response


class UserInfoView(LoginRequiredMixin, View):
    """用户中心"""

    # LoginRequiredMixin 类里面封装了判断用户是否登录的操作
    # Django用户认证系统提供了方法request.user.is_authenticated()
    # 来判断用户是否登录。
    # 如果通过登录验证则返回True。反之，返回False。
    # if request.user.is_authenticated:
    #     return render(request, 'user_center_info.html')
    # else:
    #     return redirect(reverse('users:login'))
    def get(self, request):
        """提供个人信息界面"""

        # django 用自己的用不认证系统  request 里面会携带user对象
        context = {
            'username': request.user.username,
            'mobile': request.user.mobile,
            'email': request.user.email,
            'email_active': request.user.email_active
        }

        return render(request, 'user_center_info.html', context=context)


class EmailView(LoginRequiredJSONMixin, View):
    """添加邮箱"""

    def put(self, request):
        """实现添加邮箱逻辑"""

        # 判断用户是否登录并返回JSON  LoginRequiredJSONMixin父类
        # 接受参数
        json_dict = json.loads(request.body.decode())
        email = json_dict.get('email')

        # 校验参数
        if not email:
            return http.HttpResponseForbidden('缺少必填参数!')

        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return http.HttpResponseForbidden('email格式不正确!')

        # 复制email 字段
        try:
            request.user.email = email
            # 保存用户数据(邮箱)
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '添加邮箱失败!'})

        # 异步发送验证邮件
        verify_url = generate_verify_email_url(request.user)
        send_verify_email.delay(email, verify_url)

        # 响应添加邮箱结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '添加邮箱成功'})


class VerifyEmailView(View):
    """验证邮箱"""

    def get(self, request):
        """实现邮箱验证逻辑"""

        # 接收参数
        token = request.GET.get('token')

        # 校验参数：判断token是否为空和过期，提取user
        if not token:
            return http.HttpResponseBadRequest('缺少token')

        # 没有这个用户的情况
        user = check_verify_email_token(token)
        if not user:
            return http.HttpResponseForbidden('无效的token')

        # 修改email_active的值为True
        try:
            user.email_active = True
            user.save()
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('激活邮件失败')

        # 返回邮箱验证结果
        return redirect(reverse('users:Info'))


class AddressView(LoginRequiredMixin, View):
    """用户收货地址"""

    def get(self, request):
        """提供收货地址界面"""
        # 获取用户地址列表
        login_user = request.user
        addresses = Address.objects.filter(user=login_user, is_deleted=False)

        address_dict_list = []
        for address in addresses:
            address_dict = {
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            }
            address_dict_list.append(address_dict)

        context = {
            'default_address_id': login_user.default_address_id,
            'addresses': address_dict_list,
        }

        return render(request, 'user_center_site.html', context)


class CreateAddressView(LoginRequiredJSONMixin, View):
    """新增地址"""

    def post(self, request):
        """实现新增地址逻辑"""

        # 判断是否超过地址上限：最多20个
        # Address.objects.filter(user=request.user).count()
        count = request.user.addresses.count()
        if count >= constants.USER_ADDRESS_COUNTS_LIMIT:
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '超过地址数量上限'})

        # 接受参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 参数
        if not all([receiver, province_id, city_id, district_id, place, mobile, tel, email]):
            return http.HttpResponseForbidden('缺少必传参数')

        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('参数mobile有误')

        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseForbidden('参数tel有误')

        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseForbidden('参数email有误')

        # 保存地址信息
        try:
            address = Address.objects.create(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )

            # 设置默认地址
            if not request.user.default_address:
                request.user.default_address = address
                request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({
                'code': RETCODE.DBERR,
                'errmsg': '新增地址失败'
            })

        # 新增地址成功，将新增的地址响应给前端实现局部刷新
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        # 响应保存结果
        return http.JsonResponse({
            'code': RETCODE.OK,
            'errmsg': '新增地址成功',
            'address': address_dict
        })



class UpdateDestroyAddressView(LoginRequiredJSONMixin, View):
    """修改和删除地址"""

    def put(self, request, address_id):
        """修改地址"""

        # 接收参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseForbidden('缺少必传参数')

        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('参数mobile有误')

        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseForbidden('参数tel有误')

        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseForbidden('邮箱格式不正确')

        # 判断地址是否存在,并更新地址信息
        try:
            Address.objects.filter(id=address_id).update(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({
                {'code': RETCODE.DBERR, 'errmsg': '更新地址失败'}
            })

        # 构造响应数据
        address = Address.objects.get(id=address_id)
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        # 响应更新地址结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '更新地址成功', 'address': address_dict})


    def delete(self, request, address_id):
        """删除地址"""

        try:
            # 查询要删除的地址
            address = Address.objects.get(id=address_id)

            # 将地址逻辑删除设置为True
            address.is_deleted = True
            address.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '删除地址失败'})

        # 响应删除地址结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '删除地址成功'})