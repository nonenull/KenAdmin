layui.define(['element'], function (exports) {
    let element = layui.element;

    function Tab() {
        this.loadDom = $(`
            <div id="loading">
                <div class="loading-mask">
                    <i class="layui-icon layui-anim layui-anim-rotate layui-anim-loop">&#xe63e;</i>
                    <span>loading...</span>
                </div>
            </div>
        `);
    }

    Tab.prototype.add = function (name, url) {
        let that = this;
        let tabFrame = that.setIframe(url);
        if (!that.isTabExist(name)) {
            element.tabAdd('body', {
                title: '<span>' + name + '</span>', id: name, content: tabFrame,
            });

            let tabContent = $('.custom-body .layui-tab-content .layui-tab-item').last();
            let curIframe = tabContent.find('iframe');
            tabContent.append(this.loadDom);
            that.loadDom.show();
            curIframe.on('load', function () {
                that.loadDom.hide(100);
                that.loadDom.remove();
            });
        }
        // 切换到目标标签
        element.tabChange('body', name);
        // 滚动条移动到目标标签
        let tabDom = $('.custom-body .layui-tab-title');
        let tabLiDom = tabDom.find('li[lay-id="' + name + '"]');
        tabDom.animate({'scrollLeft': tabLiDom.offset().left}, 100);
    };

    Tab.prototype.setIframe = function (url) {
        return '<iframe src="' + url + '" frameborder="0" scrolling="yes" class="content-frame"></iframe>'
    };

    Tab.prototype.isTabExist = function (name) {
        let tabDom = $('.layui-tab[lay-filter="body"]').find('li[lay-id="' + name + '"]');
        return tabDom.length > 0 && true || false;
    };

    Tab.prototype.listen = function () {
        let that = this;

        // 阻止 tab右键菜单 默认鼠标右键
        $(document).on('contextmenu', '.custom-body .layui-tab-brief .layui-tab-title, .layui-tab-right-click-menu dd', function (e) {
            return false;
        });
        // tab右键菜单
        $(document).on('mousedown', '.custom-body .layui-tab-brief .layui-tab-title li', function (e) {
            // 1 = 鼠标左键 left; 2 = 鼠标中键; 3 = 鼠标右键
            // 打开前初始化一下
            let tabRightClickMenu = $('.layui-tab-right-click-menu');
            tabRightClickMenu.hide();
            let dom = $(this);
            switch (e.which) {
                case 3:
                    // console.log('===',e.which);
                    // 获取标签的标题 宽度
                    let tabWidth = dom.outerWidth();
                    let tabOffsetLeft = dom.offset().left;
                    // console.log('tab宽度',tabWidth,'左偏移',tabOffsetLeft);

                    // 设置右键菜单位置
                    tabRightClickMenu.css({
                        'width': tabWidth, 'left': tabOffsetLeft
                    });
                    // 给 右键菜单插入标识
                    let layId = dom.attr('lay-id');
                    // console.log('获得tab id',layId);
                    tabRightClickMenu.attr('lay-filter', layId);
                    tabRightClickMenu.show();
                    e.stopPropagation();
                    break;
                default:
                    return true;
            }
        });

        // 点击空白处 隐藏 tab右键菜单
        $(document).on('mousedown', function (e) {
            let tabRightClickMenu = $('.layui-tab-right-click-menu');
            tabRightClickMenu.hide();
            return false;
        });

        // 监听 右键菜单 子按钮的 鼠标点击事件
        $('.layui-tab-right-click-menu dd').on('mousedown', function (e) {
            let self = $(this);
            let layid = self.parent('dl').attr('lay-filter');
            let linkType = self.children('a').text();
            switch (linkType) {
                case '刷新':
                    element.tabChange('body', layid);
                    let item = $('.custom-body .layui-tab-content .layui-show');
                    let iframe = item.find('iframe');
                    iframe.attr('src', iframe.attr('src'));
                    item.find('#loading').show();
                    // iframe[0].contentWindow.location.reload();
                    // item.find('#loading').show();
                    break;
                case '新标签页打开':
                    let index_num = $('.custom-body .layui-tab-title li[lay-id="' + layid + '"]').index();
                    // 获取标签页的content，然后获取iframe的url
                    let content_dom = $('.custom-body .layui-tab-content .layui-tab-item').get(index_num);
                    let url = $(content_dom).find('iframe')[0].contentWindow.location.href;
                    window.open(url, '_blank');
                    // element.tabDelete('body', layid);
                    break;
                case '关闭':
                    element.tabDelete('body', layid);
                    break;
            }
        });

        // 用户菜单
        $('.header .layui-nav-item dl a').on('click', function (e) {
            let thisDom = $(e.target);
            let href = thisDom.attr('href');
            let name = thisDom.text().split(' ')[1];
            switch (name) {
                case '注销':
                    layer.msg('退出登录，欢迎下次回来');
                    setTimeout(function () {
                        location.href = href;
                    }, 800);
                    break;
                default:
                    that.add(name, href);
                    break;
            }
            return false;
        });

    };

    exports('myTab', function () {
        let tab = new Tab();
        tab.listen();
        return tab;
    });
});