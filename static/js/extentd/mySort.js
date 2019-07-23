/**
 @Name : mySort 扩展插件 主要用来渲染生成排序按钮
 @Author: chenxiaoshun
 @Date : 2018-11-12
 */
layui.define(['myLayer'], function (exports) {
    let MOD_NAME = 'mySort';
    let $ = layui.jquery;
    let layer = layui.myLayer();

    let Sort = function (table) {
        this.tipIndex = 0;
        this.table = table;
        this.thDoms = table.find('thead tr > th[lay-sort]');
        var that = this;
        $.each(this.thDoms, function () {
            that.init($(this));
        });
    };

    Sort.prototype.init = function (thDom) {
        let that = this;
        let thWrapDom = thDom.children('.th-wrap');
        let sortDom = $('<div class="th-action-sort"></div>');
        let iconDom = $('<i class="sort-icon sort-icon-up"></i><i class="sort-icon sort-icon-down"></i>');
        sortDom.append(iconDom);
        thWrapDom.append(sortDom);

        iconDom.on("mouseover mouseout", function (e) {
            let self = $(this);

            let isUpIcon = self.hasClass("sort-icon-up");
            switch (e.type) {
                case 'mouseover':
                    isUpIcon ? self.addClass('sort-icon-hover-up icon-hover') : self.addClass('sort-icon-hover-down icon-hover');
                    break;
                case 'mouseout':
                    isUpIcon ? self.removeClass('sort-icon-hover-up icon-hover') : self.removeClass('sort-icon-hover-down icon-hover');
                    break;
            }
            e.stopPropagation();
        });

        iconDom.on('click', function (e) {
            let self = $(this);
            // 初始化其他兄弟节点
            that.thDoms.find('.sort-icon').removeClass(
                'sort-icon-hover-up sort-icon-hover-down sort-icon-selected-up sort-icon-selected-down'
            );

            let isReverse = false;
            switch (self.hasClass("sort-icon-up")) {
                case true:
                    isReverse = true;
                    $(this).addClass('sort-icon-selected-up');
                    break;
                default:
                    $(this).addClass('sort-icon-selected-down');
                    break;
            }

            let index = thDom.index();
            // 判断此列是否排序过
            that.handle(index, that.table.find('tbody'), isReverse);
            e.stopPropagation();
        });
    };

    Sort.prototype.handle = function (index, tbody, isReverse) {
        let tr = tbody.children('tr');
        let arr = $.makeArray(tr);
        let that = this;
        arr.sort(function (a, b) {
            return that._compare(index, a, b);
        });
        if (isReverse) {
            arr.reverse();
        }
        tbody.html(arr);
    };


    let dataTypeRegList = [
        [/^[0-9. ]*%$/, '_percentToNumber'],
        [/^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$/, '_ipToNumber'],
        [/^(\d{4})\-(\d{2})\-(\d{2}) (\d{2}):(\d{2}):(\d{2})$/, '_dateToNumber'],
        [/^[0-9.]*$/, '_stringToNumber'],
        [/^[0-9.]*$/, '_stringToNumber'],
    ];
    Sort.prototype._compare = function (index, a, b) {
        let aText = _getText(a, index);
        let bText = _getText(b, index);
        let func;
        $.each(dataTypeRegList, function (k, v) {
            if (eval(v[0]).test(aText)) {
                // console.log(v);
                func = eval(v[1]);
                return false;
            }
        });
        if (func) {
            let aVal = func(aText);
            let bVal = func(bText);
            return bVal - aVal;
        } else {
            return _defaultToNumber(bText) - _defaultToNumber(aText);
        }
    };

    let _defaultToNumber = function (str) {
        return str.replace(/[^0-9.]/ig, '')
    };

    let _dateToNumber = function (date) {
        return Date.parse(date);
    };

    let _percentToNumber = function (percent) {
        return parseFloat(percent);
    };

    let _stringToNumber = function (str) {
        return parseFloat(str);
    };

    let _ipToNumber = function (ip) {
        ip = $.trim(ip);
        let num = 0;
        if (ip === "") {
            return num;
        }
        let aNum = ip.split(".");
        if (aNum.length !== 4) {
            return num;
        }
        num += parseInt(aNum[0]) << 24;
        num += parseInt(aNum[1]) << 16;
        num += parseInt(aNum[2]) << 8;
        num += parseInt(aNum[3]) << 0;
        //这个很关键，不然可能会出现负数的情况
        num = num >>> 0;
        return num;
    };

    function _getText(dom, index) {
        return $(dom).children('td').eq(index).text();
    }

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
            new Sort($(this))
        });
    });
});
