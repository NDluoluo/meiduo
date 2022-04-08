from django.urls import path, include
from .views import AreasView

# contents 子路由
urlpatterns = [
    path('areas/', AreasView.as_view(), name='Areas')
]
