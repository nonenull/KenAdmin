/**
 @Name : 在原有tree组件的基础上做出二次修改
 @Author: chenxiaoshun
 @Date : 2018-11-12
 */
layui.define('jquery', function (exports) {
    "use strict";
    let $ = layui.jquery;
    let hint = layui.hint();
    let timer;

    let enterSkin = 'layui-tree-enter', Tree = function (options) {
        this.options = options;
    };

    //图标
    const icon = {
        arrow: ['&#xe623;', '&#xe625;'] //箭头
        , checkbox: ['&#xe626;', '&#xe627;'] //复选框
        , radio: ['&#xe62b;', '&#xe62a;'] //单选框
        // , branch: ['&#xe622;', '&#xe624;'] //父节点
        , branch: ['&#xe655;', '&#xe65f;'] //父节点
        , leaf: '&#xe621;' //叶节点
    };

    //初始化
    Tree.prototype.init = function (elem) {
        let that = this;
        elem.addClass('layui-box layui-tree'); //添加tree样式
        if (that.options.skin) {
            elem.addClass('layui-tree-skin-' + that.options.skin);
        }
        that.tree(elem);
        that.on(elem);
    };

    //树节点解析
    Tree.prototype.tree = function (elem, children) {
        let that = this, options = that.options;
        let nodes = children || options.nodes;

        layui.each(nodes, function (index, item) {
            // console.log('index===',index,'item====', item);
            let hasChild = item.child && item.child.length > 0;
            // console.log('item.hasChild==', item.child);
            let ul = $('<ul class="' + (item.spread ? "layui-show" : "") + '"></ul>');
            let li = $(['<li ' + (item.spread ? 'data-spread="' + item.spread + '"' : '') + '>'
                //复选框/单选框
                , function () {
                    let check = options.check;
                    let html = '';
                    if (check) {
                        // console.log('$.inArray(item.name, checkList)====', $.inArray(item.name, options.checkList));
                        let checkList = options.checkList ? options.checkList : [];
                        let index = checkList.findIndex((checkItem) => {
                            let state = true;
                            $.each(checkItem, function (k, v) {
                                if (v !== item[k]) {
                                    console.log(v, " !!==", item[k]);
                                    state = false;
                                    return false;
                                }
                            });
                            return state;
                        });
                        let checked = (index > -1) ? 'checked' : '';
                        //`($.inArray(item.id, checkList),item.id,checkList);
                        let fullname = (item.namespace || "") + ':' + item.name;
                        switch (check) {
                            case 'checkbox':
                                html = '<input type="checkbox" name="tree" value="' + fullname + '" ' + checked + '>';
                                break;
                            case 'radio':
                                html = '<input type="radio" name="tree" value="' + fullname + '" ' + checked + '>';
                                break;
                        }
                    }
                    return html;
                }()
                //展开箭头
                , function () {
                    return hasChild ? '<i class="layui-icon layui-tree-spread">' + (
                        item.spread ? icon.arrow[1] : icon.arrow[0]
                    ) + '</i>' : '';
                }()
                //节点
                , function () {
                    return '<a href="' + (item.href || 'javascript:;') + '" ' + (
                            options.target && item.href ? 'target=\"' + options.target + '\"' : ''
                        ) + '>'
                        + ('<i class="layui-icon layui-tree-' + (hasChild ? "branch" : "leaf") + '">' + (
                            hasChild ? (
                                item.spread ? icon.branch[1] : icon.branch[0]
                            ) : icon.leaf
                        ) + '</i>') //节点图标
                        + ('<cite>' + (item.display || '未命名') + '</cite></a>');
                }()

                , '</li>'].join(''));

            //如果有子节点，则递归继续生成树
            if (hasChild) {
                li.append(ul);
                that.tree(ul, item.child);
            }

            elem.append(li);
            // 有选中的checkbox的话 下拉菜单
            that.slideChecked(li);

            //触发点击节点回调
            typeof options.click === 'function' && that.click(li, item);

            //伸展节点
            that.spread(li, item);

            //拖拽节点
            options.drag && that.drag(li, item);
        });
    };

    // 针对已经预先选中的菜单，直接显示下拉状态
    Tree.prototype.slideChecked = function (elem) {
        //elem.find('input[type="checkbox"]:checked').parents('ul').addClass('layui-show');
        let liDom = elem.find('input[type="checkbox"]:checked').parents('li');
        let ul = liDom.children('ul');
        let a = ul.prev('a');
        let arrow = liDom.children('.layui-tree-spread');

        liDom.data('spread', true);
        ul.addClass('layui-show');
        arrow.html(icon.arrow[1]);
        a.find('.layui-icon').html(icon.branch[1]);
    };

    //点击节点回调
    Tree.prototype.click = function (elem, item) {
        let that = this, options = that.options;
        let aDom = elem.children('a');
        aDom.on('click', function (e) {
            let dom = $(this);
            timer && clearTimeout(timer);
            timer = setTimeout(function () {
                $(options.elem).find('.tree-focused').removeClass('tree-focused');
                dom.addClass('tree-focused');
                layui.stope(e);
                options.click(item, dom);
            }, 200);
        });
    };

    //伸展节点
    Tree.prototype.spread = function (elem, item) {
        let that = this, options = that.options;
        let arrow = elem.children('.layui-tree-spread');
        let ul = elem.children('ul'), a = elem.children('a');

        //执行伸展
        open = function () {
            if (elem.data('spread')) {
                elem.data('spread', null);
                ul.removeClass('layui-show');
                arrow.html(icon.arrow[0]);
                a.find('.layui-icon').html(icon.branch[0]);
                // tree菜单关闭后，调用closed回调
                if (options.closed) options.closed(item);
            } else {
                elem.data('spread', true);
                ul.addClass('layui-show');
                arrow.html(icon.arrow[1]);
                a.find('.layui-icon').html(icon.branch[1]);
                // tree菜单打开后，调用opened回调
                if (options.opened) options.opened(item);
            }
        };

        //如果没有子节点，则不执行
        if (!ul[0]) return;

        arrow.on('click', open);

        // 此处加timer是为了防止 单击和双击时间的冲突
        a.on('dblclick', function () {
            timer && clearTimeout(timer);
            open();
        });
    };

    //通用事件
    Tree.prototype.on = function (elem) {
        let that = this, options = that.options;
        let dragStr = 'layui-tree-drag';

        //屏蔽选中文字
        elem.find('i').on('selectstart', function (e) {
            return false
        });

        //拖拽
        if (options.drag) {
            $(document).on('mousemove', function (e) {
                let move = that.move;
                if (move.from) {
                    let to = move.to, treeMove = $('<div class="layui-box ' + dragStr + '"></div>');
                    e.preventDefault();
                    let dragDom = $('.' + dragStr);
                    dragDom[0] || $('body').append(treeMove);
                    let dragElem = dragDom[0] ? dragDom : treeMove;
                    (dragElem).addClass('layui-show').html(move.from.elem.children('a').html());
                    dragElem.css({
                        left: e.pageX + 10
                        , top: e.pageY + 10
                    })
                }
            }).on('mouseup', function () {
                let move = that.move;
                if (move.from) {
                    move.from.elem.children('a').removeClass(enterSkin);
                    move.to && move.to.elem.children('a').removeClass(enterSkin);
                    that.move = {};
                    $('.' + dragStr).remove();
                }
            });
        }

        // 监听处理checkbox
        if (options.check === 'checkbox') {
            let _checkbox = 'input[type="checkbox"]';
            $(document).on('change', _checkbox, function (e) {
                let dom = $(this);
                let isChecked = e.target.checked;
                dom.nextAll('ul').find(_checkbox).prop('checked', isChecked);
                let showDom = dom.parents('.layui-show');

                if (isChecked) {
                    showDom.prevAll(_checkbox).prop('checked', true);
                } else if (dom.parent().siblings().children(_checkbox + ':checked').length === 0) {
                    showDom.prevAll(_checkbox).prop('checked', false);
                }
            });
        }
    };

    //拖拽节点
    Tree.prototype.move = {};
    Tree.prototype.drag = function (elem, item) {
        let that = this, options = that.options;
        let a = elem.children('a'), mouseenter = function () {
            let othis = $(this), move = that.move;
            if (move.from) {
                move.to = {
                    item: item
                    , elem: elem
                };
                othis.addClass(enterSkin);
            }
        };
        a.on('mousedown', function () {
            let move = that.move;
            move.from = {
                item: item
                , elem: elem
            };
        });
        a.on('mouseenter', mouseenter).on('mousemove', mouseenter)
            .on('mouseleave', function () {
                let othis = $(this), move = that.move;
                if (move.from) {
                    delete move.to;
                    othis.removeClass(enterSkin);
                }
            });
    };

    //暴露接口
    exports('myTree', function (options) {
        let tree = new Tree(options = options || {});
        let elem = $(options.elem);
        if (!elem[0]) {
            return hint.error('layui.tree 没有找到' + options.elem + '元素');
        }
        tree.init(elem);
    });
});