layui.define(['myElement', 'myLayer', 'myForm', 'util', 'myDate'], function (exports) {
    $ = layui.jquery;
    let mlayer = layui.myLayer(true);
    let clayer = layui.myLayer();
    let form = layui.myForm();
    let util = layui.util;
    let myDate = layui.myDate;

    /* ********* CSRF ********* */
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            let cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                let cookie = $.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    let loadLayer = $('#loading');
    $.ajaxSetup({
        crossDomain: false, beforeSend: function (xhr, settings) {
            if (settings.type.toLowerCase() === 'post') {
                let csrfToken = getCookie('csrftoken');
                xhr.setRequestHeader("X-CSRFToken", csrfToken);
                // 上传文件的时候, 直接设置settings.data会发生错误
                // console.log("settings===", settings, typeof settings.data);
                if (typeof settings.data === 'string') {
                    settings.data += '&csrfmiddlewaretoken=' + csrfToken;
                }
            }
            loadLayer.show();
        }, error: function (jqXHR, textStatus, errorThrown) {
            let responseText = jqXHR.responseText;
            switch (jqXHR.status) {
                case(500):
                    if (responseText.indexOf('DEBUG = True') === -1) {
                        mlayer.error(responseText);
                    } else {
                        let resultList = responseText.split('\n\n');
                        let result = resultList[0];
                        let splitResult = result.split('\n');
                        // console.log(splitResult);
                        mlayer.error(splitResult.join('\n'));
                    }
                    break;
                case(403):
                    if (responseText.indexOf('CSRF verification failed') > -1) {
                        mlayer.error("CSRF token 验证失败");
                    } else {
                        mlayer.error("无权限执行此操作");
                    }
                    break;
                case(408):
                    mlayer.error("请求超时");
                    break;
                case(405):
                    mlayer.error("Method Not Allowed");
                    break;
                case(401):
                    mlayer.error(responseText, function () {
                        mlayer.layer.open({
                            title: '便捷登录', type: 2, area: ['700px', '450px'], fixed: false, //不固定
                            maxmin: true, content: '/', success: function (layero, index) {
                                let body = mlayer.layer.getChildFrame('body', index);
                                if (body.find('.layui-header.header').length > 0) {
                                    mlayer.close(index);
                                    mlayer.layer.msg('重新登录成功');
                                }
                            }
                        });
                    });
                    break;
                case(0):
                    mlayer.error("与服务器失去联系,请检查");
                    break;
                default:
                    mlayer.error(responseText);
            }
        }, complete: function () {
            loadLayer.hide();
        }
    });

    util.fixbar();

    // 修改.my-detail-table 的hover事件
    $(document).on('mouseover mouseout', '.my-detail-table td', function (e) {
        let hoverClass = "my-detail-table-hover";
        let dom = $(this);
        let index = dom.index();
        let z = index % 2;
        let otherDom;
        if (z === 0) {
            otherDom = dom.next();
        } else {
            otherDom = dom.prev();
        }
        switch (e.type) {
            case 'mouseover':
                dom.addClass(hoverClass);
                otherDom.addClass(hoverClass);
                break;

            case 'mouseout':
                dom.removeClass(hoverClass);
                otherDom.removeClass(hoverClass);
                break;
        }
    });

    /*
     * my-filter以"layer-"开头的，自动获取template内容，并新打开一个layer
     * 需要在页尾指定一个<script type="text/html" id=" + my-filter名 + '-template">的模板
     */
    $('[my-filter^="layer-"]').on('click', function () {
        let filterName = $(this).attr('my-filter');
        clayer.layer.open({
            type: 1, content: '<div class="my-layer-content-padding">' + $('#' + filterName + '-template').html() + '</div>',
        });
        form.render();
    });

    /*
     *   select指定了 lay-filter="auto-submit" 后
     *   修改选择自动提交表单
     * */
    form.on('select(auto-submit)', function (data) {
        clayer.msg('表单提交中...');
        let form = $(data.elem).parents('form');
        form.submit();
    });


    $('.layui-form').on('submit', function () {
        clayer.layer.msg('执行中...');
    });

    // 设置 form verify
    (function () {
        let checkConpanyEmail = function (value, item) {
            if (!value) return;
            // 先验证一下 email
            let emailRule = form.config.verify.email;
            // console.log('emailRule[0]==',emailRule[0]);
            // console.log('value==',value);
            // console.log('emailRule[0].test(value)==',emailRule[0].test(value));
            if (!emailRule[0].test(value)) {
                return emailRule[1]
            }

            let state = false;
            $.each(emailPrefix, function (k, v) {
                if (value.indexOf(v) > 0) {
                    state = true;
                    return false;
                }
            });
            if (!state) {
                return '仅支持使用公司的邮箱 ' + emailPrefix
            }
        };
        const emailPrefix = ['@hengxinyongli.com', '@tekuaikeji.com'];
        form.verify({
            companyEmail: checkConpanyEmail, companyEmails: function (value, item) {
                if (!value) return;
                let splits = value.split(',');
                let text = '';
                $.each(splits, function (k, v) {
                    // console.log('splits======', k, v);
                    v = $.trim(v);
                    let result = checkConpanyEmail(v, item);
                    if (result) {
                        text = result;
                        return false;
                    }
                });
                // console.log('text===', text);
                return text;
            },
        });
    }());

    // 根据滚动条的出现隐藏菜单栏目
    (function () {
        // 0 代表 关闭, 1 开启
        let state = 1;
        let trueWidth;

        function hasScrollbar() {
            let scrollWidth = document.body.scrollWidth;
            let clientWidth = (window.innerWidth || document.documentElement.clientWidth);
            if (Math.abs(clientWidth - trueWidth) < 120) {
                return 'no'
            }
            let isHas = scrollWidth > clientWidth;
            if (isHas) trueWidth = scrollWidth;
            return isHas
        }

        $(window).on('resize', function () {
            // 排除其他页面用打开, 无法获取到 toggleMenu 方法
            if (!('toggleMenu' in window.parent)) {
                return false;
            }
            let isHas = hasScrollbar();
            // 此处要防止死循环
            if (isHas === 'no') return false;
            if (isHas && state === 1) {
                // console.log('收回菜单=====state==', state, hasScrollbar());
                state = 0;
                window.parent.toggleMenu(state);
            } else if (!isHas && state === 0) {
                // console.log('展开菜单=====state==', state, hasScrollbar());
                state = 1;
                window.parent.toggleMenu(state);
            }
            return false;
        });
    }());

    // 卡片 隐藏
    (function () {
        let slideDom = $('.layui-card > .layui-card-header.slide');

        function setSlide(state, dom, bodyDom) {
            switch (state) {
                case 'down':
                    dom.removeClass('slide-up');
                    dom.addClass('slide-down');
                    bodyDom.slideUp();
                    break;
                case 'up':
                    dom.removeClass('slide-down');
                    dom.toggleClass('slide-up');
                    bodyDom.slideDown();
                    break;
            }
        }

        $.each(slideDom, function (k, v) {
            let self = $(this);
            let bodyDom = self.next();
            if (self.hasClass('slide-down')) {
                setSlide('down', self, bodyDom);
            } else if (self.hasClass('slide-up')) {
                setSlide('down', self, bodyDom);
            }
        });

        slideDom.on('click', function () {
            let self = $(this);
            let bodyDom = self.next();
            if (bodyDom.is(':visible')) {
                setSlide('down', self, bodyDom);
            } else {
                setSlide('up', self, bodyDom);
            }
        });
    })();


    (function () {
        // 按住 ctrl + 空格 则将当前iframe 从新标签页打开
        $(document).on('keyup', function (e) {
            if (self === top) {
                return true;
            }
            let keyCode = e.keyCode || e.which;
            if (e.ctrlKey && keyCode === 32) {
                window.open(window.location.href, "_blank");
            }
            layui.stope(e);
        });
    })();

    exports('public');
});

/*
* 调用后自动给 iframe 设置高度
* */
function AutoIframe(iframe) {
    let timer;
    timer = setInterval(function () {
        let contentDocument = iframe.contentDocument;
        if (!contentDocument && timer) {
            clearInterval(timer);
            return false;
        }
        let body = contentDocument.body;
        if (body) {
            iframe.style.height = body.scrollHeight;
        } else {
            clearInterval(timer);
        }
    }, 200)
}