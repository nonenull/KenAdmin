/**
 @Name : myTable 扩展插件 主要用来渲染生成 table的多选, 和右键按钮
 @Author: chenxiaoshun
 @Date : 2018-11-12
 */
layui.define(['jquery', 'myLayer'], function (exports) {
    let $ = layui.jquery;
    let mLayer = layui.myLayer();

    const dataIdAttr = 'data-id';
    const dataNameAttr = 'data-name';
    const checkerSelectedClass = "layui-form-checked";
    const checkerBtnClass = "my-checkbox-btn";
    const checkerCtlBtnClass = "my-checkbox-control-btn";

    tableArr = [];

    function TableChecker(dom) {
        this.tableDom = dom;
        this.selectAllStatus = false;
    }

    TableChecker.prototype.getSelect = function () {
        let idList = [];
        let nameList = [];
        let domList = this.tableDom.find('tbody tr').has('.' + checkerSelectedClass);
        $.each(domList, function (k, v) {
            idList.push($(this).attr(dataIdAttr));
            nameList.push($(this).attr(dataNameAttr));
        });
        return {
            // ids: (idList.length === 1) ? idList[0] : idList,
            // names: (nameList.length === 1) ? nameList[0] : nameList,
            ids: idList,
            names: nameList,
            length: idList.length,
            dom: this.tableDom.find('tbody tr').has('.' + checkerSelectedClass),
        };
    };

    TableChecker.prototype.select = function (id) {
        this.getcheckboxDom(id).toggleClass(checkerSelectedClass);
        this.getTrDom(id).toggleClass(tableTrSelectedClass)
    };

    TableChecker.prototype.selectAll = function () {
        let dom = this.getcheckboxDom(undefined, true);
        let trDom = this.getTrDom(undefined, true);
        if (!this.selectAllStatus) {
            dom.addClass(checkerSelectedClass);
            trDom.addClass(tableTrSelectedClass);
            this.selectAllStatus = true;
        } else {
            dom.removeClass(checkerSelectedClass);
            trDom.removeClass(tableTrSelectedClass);
            this.selectAllStatus = false;
        }
    };

    TableChecker.prototype.selectAllCancel = function () {
        // 取消打勾和选中效果
        this.getcheckboxDom(undefined, true).removeClass(checkerSelectedClass);
        this.getTrDom(undefined, true).removeClass(tableTrSelectedClass);
    };

    TableChecker.prototype.reverseSelect = function () {
        this.getcheckboxDom(undefined, true).toggleClass(checkerSelectedClass);
    };

    TableChecker.prototype.getTrDom = function (id, ctl) {
        let ctlState = !!ctl;
        let selectorDom = ctlState ? 'tr' : 'tbody tr';

        let findDom = id ? selectorDom + '[' + dataIdAttr + '=' + id + ']' : selectorDom;
        return this.tableDom.find(findDom);
    };

    TableChecker.prototype.getcheckboxDom = function (id, ctl) {
        let ctlState = !!ctl;
        let dom = id ? this.getTrDom(id, ctlState) : this.getTrDom(undefined, ctlState);
        return dom.find("." + checkerBtnClass);
    };

    /*
    *   监听 table tbody tr元素点击事件, 点击后选中相应的行
    * */
    TableChecker.prototype.startListen = function () {
        let self = this;
        // my-checkbox-btn 自定义 checkbox按钮，无需form标签
        // 点击 选中框, 则选中当前行
        self.tableDom.on('click', "tbody tr", function (e) {
            let dom = $(this);
            // 禁止全选键点击在此处被触发.
            let id = dom.attr(dataIdAttr);
            self.select(id);
        });

        /*
        * 监听全选按钮的鼠标按下事件, 左键点击为全选, 右键为反选
        * 左键单击 checkbox控制按钮，则table下td 所有checkbox都选中
        * */
        self.tableDom.on('mousedown', '.' + checkerBtnClass + '.' + checkerCtlBtnClass, function (e) {
            switch (e.which) {
                case 1:
                    self.selectAll();
                    break;
                case 3:
                    self.reverseSelect();
                    break;
            }
        });
    };


    const tableTrSelectedClass = 'my-table-this';

    function TableContextMenu(config, checker) {
        this.config = config;
        this.checker = checker;
        this.tableDom = config.dom;
        this.contextMenuDom = $('<div class="layui-btn-container my-table-right-tab layui-anim layui-anim-scaleSpring"></div>');
        $('.my-container').append(this.contextMenuDom);
    }

    TableContextMenu.prototype.generatebtn = function () {
        let that = this;
        let colorArr = [
            'layui-btn-warm',
            'layui-btn-normal',
            'layui-btn-danger',
            'layui-btn-primary',
        ];
        // console.log('start to generatebtn');
        $.each(that.config.btn, function (k, v) {
            let color = v.color || colorArr[k];
            let buttonDom = $('<button class="layui-btn ' + color + '">' + v.name + '</button>');
            //console.log('contextMenuDom===========', that.contextMenuDom);
            that.contextMenuDom.append(buttonDom);
            buttonDom.on('click', function () {
                if (!v.url) {
                    mLayer.warning('功能未开放.');
                    return false;
                }
                v.callback(that.checker);
            })
        })
    };

    TableContextMenu.prototype.open = function () {
        this.contextMenuDom.show()
    };

    TableContextMenu.prototype.close = function () {
        this.contextMenuDom.hide();
        this.checker.selectAllCancel();
    };

    TableContextMenu.prototype.startListen = function () {
        let self = this;

        // 代理 table 的右键打开 菜单
        this.contextMenuDom.on('contextmenu', function (e) {
            return false;
        });

        self.tableDom.on('contextmenu', function (e) {
            let curDom = $(e.target);
            //console.log('curDom===', curDom);
            if (curDom.parents('thead').length) {
                //console.log('curDom===has parents');
                return false;
            }
            self.checker.selectAllCancel();
            self.close();
            // 选中行
            let selectdDom = curDom.parents('tr');
            self.checker.select(
                selectdDom.attr(dataIdAttr)
            );

            // let tabOffsetTop = e.pageY || e.clientY + document.body.scrollTop;
            let tabOffsetTop = selectdDom.offset().top || e.clientY + document.body.scrollTop;
            let tabOffsetLeft = e.pageX || e.clientX + document.body.scrollLeft;
            // console.log('top偏移 ', tabOffsetTop, '左偏移', tabOffsetLeft);
            // 设置右键菜单位置
            self.contextMenuDom.css({
                'top': tabOffsetTop + (selectdDom.height() / 2) - (self.contextMenuDom.height() / 2),
                'left': tabOffsetLeft + (self.contextMenuDom.width() - 20),
            });
            self.checker.getSelect().dom.addClass(tableTrSelectedClass);
            self.open();
            return false;
        });

        /*
        * 点击空白处 隐藏按钮组
        * 判断 子菜单是否可见, 如果不可见, 则不处理, 否则会跟 选中框的点击事件冲突
        * */
        self.tableDom.on('click', function (e) {
            var isContextMenuHidden = self.contextMenuDom.is(":hidden");
            if (isContextMenuHidden) {
                return false;
            }
            self.close();
            e.stopPropagation();
        });
    };

    /** 防止重复 **/
    function check(dom) {
        let obj;
        $.each(tableArr, function (k, v) {
            if (dom.is(v.dom)) {
                obj = v;
                return false;
            }

        });
        return obj;
    }

    //输出接口
    exports('myTable', function (config) {
        // console.trace()
        config = config || {};
        let dom = config.dom = (config.dom || $('.layui-table').has('.my-checkbox-btn'));
        config.btn = (config.btn || []);

        if (typeof dom === "string") {
            dom = $(dom);
        }

        if (config.callback) {
            // console.log('存在回调函数');
            let timer;
            timer = setInterval(function () {
                let existObj = check(dom);
                if (existObj) {
                    // console.log('开始执行回调');
                    config.callback(existObj);
                    clearInterval(timer);
                }
            }, 4);
            return
        }
        let existObj = check(dom);
        if (existObj) {
            // console.log('myTable被重复执行, 返回缓存');
            return existObj;
        }

        let c = new TableChecker(dom);
        c.startListen();

        let cm = new TableContextMenu(config, c);
        cm.generatebtn();
        cm.startListen();

        let tableObj = {
            dom: dom,
            checker: c,
            contextMenu: cm,
        };
        tableArr.push(tableObj);

        return tableObj;
    });
});
