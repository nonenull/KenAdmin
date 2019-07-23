/**
 @Name : myForm 扩展插件 主要用来扩展lay-form功能
 @Author: chenxiaoshun
 @Date : 2018-11-12
 */
layui.define(['form', 'myLayer'], function (exports) {
    let $ = layui.jquery;
    let MOD_NAME = 'myForm';
    let form = layui.form;
    let layer = layui.myLayer;

    /*
     * 为form模块 增加一个 监听 select change  radio事件
     * 使用方法:
     *     在需要此功能的select标签 上 添加 my-change 自定义属性, 将自动拥有此功能
     *     my-change :
     *          例子: my-change={'value1':'select1','value2':'select2','value3':['select2','select3']}
     *          格式: {value:name,...},支持指定多对, ·value·为需要引发事件的值，·name·为需要显示的select name
     *'
     */

    function changeFormItem(data) {
        let value = data.value;
        let elem = $(data.elem);
        let filter = elem.attr('my-change');
        if (!filter) return false;

        let curform = elem.parents('.layui-form');
        let parseobj = JSON.parse(filter);
        //console.log('parseobj======== ', parseobj);

        layui.each(parseobj, function (selectValue, slideNames) {
            if ($.isArray(slideNames)) {
                layui.each(slideNames, function (index, value) {
                    resetItem(value);
                })
            } else {
                resetItem(slideNames);
            }
        });

        layui.each(parseobj, function (selectValue, slideNames) {
            if ($.isArray(slideNames)) {
                layui.each(slideNames, function (index, value) {
                    slideItem(selectValue, value);
                })
            } else {
                slideItem(selectValue, slideNames);
            }
        });

        // 打开显示 表单项
        function slideItem(selectValue, slideName) {
            let formItem = curform.find('[name="' + slideName + '"]');
            let slideDom = formItem.parents('.layui-form-item');

            if (selectValue === value) {
                slideDom.slideDown();
                slideDom.addClass('my-slided');
            }
        }

        // 重置表单项的状态, 隐藏
        function resetItem(slideName) {
            let formItem = curform.find('[name="' + slideName + '"]');
            //console.log('resetItem formitem======', slideName, formItem);
            let slideDom = formItem.parents('.layui-form-item');
            slideDom.hide();
            slideDom.removeClass('my-slided');
        }
    }

    form.initChange = function () {
        let myChangeDom = $('.layui-form').find('input[type="radio"][my-change]:checked, select[my-change]');
        // console.log('myChangeDom=========', myChangeDom);
        $.each(myChangeDom, function (k, v) {
            let self = $(v);
            let tagName = v.tagName.toLowerCase();
            let data = {};
            data.elem = v;
            switch (tagName) {
                case "input":
                    data.value = self.val();
                    break;
                case "select":
                    data.value = self.val();
                    break;
            }
            // console.log(self, data);
            changeFormItem(data);
        });
    };

    form.on('radio', function (data) {
        //console.log('radio data==== ', data);
        changeFormItem(data);
    });

    form.on('select', function (data) {
        changeFormItem(data);
    });

    // 遍历json的键,值 填充到表单中
    // 表单name == json key
    form.jsonToForm = function (json, layFilter) {
        let formDom = $('form[lay-filter="' + layFilter + '"]');
        layui.each(json, function (k, v) {
            let item = formDom.find('[name="' + k + '"]');
            let tagName;
            if (item.length) {
                tagName = (item.prop('tagName')).toLowerCase();
            }
            // console.log('tagName===', tagName, k, v);
            if (tagName === 'select') {
                let option = item.find('option');
                option.removeAttr('selected');
                layui.each(option, function (index, e) {
                    if (e.value === v) {
                        // console.log(e.value,v);
                        e.selected = true;
                    }
                });
            } else {
                item.attr('value', v);
            }
        });
        form.render('select');
    };

    //表单reset重置渲染
    $(document).on('reset', '.layui-form', function () {
        $('.my-slided').slideUp().removeClass('.my-slided');
    });

    form.verify({
        ip: [/^(?:(?:2[0-4][0-9]\.)|(?:25[0-5]\.)|(?:1[0-9][0-9]\.)|(?:[1-9][0-9]\.)|(?:[0-9]\.)){3}(?:(?:2[0-5][0-5])|(?:25[0-5])|(?:1[0-9][0-9])|(?:[1-9][0-9])|(?:[0-9]))$/, '不符合IP格式'],
        domain: [/^(?=^.{3,255}$)[a-zA-Z0-9/*][-a-zA-Z0-9/*]{0,62}(\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+$/, '不符合域名格式'],
        port: [/^([0-9]|[1-9]\d{1,3}|[1-5]\d{4}|6[0-5]{2}[0-3][0-5])$/, '端口有误'],
        unnecessary_number: function (value) {
            if (value) {
                if (!new RegExp("^([1-9][0-9]*){1,3}$").test(value)) {
                    return '填写数字！'
                }
            }
        }
    });


    /*
     自定义一个多选组件
     options:
     dom 指定某个select，默认使用带有my-multi-select的
     url select框变化的时候自动请求的url
     leftName  指定左边待选区的select name
     rightName 指定右边已选区的select name
     cuccess  成功回调函数
     */
    let msgConf = {
        icon: 2, shift: 6
    };
    form.MultiSelect = function (options) {
        if (!options.url) throw Error('options 缺少参数: url');

        let defaultOptions = {
            dom: $('select[my-multi-select]'), leftName: 'choose', rightName: 'choosed', display: 'block',
        };
        $.extend(defaultOptions, options);
        this.options = defaultOptions;
        this.init();
    };

    form.MultiSelect.prototype.init = function () {
        let that = this;
        let selectAreaHtml = '<div class="layui-form-item my-multi-select" style="display: ' + that.options.display + '">' + '<label class="layui-form-label">选区</label>' + '<div class="layui-input-inline">' + '<p>待选区</p>' + '<select multiple name="' + that.options.leftName + '" lay-ignore></select>' + '</div>' + '<div class="layui-input-inline layui-btn-group">' + '<a class="layui-btn layui-btn-mini"> > </a>' + '<a class="layui-btn layui-btn-mini"> >> </a>' + '<a class="layui-btn layui-btn-mini layui-btn-normal"> < </a>' + '<a class="layui-btn layui-btn-mini layui-btn-normal"> << </a>' + '<a class="layui-btn layui-btn-mini layui-btn-danger"><i class="layui-icon">&#x1002;</i></a>' + '</div>' + '<div class="layui-input-inline">' + '<p>已选区</p>' + '<select multiple name="' + that.options.rightName + '" lay-ignore></select>' + '</div>' + '</div>';

        let selectAreaDom = $(selectAreaHtml);
        that.leftSelect = selectAreaDom.find('select[name="' + that.options.leftName + '"]');
        that.rightSelect = selectAreaDom.find('select[name="' + that.options.rightName + '"]');
        that.options.dom.parents('.layui-form-item').after(selectAreaDom);
        form.render('select');
        this.action();
    };

    form.MultiSelect.prototype.action = function () {
        let that = this;
        let url = that.options.url;
        let multiSelect = that.options.dom;
        let leftSelect = that.leftSelect;
        let rightSelect = that.rightSelect;
        multiSelect.on('change', function (e) {
            let optionList = '';
            let postData = $(this).serialize();
            $.post(url, postData, function (result) {
                if (!result.length) {
                    layer.msg('没有数据');
                    return false;
                }
                $.each(result, function (k, v) {
                    let value = v[0];
                    let text = '';
                    let len = v.length;
                    if (len === 2) {
                        text = '【' + value + '】-- ' + v[1];
                    } else {
                        throw Error(url + ' 请求返回的格式有误');
                    }
                    optionList += '<option value="' + value + '">' + text + '</option>';
                });
                leftSelect.html(optionList);
                form.render('select');
            });
        });

        $('.my-multi-select .layui-btn-group .layui-btn').on('click', function () {
            let btn = $(this);
            switch (btn.index()) {
                case 0:
                    _transferOption(leftSelect, rightSelect, true);
                    break;
                case 1:
                    _transferOption(leftSelect, rightSelect);
                    break;
                case 2:
                    _transferOption(rightSelect, leftSelect, true);
                    break;
                case 3:
                    _transferOption(rightSelect, leftSelect);
                    break;
                case 4:
                    rightSelect.html('');
                    break;
            }
        });

        function _transferOption(dom, other, selected) {
            let findStr = selected ? 'option:selected' : 'option';
            let msgStr = selected ? '请选择' : '选区空';
            let optionDom = dom.find(findStr);
            if (!optionDom.length) {
                layer.msg(msgStr, msgConf);
                return false;
            }
            let otherOption = other.find('option');
            $.each(optionDom, function (i, v) {
                $.each(otherOption, function (j, k) {
                    let vHtml = v.innerHTML;
                    if (vHtml === k.innerHTML) {
                        delete optionDom[i];
                        layer.msg('存在重复选项，将过滤');
                        return true;
                    }
                });
            });
            other.prepend(optionDom);
            form.render('select');
        }
    };

    form.MultiSelect.prototype.getValues = function () {
        return this.rightSelect.children('option').map(function () {
            return $(this).val();
        }).get();
    };

    /*
    * 主要用于生成 password 字段的时候, 加一个 密码可视和隐藏功能
    * */
    $('.layui-form-password .layui-form-mid.layui-word-aux').on('click', function () {
        let self = $(this);
        let inputDom = self.prev().children('input');
        switch (inputDom.prop('type')) {
            case 'password':
                inputDom.prop('type', 'text');
                break;
            default:
                inputDom.prop('type', 'password');
                break;
        }
        self.toggleClass('my-open-eye');
    });

    let selectedForm = $('.my-select-form');
    selectedForm.on('click', 'button:contains("全选")', function () {
        let curSelectForm = $(this).parents('.my-select-form');
        let checkboxDom = curSelectForm.find('input[type=checkbox]');
        let checkedDom = checkboxDom.filter(':checked');
        if (checkboxDom.length === checkedDom.length) {
            checkboxDom.prop('checked', false);
        } else if (checkedDom.length >= 0) {
            checkboxDom.prop('checked', true);
        }
        form.render();
    });

    selectedForm.on('click', 'button:contains("反选")', function () {
        let curSelectForm = $(this).parents('.my-select-form');
        let checkboxDom = curSelectForm.find('input[type=checkbox]');
        let checkedDom = checkboxDom.filter(':checked');
        let noCheckedDom = checkboxDom.not(':checked');
        checkedDom.prop('checked', false);
        noCheckedDom.prop('checked', true);
        form.render();
    });


    // 重写form表单的val方法
    // 先遍历 form 的 item dom
    // 再遍历 值
    form.val = function (filter, object) {
        let ELEM = '.layui-form';
        var formElem = $(ELEM + '[lay-filter="' + filter + '"]');
        formElem.each(function (index, item) {
            var itemFrom = $(this);
            layui.each(object, function (key, value) {
                let itemElem = itemFrom.find('[name="' + key + '"]'), type;
                //console.log('itemElem ======= ', itemElem);
                //如果对应的表单不存在，则不执行
                if (!itemElem[0]) return;
                type = itemElem[0].type;

                switch (type) {
                    case 'checkbox':
                        // 如果为复选框
                        // 存在多个checkbox的情况
                        if (itemElem.length > 1) {
                            // console.log('存在多个checkbox的情况');
                            itemElem.each(function () {
                                let curVal = this.value;
                                this.checked = !!(curVal === value || $.inArray(curVal, value) >= 0);
                            });
                        } else {
                            itemElem[0].checked = value;
                        }
                        break;
                    case 'radio':
                        //如果为单选框
                        itemElem.each(function () {
                            this.checked = this.value === value;
                        });
                        break;
                    default:
                        //其它类型的表单
                        itemElem.val(value);
                        break;
                }
            });
        });
        form.render(null, filter);
    };

    exports(MOD_NAME, function (options) {
        return form.set(options);
    });
});