from .views import ImageCodeView, SMSCodeView
from django.urls import re_path

# verifications 子路由
urlpatterns = [
    # 图形验证码
    re_path(r'image_codes/([\w-]+)/', ImageCodeView.as_view(), name='ImageCode'),
    # 短信验证码
    re_path(r'sms_codes/(1[3-9]\d{9})/', SMSCodeView.as_view(), name='SMSCode')
]
