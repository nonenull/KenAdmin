/**
 @Name : URL 解析 插件
 @Author: chenxiaoshun
 @Date : 2018-11-12
 */
layui.define(function (exports) {
    let $ = layui.jquery;
    let MOD_NAME = 'myUrl';

    function Url(urlStr) {
        this.urlStr = urlStr;
        this.protocol = '';
        this.host = '';
        this.port = '';
        this.path = '';
        this.hash = '';
        this.args = {};
        this.decode(urlStr);
    }

    Url.prototype.encodeArgs = function (args) {
        let argArr = [];
        if (!args) {
            args = this.args;
        }
        $.each(args, function (k, v) {
            if (typeof v === "object") {
                // console.log('v=========', v);
                v.forEach(function (j) {
                    argArr.push(k + '=' + j)
                });
                return true;
            }
            argArr.push(k + '=' + v)
        });
        return argArr.join('&');
    };

    /*
    *
    * 将 解析的东西重新编码成一条完整的url
    *
    * */
    Url.prototype.encode = function (onlyArgs = false) {
        let urlStr = '';
        let argStr = this.encodeArgs();
        if (onlyArgs) {
            return argStr;
        }
        if (this.protocol) {
            urlStr += this.protocol + "://"
        }
        if (this.host) {
            urlStr += this.host
        }
        if (this.port) {
            urlStr += ":" + this.port
        }
        if (this.path) {
            urlStr += this.path ? this.path : '/'
        }
        if (argStr) {
            urlStr += "?" + argStr
        }
        if (this.hash) {
            urlStr += "#" + this.hash
        }
        return urlStr;
    };

    Url.prototype.parseArgs = function (urlStr, isUpdate = true) {
        let args = {};
        let urlSplist = urlStr.split('?');
        // 获取 参数
        if (urlSplist.length <= 1) {
            return {};

        }
        let argStr = urlSplist[1];
        // console.log('argStr======', argStr);
        let argSplist = argStr.split('&');
        for (let i = 0; i < argSplist.length; i++) {
            let arg = argSplist[i].split("=");
            let key = arg[0];
            let value = decodeURIComponent(arg[1]);
            if (!args[key]) {
                args[key] = value;
            } else {
                if (typeof args[key] === "string") {
                    let tmpVal = args[key];
                    args[key] = new Set([tmpVal]);
                }
                // console.log('args[arg[0]]========', args[arg[0]])
                args[key].add(value)
            }
        }

        if (isUpdate) {
            $.extend(this.args, args);
        }
        console.log('args======', args);
        return args;
    };

    Url.prototype.parseHash = function (urlStr, isUpdate = true) {
        let urlSplist = urlStr.split('#');
        if (urlSplist.length > 1) {
            this.hash = urlSplist.pop();
        }
    };

    Url.prototype.decode = function (urlStr) {
        if (!urlStr) return false;

        let urlSplist = urlStr.split('?');
        // console.log('urlSplist==', urlSplist);
        let head = urlSplist[0];
        let headSplit = head.split('://');
        this.protocol = headSplit[0];
        // console.log('headSplit==', headSplit);

        let rHead = headSplit[1];
        let rHeadSplit = rHead.split('/');
        // console.log('rHeadSplit==', rHeadSplit);
        // 获取域名  端口
        let hostPort = rHeadSplit[0];
        let hostPortSplist = hostPort.split(':');
        this.host = hostPortSplist[0];
        this.port = hostPortSplist[1];

        // 获取访问路径
        let pathArr = rHeadSplit.slice(1);
        this.path = '/' + pathArr.join('/');

        // 获取 参数
        this.parseArgs(urlStr);
        this.parseHash(urlStr);
    };


    exports(MOD_NAME, function (url = '') {
        return new Url(url)
    });
});