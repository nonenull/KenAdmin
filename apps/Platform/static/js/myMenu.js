layui.define(['element'], function (exports) {
    $ = layui.jquery;
    let element = layui.element;

    function Menu(dom) {
        this.menuDom = $(dom);
        this.menuWidth = $(dom).width();
    }

    Menu.prototype.load = function (menu, parentDom, level) {
        let that = this;
        menu = menu || menuJson;
        parentDom = parentDom || this.menuDom;
        level = level || 1;

        $.each(menu, function (k, v) {
            let curDom;
            let childDom;
            let curMenu = v;
            let menuUrl = curMenu.url;
            let menuName = curMenu.display;
            let curMenuChild = curMenu.child;
            if (level === 1) {
                curDom = $('<li class="layui-nav-item"></li>');
                if (curMenuChild) {
                    childDom = $('<dl class="layui-nav-child"></dl>')
                }
            } else {
                curDom = $('<dd></dd>');
                childDom = $('<dl class="layui-nav-child"></dl>');
            }
            curDom.prepend('<a href="' + menuUrl + '">' + menuName + '</a>');
            parentDom.append(curDom);
            if (curMenuChild) {
                curDom.append(childDom);
                that.load(curMenuChild, childDom, level + 1);
            }
        });
    };

    exports('myMenu', function (dom) {
        let menu = new Menu(dom);
        menu.load();
        element.init('nav');
    });
});