/**
 @Name : mySSH 主要用来web terminal
 @Author: chenxiaoshun
 @Date : 2019-04-16
 */

layui.define(['jquery', 'layer'], function (exports) {
    let MOD_NAME = 'mySSH';
    let $ = layui.jquery;
    let layer = layui.layer;
    let mainDom = $('<div class="layui-row layui-col-space15 my-webssh">');
    let toolBarDom = $(`
        <div class="layui-col-xs12 layui-col-sm12 layui-col-md12 my-webssh-tool">
            <div class="layui-btn-group">
              <button class="layui-btn layui-btn-sm" title="刷新页面">
                <i class="layui-icon layui-icon-refresh-3"></i>
              </button>
              <button class="layui-btn layui-btn-sm" title="置顶">
                <i class="layui-icon layui-icon-up"></i>
              </button>
              <button class="layui-btn layui-btn-sm" title="置底">
                <i class="layui-icon layui-icon-down"></i>
              </button>
              <button class="layui-btn layui-btn-sm" title="清空屏幕">
                <i class="layui-icon layui-icon-file"></i>
              </button>
            </div>
        </div>    
    `);

    let termDom = $(`
        <div class="layui-col-xs12 layui-col-sm12 layui-col-md10">
            <div class="layui-row layui-col-space15">
                <div class="layui-col-xs12 layui-col-sm12 layui-col-md12 my-webssh-term"></div>
            </div>
        </div>
    `);
    let historyDom = $('<div class="layui-col-xs12 layui-col-sm12 layui-col-md2 my-webssh-history">');

    let mySSH = function (conf) {
        let defaultConf = {
            unique: 0, elem: '', socketUrl: '', args: '', toolBar: true, historyBar: true, readonly: false, termConf: {},
        };
        this.conf = $.extend({}, defaultConf, conf);

        this.elem = $(this.conf.elem);
        // 根据配置加载html
        if (this.conf.toolBar === true) {
            termDom.find('.my-webssh-term').before(toolBarDom);
        }
        mainDom.append(termDom);
        if (this.conf.historyBar === true) {
            mainDom.append(historyDom);
        }
        this.elem.append(mainDom);
        this.getTermSize();

        this.initPanel();
        this.init();
        this.listen();
        this.cmdCacheTableName = 'ssh-history';
        this.cmd = '';
    };

    /*
    * 初始化 elem
    * */
    mySSH.prototype.initPanel = function () {
        this.elem.append();
    };

    mySSH.prototype.init = function () {
        let that = this;
        this.initState = true;
        let cols = that.cols;
        let rows = that.rows;
        that.term = new Terminal($.extend({
            cols: cols, rows: rows, useStyle: true, cursorBlink: true, fontSize: 14,
        }, that.conf.termConf));
        that.term.open(termDom.get(0));
        that.term.writeln("connecting to host ...");
        window.term = that.term;
        let protocol = (location.protocol === 'https:') ? 'wss://' : 'ws://';
        let socketURL = protocol + location.hostname + ((location.port) ? (':' + location.port) : '') + this.conf.socketUrl + '?width=' + cols + '&height=' + rows + '&' + this.conf.args;
        that.socket = new WebSocket(socketURL);
    };

    mySSH.prototype.listen = function () {
        let that = this;
        that.socket.addEventListener('open', function () {
            //that.term.open(termDom.get(0));
            historyDom.height(termDom.height());
        });

        // 监听 websocket 来消息
        that.socket.addEventListener('message', function (recv) {
            let data = JSON.parse(recv.data);
            let message = data.message;
            // console.log('收到消息 ===========', message);

            let status = data.status;
            if (that.initState === true && status === 0) {
                that.term.writeln("connected, open terminal ...");
                that.initState = false;
            }
            that.term.write(message)
        });

        // 监听 websocket 关闭
        that.socket.addEventListener('close', function (event) {
            that.term.write(`\r\nconnection closed, code: ${event.code} , reason: ${event.reason || 'none'}\r\n`)
        });


        // 监听 term 输入
        that.term.on('data', function (data) {
            if (that.conf.readonly === true) {
                layer.msg('此终端为只读模式.');
                return;
            }
            // console.log("term 输入数据 ======== ", data);
            let sendData = that.generateMsg(0, data, {
                'cols': that.cols, 'rows': that.rows
            });

            that.socket.send(sendData);
            switch (data) {
                // 按下回车代表 命令完成发出
                case '':
                    break;
                case '\r':
                    if (that.cmd === '') {
                        break;
                    }
                    that.addHistory(that.cmd);
                    // console.log('this.cmd========', that.cmd);
                    that.cmd = '';
                    break;
                case '\x7f':
                    that.cmd = that.cmd.slice(0, -1);
                    break;
                default:
                    that.cmd += data;
            }
        });

        $(window).resize(function () {
            that.getTermSize();
            let sendData = that.generateMsg(1, null, {
                'cols': that.cols, 'rows': that.rows
            });

            that.socket.send(sendData);
            that.term.resize(that.cols, that.rows)
        });

        $(document).on('click', '.my-webssh-history > p', function () {
            let self = $(this);
            let data = self.text();
            // console.log('history ===', data, that.term);
            // that.term.write(txt);
            that.socket.send(that.generateMsg(0, data));
        });

        $(document).on('click', '.my-webssh-tool button', function () {
            // console.log('term==', that.term);
            let self = $(this);
            let title = self.attr('title');
            switch (title) {
                case '刷新页面':
                    location.reload();
                    break;
                case '清空屏幕':
                    that.term.clear();
                    break;
                case '置顶':
                    that.term.scrollToTop();
                    break;
                case '置底':
                    that.term.scrollToBottom();
                    break;
            }
        });

        /*
        * 1001	Going Away
        * The endpoint is going away,
        * either because of a server failure or because the browser is navigating away from the page that opened the connection.
        * */
        $(window).on('beforeunload', function () {
            that.socket.close(4444, '刷新或离开此页面');
        });
    };

    mySSH.prototype.generateMsg = function (status, data, extend) {
        let message = {'status': status, 'data': data};
        if (extend) {
            message = $.extend(message, extend);
        }
        let sendData = JSON.stringify(message);
        // console.log('senddata====', sendData);
        return sendData;
    };

    mySSH.prototype.getTermSize = function () {
        let that = this;
        let initWidth = 9;
        let initHeight = 17;
        let windowsWidth = termDom.width();
        let windowsHeight = termDom.height() || 500;
        // console.log('windowsWidth=====', windowsWidth);
        // console.log('windowsHeight=====', windowsHeight);
        this.cols = Math.floor(windowsWidth / initWidth);
        this.rows = Math.floor(windowsHeight / initHeight);
        return {
            cols: that.cols, rows: that.rows,
        }
    };

    mySSH.prototype.addHistory = function (cmd) {
        let that = this;
        historyDom.prepend('<p>' + cmd + '</p>');
        // 存入缓存
        let cmdHistory = layui.data(that.cmdCacheTableName, 'cmd');
        if (cmdHistory === undefined) {
            cmdHistory = [];
        }
        if (cmdHistory.includes(cmd)) {
            return;
        }
        // console.log('前 cmdHistory=======', cmdHistory);
        cmdHistory.push(cmd);
        // console.log('后 cmdHistory=======', cmdHistory);

        layui.data(that.cmdCacheTableName, {
            key: 'cmd', value: cmdHistory
        });
    };

    mySSH.prototype.openHistoryPanel = function () {
        let that = this;
        historyDom.slideDown();
    };

    exports(MOD_NAME, function (conf) {
        return new mySSH(conf);
    });
});