from django.contrib.auth.decorators import login_required
from .views import RegisterView, UsernameCountView, MobileCountView,\
    LoginView, LogoutView, UserInfoView, EmailView, VerifyEmailView, \
    AddressView, CreateAddressView, UpdateDestroyAddressView

from django.urls import re_path, path
# login_required 、 login_required(LogoutView.as_view()) 装饰器用来判断用户 是否登录
# login_required 只能装饰函数视图、但是我们的类视图都被 as_view（）方法转换为了函数视图

# user 子路由
urlpatterns = [
    # 注册路由
    path(r'register/', RegisterView.as_view(), name='register'),
    re_path(r'usernames/([a-zA-Z0-9_-]{5,20})/count/', UsernameCountView.as_view(), name='UsernameCount'),
    re_path(r'mobiles/(1[3-9]\d{9})/count/', MobileCountView.as_view(), name='MobileCount'),
    re_path(r'login/', LoginView.as_view(), name='Login'),
    re_path(r'logout/', LogoutView.as_view(), name='Logout'),
    re_path(r'info/', UserInfoView.as_view(), name='Info'),
    re_path(r'emails/', EmailView.as_view(), name='Email'),
    re_path(r'emails/verification/', VerifyEmailView.as_view(), name='VerifyEmail'),
    re_path(r'addresses/', AddressView.as_view(), name='Address'),
    re_path(r'addresses/create/', CreateAddressView.as_view(), name='CreateAddress'),
    re_path(r'addresses/(\d+)/', UpdateDestroyAddressView.as_view(), name='UpdateDestroyAddress'),
]
