from .views import RegisterView, UsernameCountView, MobileCountView
from django.urls import re_path, path

# user 子路由
urlpatterns = [
    # 注册路由
    path(r'register/', RegisterView.as_view(), name='register'),
    re_path(r'usernames/([a-zA-Z0-9_-]{5,20})/count/', UsernameCountView.as_view(), name='UsernameCount'),
    re_path(r'mobiles/(1[3-9]\d{9})/count/', MobileCountView.as_view(), name='MobileCount'),
]
