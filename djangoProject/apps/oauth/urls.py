from django.urls import path
from .views import QQAuthURLView, QQAuthUserView

# oauth 子路由
urlpatterns = [
    # 提供QQ登录扫码页面
    path(r'qq/login/', QQAuthURLView.as_view(), name='QQAuthURL'),
    # 处理QQ登录回调
    path(r'oauth_callback/', QQAuthUserView.as_view(), name='QQAuthUser'),
]
