from django.urls import path, include
from .views import IndexView

# contents 子路由
urlpatterns = [
    path(r'', IndexView.as_view(), name='index')
]
