from django.contrib.auth.mixins import LoginRequiredMixin
from django import http

from djangoProject.utils.response_code import RETCODE


class LoginRequiredJSONMixin(LoginRequiredMixin):
    """自定义判断用户是否登录的扩展类：返回JSON"""

    # 为什么只需要重写handle_no_permission？
    # 因为判断用户是否登录的操作，父类已经完成，子类只需要关心，如果用户未登录，对应怎样的操作
    def handle_no_permission(self):
        """直接响应JSON数据"""
        return http.JsonResponse({'code': RETCODE.SESSIONERR, 'errmsg': '用户未登录'})


"""
def handle_no_permission(self):
    if self.raise_exception:
        raise PermissionDenied(self.get_permission_denied_message())
    return redirect_to_login(self.request.get_full_path(), self.get_login_url(), self.get_redirect_field_name())

class LoginRequiredMixin(AccessMixin):

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)
"""










#
# 提示：
#
# login_required装饰器可以直接装饰函数视图，但是本项目使用的是类视图。
# as_view()方法的返回值就是将类视图转成的函数视图。
# 结论：
#
# 要想使用login_required装饰器装饰类视图，可以间接的装饰as_view()方法的返回值，以达到预期效果。
# url(r'^info/$', login_required(views.UserInfoView.as_view()), name='info'),
# class UserInfoView(View):
#     """用户中心"""
#
#     def get(self, request):
#         """提供个人信息界面"""
#         return render(request, 'user_center_info.html')
# 2.定义View子类封装login_required装饰器
#
# 提示：LoginRequired(object)依赖于视图类View，复用性很差。
# url(r'^info/$', views.UserInfoView.as_view(), name='info'),
# class LoginRequired(View):
#   """验证用户是否登陆"""
#
#   @classmethod
#   def as_view(cls, **initkwargs):
#       # 自定义as_view()方法中，调用父类的as_view()方法
#       view = super().as_view()
#       return login_required(view)
#
#
# class UserInfoView(LoginRequired):
#     """用户中心"""
#
#     def get(self, request):
#         """提供个人信息界面"""
#         return render(request, 'user_center_info.html')
# 3.定义obejct子类封装login_required装饰器
#
# 提示：LoginRequired(object)不依赖于任何视图类，复用性更强。
# url(r'^info/$', views.UserInfoView.as_view(), name='info'),
# class LoginRequired(object):
#   """验证用户是否登陆"""
#
#   @classmethod
#   def as_view(cls, **initkwargs):
#       # 自定义as_view()方法中，调用父类的as_view()方法
#       view = super().as_view()
#       return login_required(view)
#
#
# class UserInfoView(LoginRequired, View):
#     """用户中心"""
#
#     def get(self, request):
#         """提供个人信息界面"""
#         return render(request, 'user_center_info.html')
# 4.定义验证用户是否登录扩展类
#
# 提示：定义扩展类方便项目中导入和使用(meiduo_mall.utils.views.py)
# class LoginRequiredMixin(object):
#   """验证用户是否登录扩展类"""
#
#   @classmethod
#   def as_view(cls, **initkwargs):
#       # 自定义的as_view()方法中，调用父类的as_view()方法
#       view = super().as_view()
#       return login_required(view)
#  class UserInfoView(LoginRequiredMixin, View):
#     """用户中心"""
#
#     def get(self, request):
#         """提供个人信息界面"""
#         return render(request, 'user_center_info.html')

# def login_required_json(view_func):
#     """
#     判断用户是否登录的装饰器，并返回json
#     :param view_func: 被装饰的视图函数
#     :return: json、view_func
#     """
#     # 恢复view_func的名字和文档
#     @wraps(view_func)
#     def wrapper(request, *args, **kwargs):
#
#         # 如果用户未登录，返回json数据
#         if not request.user.is_authenticated():
#             return http.JsonResponse({'code': RETCODE.SESSIONERR, 'errmsg': '用户未登录'})
#         else:
#             # 如果用户登录，进入到view_func中
#             return view_func(request, *args, **kwargs)
#
#     return wrapper
