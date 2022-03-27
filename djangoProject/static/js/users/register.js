const register = {
    // 修改Vue读取变量的语法
    delimiters: ['[[', ']]'],
    data() {
        return {
            // 用户名
            username: '',
            // 密码
            password: '',
            // 确认密码
            password2: '',
            // 手机号
            mobile: '',
            // 是否勾选协议
            allow: '',
            // 用户名错误
            error_name: false,
            // 密码错误
            error_password: false,
            // 密码错误
            error_re_password: false,
            // 手机号错误
            error_mobile: false,
            // 没有勾选协议
            error_allow: false,
            // 图形验证码路劲
            image_code_url: '',
            // 图形验证码
            image_code: '',
            // 图形验证码错误状态
            error_image_code: false,
            // 短信验证码
            sms_code: '',
            sms_code_tip: '获取短信验证码',
            // 短信验证码状态
            sending_flag: false,

            // 错误信息
            error_name_message: '',
            error_mobile_message: '',
            error_password_message: '',
            error_re_password_message: '',
            error_image_code_message: '',
            error_sms_code_message: '',
            error_sms_code: ''
        }
    },
    mounted() {
        // 生成图形验证码
        this.generate_image_code();
    },
    // 用户交互事件实现
    methods: {
        // 生成图形验证码
        generate_image_code() {
            // 生成UUID.generateUUID() : 封装在common.js文件里面
            this.uuid = generateUUID();
            // 拼接图形验证码请求地址
            this.image_code_url = '/image_codes/' + this.uuid + '/';
        },
        // 校验图形验证码
        check_image_code() {
            if (!this.image_code) {
                this.error_image_code_message = '请填写图片验证码';
                this.error_image_code = true;
            } else {
                this.error_image_code = false;
                this.error_image_code_message = '';
            }
        },
        // 校验短信验证码
        check_sms_code() {
            if (this.sms_code.length === 0) {
                this.error_sms_code_message = '请填写短信验证码';
                this.error_sms_code = true;
            } else if (this.sms_code.length < 6) {
                this.error_sms_code_message = '验证码错误';
                this.error_sms_code = true;
            } else {
                // let url = '/sms_codes/' + this.mobile + '/';
                // axios.post(url, {
                //     mobile: this.mobile,
                //     sms_code: this.sms_code
                // }).then(response => {
                //     if (response.data.sms_code_errmsg === '') {
                //         this.error_sms_code = false;
                //     } else {
                //         this.error_sms_code = true;
                //         this.error_sms_code_message = data.sms_code_errmsg;
                //     }
                // }).catch(error => {
                //     console.log(error);
                // });
                this.error_sms_code_message = '';
                this.error_sms_code = false;
            }
        },
        // 发送短信验证码
        send_sms_code() {
            // 避免重复点击
            if (this.sending_flag === true) {
                return;
            } else {
                this.sending_flag = true;
            }
            // 校验参数
            this.check_mobile();
            this.check_image_code();
            if (this.error_mobile === true || this.error_image_code === true) {
                this.sending_flag = false
                return;
            }
            let url = '/sms_codes/' + this.mobile + '/?image_code=' + this.image_code + '&uuid=' + this.uuid;
            axios.get(url, {
                responseType: 'json'
            }).then(response => {
                if (response.data.code === '0') {
                    // 倒计时60S
                    var num = 60;
                    var time = setInterval(() => {
                        if (num === 1) {
                            clearInterval(time);
                            this.sms_code_tip = '获取短信验证码';
                            this.sending_flag = false;
                        } else {
                            num -= 1;
                            // 展示倒计时信息
                            this.sms_code_tip = num + '秒';
                        }
                    }, 1000, 60)
                } else {
                    // 4001
                    if (response.data.code === '4001') {
                        this.error_image_code_message = response.data.errmsg;
                        this.error_image_code = true;
                    } else {
                        // 4002
                        this.error_sms_code_message = response.data.errmsg;
                        this.error_sms_code = true;
                    }
                    // 上一次失败的不行了、需要重新获取图片验证码
                    this.generate_image_code();
                    this.sending_flag = false;
                }
            }).catch(error => {
                console.log(error.response);
                this.sending_flag = false;
            });

        },
        // 校验用户名
        check_username() {
            let re = /^[a-zA-Z0-9_-]{5,20}$/;
            if (re.test(this.username)) {
                this.error_name = false;
                this.error_name_message = '';
            } else {
                this.error_name_message = '请输入5-20个字符的用户名';
                this.error_name = true;
            }

            // 判断用户是否已注册
            // 只有当用户输入的用户名满足条件时才会执行下面代码
            if (this.error_name === false) {
                let url = '/usernames/' + this.username + '/count/'
                axios.get(url, {
                    responseType: 'json'
                }).then(response => {
                    if (response.data.count === 1) {
                        this.error_name_message = '用户名已存在';
                        this.error_name = true;
                    } else {
                        this.error_name = false;
                        this.error_name_message = '';
                    }
                }).catch(error => {
                    console.log(error.response);
                })
            }
        },
        // 校验密码
        check_password() {
            let re = /^[0-9A-Za-z]{8,20}$/;
            if (re.test(this.password)) {
                this.error_password = false;
                this.error_password_message = '';
            } else {
                this.error_password = true;
                this.error_password_message = '请输入8-20位的密码';
            }
        },
        // 校验确认密码
        check_re_password() {
            if (this.password !== this.password2) {
                this.error_re_password = true;
                this.error_re_password_message = ''
            } else {
                this.error_re_password = false;
                this.error_re_password_message = '两次输入的密码不一致'
            }
        },
        // 校验手机号
        check_mobile() {
            let re = /^1[3-9]\d{9}$/;
            if (re.test(this.mobile)) {
                this.error_mobile = false;
            } else {
                this.error_mobile_message = '您输入的手机号格式不正确';
                this.error_mobile = true;
            }

            // 判断手机号是否已注册
            // 只有当用户输入的手机号满足条件时才会执行下面代码
            if (this.error_mobile === false) {
                let url = '/mobiles/' + this.mobile + '/count/';
                axios.get(url, {
                    responseType: 'json'
                }).then(response => {
                    if (response.data.count === 1) {
                        this.error_mobile_message = '您输入的手机号已被注册!';
                        this.error_mobile = true;
                    } else {
                        this.error_mobile_message = '';
                        this.error_mobile = false;
                    }
                }).catch(error => {
                    console.log(error.response)
                })
            } else {

            }
        },
        // 校验是否勾选协议
        check_allow() {
            if (!this.allow) {
                this.error_allow = true;
            } else {
                this.error_allow = false;
            }
        },
        // 监听表单提交事件
        on_submit() {
            this.check_username();
            this.check_password();
            this.check_re_password();
            this.check_mobile();
            this.check_allow();
            if (this.error_name === true || this.error_password === true || this.error_re_password === true
                || this.error_mobile === true || this.error_allow === true) {
                // 禁用表单的提交
                window.event.returnValue = false;
            }
        }
    }

};

Vue.createApp(register).mount('#app');