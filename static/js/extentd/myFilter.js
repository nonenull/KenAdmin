/**
 @Name : myFilter 扩展插件 主要用来渲染lay-sort生成过滤表单
 @Author: chenxiaoshun
 @Date : 2018-11-12
 */
layui.define(['myUrl'], function (exports) {
    let MOD_NAME = 'myFilter';
    let $ = layui.jquery;
    let myUrl = layui.myUrl;

    let Filter = function (table) {
        this.table = table;
        this.tipIndex = 0;
        let that = this;
        this.thDoms = table.find('thead tr > th[lay-tfilter]');
        $.each(this.thDoms, function () {
            that.init($(this));
        });
    };

    Filter.prototype.init = function (thDom) {
        // let that = this;
        let thWrapDom = thDom.children('.th-wrap');
        let filterDom = $('<div class="th-action-filter"></div>');
        let iconDom = $('<svg viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg"><path d="M889.6 177.066667 618.666667 448l0 247.466667c0 8.533333-6.4 17.066667-12.8 19.2 0 0 0 2.133333-2.133333 2.133333L445.866667 874.666667c-4.266667 6.4-10.666667 12.8-19.2 12.8 0 0 0 0 0 0-6.4 0-10.666667-2.133333-17.066667-6.4-2.133333-2.133333-2.133333-2.133333-2.133333-4.266667C405.333333 870.4 405.333333 868.266667 405.333333 864L405.333333 445.866667 134.4 174.933333c0 0 0 0 0 0C130.133333 170.666667 128 166.4 128 160 128 153.6 130.133333 149.333333 134.4 145.066667c0 0 0 0 0 0 4.266667-4.266667 12.8-6.4 19.2-6.4L874.666667 138.666667c0 0 2.133333 0 2.133333 0 2.133333 0 4.266667 0 6.4 2.133333 2.133333 0 2.133333 2.133333 2.133333 2.133333 2.133333 0 2.133333 2.133333 4.266667 2.133333C898.133333 153.6 898.133333 168.533333 889.6 177.066667zM202.666667 181.333333l238.933333 238.933333c4.266667 4.266667 6.4 10.666667 6.4 17.066667L448 810.666667l125.866667-125.866667c0 0 2.133333-2.133333 2.133333-2.133333L576 437.333333c0 0 0-2.133333 0-2.133333 0-4.266667 2.133333-10.666667 6.4-14.933333L823.466667 181.333333 202.666667 181.333333z"></path></svg>');
        filterDom.append(iconDom);
        thWrapDom.append(filterDom);

        // 事件需要阻止冒泡, 防止绑定的相同事件被重复触发
        thDom.on("mouseenter mouseleave", function (e) {
            // let self = $(this);
            // 过滤表单打开的时候不触发hover事件
            if ($(e.target).parents('.th-action-filter-form').length) {
                return false;
            }
            switch (e.type) {
                case 'mouseenter':
                    iconDom.addClass('icon-hover');
                    break;
                case 'mouseleave':
                    layer.close(this.tipIndex);
                    iconDom.removeClass('icon-hover');
                    break;
            }
            e.stopPropagation();
        });

        thDom.on('click', function (e) {
            let self = $(this);
            let formClassName = '.th-action-filter-form';
            // 事件阻止冒泡 .th-action-filter-form, 防止重复触发
            // 如果目标 e.target 是 filter-form 或者其子元素, 阻止冒泡, 不阻止会导致点击意外关闭掉 filter 表单
            let targetDom = $(e.target);
            if (targetDom.parents(formClassName).length || targetDom.hasClass(formClassName.substr(1))) {
                return false;
            }
            // 当本列的过滤表单已经显现的时候, 再点击就关闭
            let formDom = self.find(formClassName);
            // console.log(formDom);
            if (formDom.is(':hidden')) {
                $(formClassName).hide();
                formDom.toggle();
            } else {
                formDom.toggle();
            }
            e.stopPropagation();
        });

        /*
        *   filter form 提交
        *   新打开的表单不自动选中历史选中的参数
        *   当新表单提交后, 需要删除同name的历史选中参数
        *   不同name的历史参数依旧保留
        * */
        thDom.find('button[lay-submit]').on('click', function () {
            let self = $(this);
            let form = self.parents('.layui-form');
            let argArray = form.serializeArray();
            let url = myUrl(location.href);
            let flushState = true;
            // console.log('location.href======', location.href);
            // console.log('pre url======', url);
            // console.log('argArray======', argArray);
            // 遍历表单提交的数据
            $.each(argArray, function (k, v) {
                let name = v.name;
                delete url.args['page'];
                if (flushState) {
                    delete url.args[name];
                    flushState = false;
                }
                if (!url.args[name]) {
                    url.args[v.name] = new Set();
                }
                url.args[v.name].add(v.value);
            });
            layer.load();
            // console.log('url======', url);
            location.href = url.encode();
        });

        thDom.find('button[type="reset"]').on('click', function () {
            let self = $(this);
            let form = self.parents('.layui-form');
            let url = myUrl(window.location.href);
            let name = form.find('input[type="checkbox"]').attr('name');
            // console.log('url.args========', url.args);
            // console.log('name========', name);
            delete url.args[name];
            location.href = url.encode();
        });
    };


    //输出接口
    exports(MOD_NAME, function (table) {
        switch (typeof table) {
            case "undefined":
                table = $('table.layui-table');
                break;
            case "string":
                table = $(table);
                break;
        }

        // 防止同时多个表格, 多个lay-sort渲染 冲突的问题
        $.each(table, function () {
            new Filter($(this))
        });
    });
});