/**
 @Name : myElement 扩展插件
 @Author: chenxiaoshun
 @Date : 2018-11-22
 */
layui.define(['element', 'myLayer'], function (exports) {
    let $ = layui.jquery;
    let MOD_NAME = 'myElement';
    let element = layui.element;
    let MY_SWITCH_BTN = '.my-switch-btn';
    let mLayer = layui.myLayer(true);
    console.log(mLayer);
    /*
     * 页面加载后 自动 渲染 switch 按钮
     * 例子:
     *  <div class="my-switch-btn layui-form-switch" lay-text="停止|启动" lay-switch-status="0" lay-filter="redis-switch"><em></em><i></i></div>
     *  lay-text="停止|启动": 用 ‘|’ 做分隔符，左边为 off状态的文字，右边为on状态的文字
     *  lay-switch-status: 用来标示按钮默认的状态，为 0 代表 off ,1 代表 on
     *  lay-filter:  见layui官网
     *
     * */
    $(function () {
        let btn = $(MY_SWITCH_BTN);
        layui.each(btn, function (i, e) {
            let dom = $(e);
            let status = parseInt(dom.attr('lay-switch-status'));
            let layText = dom.attr('lay-text').split('|');
            let off = layText[0], on = layText[1];
            let isAllowStatus = layText.hasOwnProperty(status);
            if (!isAllowStatus) {
                layui.hint().error('设置错误，请检查switch按钮的 lay-text lay-switch-status属性' + '\n' + dom.prop('outerHTML'));
                return false;
            }
            let statusText = layText[status];
            dom.find('em').text(layText[status]);
            if (statusText === on) {
                dom.addClass('layui-form-onswitch');
            }
        });
    });

    // switch按钮的控制方法
    $(document).on('click', MY_SWITCH_BTN, function (e) {
        let othis = $(this);
        let filter = othis.attr('lay-filter');
        let status = !!parseInt(othis.attr('lay-switch-status'));
        let btn = new element.switchBtn(othis);
        layui.event.call(this, 'element', 'my-switch(' + filter + ')', {
            btn: btn, elem: e.target, status: status, othis: othis
        });
    });

    // 监听 tab 切换，如果标签 存在layid 则动态修改location.hash，在url中显示当前打开的标签
    element.on('tab', function (data) {
        let tabDom = data.elem;
        let index = data.index;
        let titleDom = tabDom.find('.layui-tab-title > li').eq(index);
        let layID = titleDom.attr('lay-id');
        if (layID) {
            location.hash = '#' + layID;
            history.pushState({}, '', location.href);
        }
    });

    // layid 不存在时，可以根据layid的值来切换到相应索引值等于layid的标签
    element.tabChange = function (filter, layid) {
        let title = '.layui-tab-title';
        let tabElem = $('.layui-tab[lay-filter=' + filter + ']');
        let titElem = tabElem.children(title);
        let liElem = titElem.find('>li[lay-id="' + layid + '"]');
        if (!liElem.length) liElem = titElem.find('>li').eq(layid);
        liElem.click();
        return this;
    };

    // 自定义switch 控制方法
    element.switchBtn = function (btn) {
        let status = parseInt(btn.attr('lay-switch-status'));
        let layText = btn.attr('lay-text').split('|');
        let on = layText[0], off = layText[1];
        this.toggle = function () {
            let newStatus = (layText[status] === on) ? off : on;
            btn.find('em').text(newStatus);
            btn.toggleClass('layui-form-onswitch');
        };
    };

    /* 一个倒计时 提示框  */
    element.CountDown = function () {
        let existDom = $('#countdown');
        if (existDom.length === 0) {
            this.dom = $('<div id="countdown"><span>倒计时</span><span>0</span></div>');
        } else {
            this.dom = existDom;
        }
        $('body').append(this.dom);
        this.numDom = this.dom.children('span:last');
    };

    element.CountDown.prototype.setNumber = function (number) {
        this.numDom.text(number);
    };

    element.CountDown.prototype.start = function (number, callback) {
        if (number === undefined) throw Error('请传递一个倒计时的数字');
        number = parseInt(number);
        let that = this;
        that.stop();
        that.dom.show(200, function () {
            that.setNumber(number--);
        });
        that.timer = setInterval(function () {
            that.setNumber(number);
            if (number === 0) {
                that.stop();
                //console.log('时间到');
                if (callback) callback();
            }
            number--;
        }, 1000);
    };

    element.CountDown.prototype.stop = function () {
        clearInterval(this.timer);
        this.setNumber(0);
        this.dom.hide(100);
    };
    /* 一个倒计时 提示框  */

    /* 一个 步骤流程进度条  */
    /*
    *   options:
    *       {
    *           dom : '#id', // dom位置
    *           processList: [], // 支持简单的['a','b','c']形式, 也支持复杂一点的 [{'id':'111','role':'a', type:' role type', text:'help text'}]
    *           curProgress: 0, // 支持直接输入数组下标的方式, 或者直接指定 name 值
    *       }
    *
    * */
    element.StepProcessBar = function (options) {
        if (!options.dom) throw Error('请设置dom');
        if (!options.nodeList || !options.nodeList.length) throw Error('请设置 nodeList');
        // 此处流程进度是从1开始计, 减1方便计算
        switch (typeof options.curProgress) {
            case "undefined":
                options.curProgress = -1;
                break;
            case "number":
                options.curProgress -= 1;
                break;
            default:
                $.each(options.nodeList, function (k, v) {
                    if (options.curProgress === v || options.curProgress === v.name) {
                        options.curProgress = k;
                        return false;
                    }
                });
                break
        }
        if (typeof options.dom === 'string') options.dom = $(options.dom);

        this.options = options;
        this.init();
    };

    element.StepProcessBar.prototype.init = function () {
        let that = this;
        let options = that.options;
        let pList = options.nodeList;
        let pListLen = pList.length;
        let curProgress = options.curProgress;
        let curPercent = 100 / (pListLen - 1) * options.curProgress + '%';
        let wrap = $('<div class="my-process"></div>');
        let stepBar = $('<div class="layui-progress layui-progress-big"></div>');
        wrap.append(stepBar);
        let progressBar = that.progressBar = $('<div class="layui-progress-bar" lay-percent="' + curPercent + '"></div>');
        stepBar.append(progressBar);
        $.each(options.nodeList, function (k, v) {
            // console.log(k,v);
            let barContent = $('<div class="step-bar-content"></div>');
            if (v.id) {
                barContent.attr('data-id', v.id);
            }

            let curPercent = 100 / (pListLen - 1) * k + '%';
            barContent.css('left', curPercent);
            stepBar.append(barContent);
            let indexDom = $('<span>' + (k + 1) + '</span>');
            let status = v.status;
            let badge = v.badge;
            if (typeof v === "string") {
                barContent.append('<div class="step-bar-content-title"><em class="layui-badge layui-bg-gray">' + v + '</em></div>');
            } else {
                let type = v.type;
                let text = v.text;

                if (type) {
                    indexDom = $('<span>' + type + '</span>');
                }
                if (text) {
                    barContent.prepend('<div class="step-bar-content-top"><em>' + text + '</em></div>');
                }
                barContent.append('<div class="step-bar-content-title"><em class="layui-badge layui-bg-cyan">' + v.name + '</em></div>');
                if (typeof v.operator === "object") {
                    barContent.append(`<div class="step-bar-content-operator"><em class="layui-badge layui-bg-rim" data-name="${v.operator.join("\n")}">点击查看</em></div>`);
                } else if (v.operator) {
                    barContent.append(`<div class="step-bar-content-operator"><em class="layui-badge layui-bg-gray">${v.operator}</em></div>`);
                }
                if (status) {
                    let contentDom = $('<div class="step-bar-content-bottom"><em class="layui-badge layui-bg-gray">' + status + '</em></div>');
                    let emDom = contentDom.children('em');
                    if (badge) {
                        emDom.removeClass('layui-bg-gray').addClass(badge);
                    }
                    barContent.append(contentDom);
                }
            }
            if (k <= curProgress) {
                if (k === curProgress && status) {
                    indexDom.addClass(badge);
                } else {
                    indexDom.css('background-color', '#5FB878')
                }
            }
            barContent.append(indexDom);
            barContent.css('left', curPercent);
            if (options.click) {
                barContent.on('click', function (e) {
                    if ($(e.target).parents('.step-bar-content-operator').length) {
                        return true;
                    }
                    options.click(v, $(this));
                });
            }
        });
        options.dom.html(wrap);
        element.init();
        $(document).on('click', '.step-bar-content-operator > .layui-badge.layui-bg-rim', function () {
            console.log('$(this)=======', $(this));
            let name = $(this).attr('data-name');
            mLayer.alert(name);
            return false;
        });
    };

    element.StepProcessBar.prototype.setProgress = function (index) {
        // 重新设置进度
        this.options.curProgress = index - 1;
        this.init();
    };

    /* 一个 步骤流程进度条  */

    // 一个 支持上下拉的box
    $('.my-box').find('.my-box-tools > button').on('click', function (e) {
        let btn = $(this);
        let box = btn.parents('.my-box');
        switch (btn.index()) {
            case 0:
                let isOpened = box.hasClass('my-box-opened');
                if (isOpened) {
                    box.find('.my-box-body').slideUp();
                    box.css('height', 'inherit');
                    box.removeClass('my-box-opened');
                } else {
                    box.find('.my-box-body').slideDown();
                    box.css('height', '');
                    box.addClass('my-box-opened');
                }
                break;
            case 1:
                box.find('.my-box-body').slideUp(function () {
                    setTimeout(function () {
                        box.remove();
                    }, 300);
                });
                box.css('height', 'inherit');
                break;
        }
    });

    let selectedCls = 'layui-this';
    let showCls = 'my-tab-show';
    let tabDom = $('.my-tab');
    tabDom.on('click', '.my-tab-head > div', function () {
        let self = $(this);
        let curTab = self.parents('.my-tab');
        curTab.find('.my-tab-head > div').removeClass(selectedCls);
        self.addClass(selectedCls);
        let index = self.index();
        let tabContentsDom = curTab.find('.my-tab-contents > .my-tab-content');
        tabContentsDom.removeClass(showCls);
        tabContentsDom.eq(index).addClass(showCls);
    });


    if (tabDom.length > 0) {
        $.each(tabDom, function () {
            $(this).find('.my-tab-head > div.layui-this').click();
        });
    }

    exports(MOD_NAME, function (options) {
        return element.set(options);
    });
});