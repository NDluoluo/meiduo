from celery import Celery

# 创建celery实例
celery_app = Celery('meiduo')
# 加载celery配置
celery_app.config_from_object('celery_tasks.config')
# 自动注册celery 任务
celery_app.autodiscover_tasks(['celery_tasks.sms'])


# 启动Celery服务
# celery -A celery_tasks.main worker -l info
# -A指对应的应用程序, 其参数是项目中 Celery实例的位置。
# worker指这里要启动的worker。
# -l指日志等级，比如info等级。

# 改变进程池方式为协程方式
# celery worker的工作模式   pip install eventlet
# celery -A celery_tasks.main worker -l info -P eventlet -c 1000