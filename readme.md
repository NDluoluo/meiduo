##### 官方文档地址

- https://docs.djangoproject.com/zh-hans/4.0

##### 安装Django

- python -m pip install django

##### 创建requirements

- pip freeze > requirements.txt

##### 创建项目

- django-admin startproject project_name

##### 创建应用

- python manage.py startapp app_name

##### 修改语言和时区

- 在项目文件的settings.py中找到并修改:
    - a.LANGUAGE_CODE为语言
    - b.TIME_ZONE为时区
        ```python
        LANGUAGE_CODE = 'zh-Hans'
        TIME_ZONE = 'Asia/Shanghai'
        ```

##### 配置数据库

- python -m pip install pymysql

- 修改默认数据库配置:
    - a.在项目文件的settings.py中DATABASES修改默认数据库:
        ```python
        DATABASES = {
        # 'default': {
        #     'ENGINE': 'django.db.backends.sqlite3',
        #     'NAME': BASE_DIR / 'db.sqlite3',
        # }
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'database_name',
            'USER': 'root',
            'PASSWORD': 'password',
            'HOST': '127.0.0.1',
            'PORT': '3306',
            }
        }
        ```
    - b.在项目文件的_init_.py中写入代码：
        ```python
        import pymysql
        pymysql.install_as_MySQLdb()
        ```

##### 启动项目(本地开发环境) 迁移模型类

- python manage.py makemigrations
- python manage.py migrate
- python manage.py runserver

##### 修改项目模板文件(template)路径配置  默认模板和jinja2模板

- 在settings.py文件中找到

  ```python
  TEMPLATES = [
      {
          'BACKEND': 'django.template.backends.django.DjangoTemplates',
          'DIRS': [],
          'APP_DIRS': True,
          'OPTIONS': {
              'context_processors': [
                  'django.template.context_processors.debug',
                  'django.template.context_processors.request',
                  'django.contrib.auth.context_processors.auth',
                  'django.contrib.messages.context_processors.messages',
              ],
          },
      },
        {
        # 'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'environment': 'djangoProject.utils.jinja2_dev.environment'
        },
    }
  ]
  ```

- 将DIRS的值改为os.path.join(BASE_DIR,'first_a/templates')

  ```python
          'DIRS': [os.path.join(BASE_DIR,'your_project_name/templates')],
  ```


##### 创建并且配置静态文件

- a.新建文件夹static(和templates处于同一级目录)

- b.在settings中新增：

  ```python
  STATICFILES_DIRS=[
      os.path.join(BASE_DIR,'first_a/static')
  ]
  ```

安装 rabbitmq 配置远程访问
启用消息队列模式

安装eventlet模块
启用 Eventlet 池 

celery -A celery_tasks.main worker -l info -P eventlet -c 1000

默认账户： makelove 12345678  
rabbitmq makelove 123456