/**
 @Name : myLayer 扩展插件 主要用来扩展layer 功能
 @Author: chenxiaoshun
 @Date : 2018-11-12
 */
layui.define(['layer', 'form'], function (exports) {
    let $ = layui.jquery;
    let layer = layui.layer;
    let form = layui.form;
    let MOD_NAME = 'myLayer';

    function Layer(isParent, top) {
        this.window = window;
        this.layer = layer;
        // 这里需要排除 跳到最外面的主页
        // console.log('$(window.parent.document).find(\'.layui-layout.layui-layout-admin\')', $(window.parent.document).find('.layui-layout.layui-layout-admin').length);
        let mainDom = $(window.parent.document).find('.layui-layout.layui-layout-admin');
        // 防止 layer 跳到最外层
        if (isParent && mainDom.length < 1) {
            this.window = window.parent;
            this.layer = this.window.layer;
        } else if (top) {
            this.window = window.top;
        }
    }

    Layer.prototype.success = function (content, callback) {
        let that = this;
        that.alert({
            title: '成功', content: content, icon: 'layui-icon-ok-circle', skin: 'success-layer',
        }, callback);
    };

    Layer.prototype.warning = function (content, callback) {
        let that = this;
        that.alert({
            title: '警告', content: content, icon: 'layui-icon-face-cry', skin: 'warning-layer',
        }, callback);
    };

    Layer.prototype.error = function (content, callback) {
        let that = this;
        that.alert({
            title: '错误提示', content: content, icon: 'layui-icon-close-fill', skin: 'error-layer',
        }, callback);
    };

    Layer.prototype.radioPrompt = function (value = {}, callback) {
        let that = this;
        let radios = [];
        $.each(value, function (k, v) {
            radios.push('<input type="radio" name="type" value="' + k + '" title="' + v + '">')
        });
        that.layer.open({
            type: 1,
            content: '<div class="layui-card"><div class="layui-card-body">\n' + '<form class="layui-form">\n' + '  <div class="layui-form-item">\n' + ' <label class="layui-form-label">选择类型</label>' + '    <div class="layui-input-block">\n' + radios.join('\n') + '    </div>\n' + '  </div>' + '  </form>' + '</div></div>',
            btn: ['确定', '取消'],
            btn1: function (index, layero) {
                let radioDom = layero.find('input[type="radio"]:checked');
                //console.log('选中了: ',radioDom);
                callback(radioDom);
            },
            success: function (layero, index) {
                form.render();
            },
        });
    };

    Layer.prototype.alert = function (options, callback) {
        let that = this;
        //let title = '提示';
        if (typeof options === "string") {
            let content = options;
            options = {};
            options.content = content;
        }
        options.title = options.title ? options.title : '提示';

        // 替换 被转换的字符
        options.content = options.content.replace(/[<>&"]/g, function (c) {
            return {'<': '&lt;', '>': '&gt;', '&': '&amp;', '"': '&quot;'}[c];
        });
        // 如果是在iframe发起弹窗, 则调用parent的layer对象执行弹窗
        //console.log(window.parent);
        // 此处还需要判断是否 parent 是最外层
        that.layer.open({
            type: 1,
            title: 'icon' in options ? '<i class="layui-icon ' + options.icon + '" style="font-size: 25px;margin-right: 10px;vertical-align: middle;"></i>' + options.title : options.title,
            skin: options.skin,
            offset: '30%',
            moveOut: true,
            content: '<div style="padding:20px;min-width:260px;">' + options.content.split('\n').join('<br>') + '</div>',
            btn: ['确定'],
            yes: function (index, layero) {
                if (callback) {
                    callback();
                }
                that.close(index);
            }
        });
    };

    Layer.prototype.confirm = function (content, success, cancel) {
        let that = this;
        if (typeof (content) === 'function') {
            success = content;
            content = '确定吗?';
        }
        let title = '请确认';
        let content_list = content.split('\n');
        // console.log('content ==',content);
        // console.log('content list==',content_list);
        if (content_list.length > 1) {
            title = content_list[0];
            content_list.splice(0, 1);
        }
        that.layer.open({
            type: 1,
            title: title,
            skin: 'warning-layer',
            offset: '30%',
            content: '<div style="padding:20px;min-width: 260px;">' + content_list.join('<br>') + '</div>',
            btn: ['确定', '取消'],
            yes: function (index, layero) {
                if (success) {
                    success();
                }
                that.close(index);
            },
            btn2: function (index) {
                if (cancel) {
                    cancel();
                }
                that.close(index);
            },
            cancel: function (index, layero) {
                if (cancel) {
                    cancel();
                }
            },
        });
    };

    //
    Layer.prototype.panel = function (url, title = "未知", type = 2) {
        let that = this;
        if (!url) {
            that.layer.warning('缺少url参数');
            return false;
        }
        return that.layer.open({
            type: type,
            skin: 'layui-anim my-layer-panel',
            title: title,
            anim: -1,
            offset: 'rb',
            area: ['50%', '100%'],
            fixed: true, resize: true, // shadeClose: true,
            closeBtn: 1,
            tipsMore: true,
            content: url,
        });
    };

    Layer.prototype.page = function (url, title) {
        let that = this;
        if (!title) {
            title = url;
        }
        return that.layer.open({
            type: 2, title: title, content: url, area: ['100%', '100%'], // offset: 'auto',
            offset: 't', maxmin: true, shadeClose: true, scrollbar: true,
        });
    };

    Layer.prototype.close = function (index) {
        let that = this;
        if (index) {
            that.layer.close(index);
            return false;
        }
        that.layer.closeAll()
    };

    Layer.prototype.refresh = function () {
        this.window.location.reload();
    };

    exports(MOD_NAME, function (isParent = false) {
        return new Layer(isParent)
    });
});