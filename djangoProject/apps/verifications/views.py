from random import random

from django import http
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection
from . import constants
from djangoProject.apps.verifications.libs.captcha.captcha import captcha
from .libs.yuntongxun.ccp_sms import CCP
from djangoProject.utils.response_code import RETCODE
import logging
from djangoProject.celery_tasks.sms.tasks import ccp_send_sms_code

# Create your views here.
# 创建日志输出器
logger = logging.getLogger('django')


class ImageCodeView(View):
    '''图形验证码'''

    def get(self, request, uuid):
        """
        :param request: 请求对象
        :param uuid: 唯一标识图形验证码所属于的用户
        :return: image/jpg
        """
        # 生成图片验证码
        text, image = captcha.generate_captcha()

        # 保存图形验证码
        redis_conn = get_redis_connection('verify_code')
        redis_conn.setex('img_%s' % uuid, constants.IMAGE_CODE_REDIS_EXPIRES, text)

        # 响应图片验证码
        return http.HttpResponse(image, content_type='image/jpg')


class SMSCodeView(View):
    '''短信验证码'''

    def get(self, request, mobile):
        """
              :param reqeust: 请求对象
              :param mobile: 手机号
              :return: JSON
        """

        image_code_client = request.GET.get('image_code')
        uuid = request.GET.get('uuid')

        # 校验参数
        if not all([image_code_client, uuid]):
            return http.JsonResponse({'code': RETCODE.NECESSARYPARAMERR, 'errmsg': '缺少必传参数'})

        # 创建redis连接对象
        redis_conn = get_redis_connection('verify_code')

        send_flag = redis_conn.get('send_flag_%s' % mobile)
        if send_flag:
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '发送短信过于频繁'})

        # 提取图形验证码
        image_code_server = redis_conn.get('img_%s' % uuid)
        if image_code_server is None:
            # 图形验证码过期或者不存在
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图形验证码失效'})

        # 删除图形验证码，避免恶意测试图形验证码
        try:
            redis_conn.delete('img_%s' % uuid)
        except Exception as e:
            logger.error(e)

        # 对比图形验证码
        # bytes转字符串
        image_code_server = image_code_server.decode()
        # 转小写后比较
        if image_code_client.lower() != image_code_server.lower():
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '输入图形验证码有误'})

        # 生成短信验证码：生成6位数验证码
        # sms_code = '%06d' % random.randint(0, 999999)
        # 测试的时候验证码设置为固定值
        sms_code = '666666'
        logger.info(sms_code)

        # 创建Redis管道
        pl = redis_conn.pipeline()
        # 保存短信验证码\将Redis请求添加到队列
        redis_conn.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # 重新写入send_flag
        redis_conn.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        # 执行请求
        pl.execute()

        # 管道pipeline

        # 可以一次性发送多条命令并在执行完后一次性将结果返回。
        # pipeline通过减少客户端与Redis的通信次数来实现降低往返延时时间。
        # 实现的原理

        # 实现的原理是队列。
        # Client可以将三个命令放到一个tcp报文一起发送。
        # Server则可以将三条命令的处理结果放到一个tcp报文返回。
        # 队列是先进先出，这样就保证数据的顺序性

        redis_conn.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # 发送短信验证码 (本地环境没有集成云通讯、暂不使用)
        # CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60],
                                #constants.SEND_SMS_TEMPLATE_ID)

        # Celery异步发送短信验证码 (本地环境没有集成云通讯、暂不使用)
        # ccp_send_sms_code.delay(mobile, sms_code)

        # 响应结果e
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '发送短信成功'})


