/**
 @Name : myDate 日期扩展插件
 @Author: chenxiaoshun
 @Date : 2018-12-22
 */
layui.define(['laydate'], function (exports) {
    let MOD_NAME = 'myDate';
    let $ = layui.jquery;
    let laydate = layui.laydate;

    let myDate = function (dateStr) {
        this.originalDate = new Date(dateStr);
        if (this.originalDate === 'Invalid Date') {
            layui.hint().error('不支持的日期格式: ' + dateStr);
            this.originalDate = new Date();
        }
        this.date = this.originalDate;
    };

    myDate.prototype.calc = function (type, number) {
        number = parseInt(number);
        let dtTmp = this.date;
        switch (type) {
            case 's' :
                this.date = new Date(Date.parse(dtTmp) + (1000 * number));
                break;
            case 'n' :
                this.date = new Date(Date.parse(dtTmp) + (60000 * number));
                break;
            case 'h' :
                this.date = new Date(Date.parse(dtTmp) + (3600000 * number));
                break;
            case 'd' :
                this.date = new Date(Date.parse(dtTmp) + (86400000 * number));
                break;
            case 'w' :
                this.date = new Date(Date.parse(dtTmp) + ((86400000 * 7) * number));
                break;
            case 'q' :
                this.date = new Date(dtTmp.getFullYear(), (dtTmp.getMonth()) + number * 3, dtTmp.getDate(), dtTmp.getHours(), dtTmp.getMinutes(), dtTmp.getSeconds());
                break;
            case 'm' :
                this.date = new Date(dtTmp.getFullYear(), (dtTmp.getMonth()) + number, dtTmp.getDate(), dtTmp.getHours(), dtTmp.getMinutes(), dtTmp.getSeconds());
                break;
            case 'y' :
                this.date = new Date((dtTmp.getFullYear() + number), dtTmp.getMonth(), dtTmp.getDate(), dtTmp.getHours(), dtTmp.getMinutes(), dtTmp.getSeconds());
                break;
        }
        return this;
    };

    myDate.prototype.format = function (mask) {
        let d = this.date;
        let zeroize = function (value, length) {
            if (!length) length = 2;
            value = String(value);
            for (let i = 0, zeros = ''; i < (length - value.length); i++) {
                zeros += '0';
            }
            return zeros + value;
        };

        return mask.replace(/"[^"]*"|'[^']*'|\b(?:d{1,4}|m{1,4}|yy(?:yy)?|([hHMstT])\1?|[lLZ])\b/g, function ($0) {
            switch ($0) {
                case 'd':
                    return d.getDate();
                case 'dd':
                    return zeroize(d.getDate());
                case 'ddd':
                    return ['Sun', 'Mon', 'Tue', 'Wed', 'Thr', 'Fri', 'Sat'][d.getDay()];
                case 'dddd':
                    return ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'][d.getDay()];
                case 'M':
                    return d.getMonth() + 1;
                case 'MM':
                    return zeroize(d.getMonth() + 1);
                case 'MMM':
                    return ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][d.getMonth()];
                case 'MMMM':
                    return ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][d.getMonth()];
                case 'yy':
                    return String(d.getFullYear()).substr(2);
                case 'yyyy':
                    return d.getFullYear();
                case 'h':
                    return d.getHours() % 12 || 12;
                case 'hh':
                    return zeroize(d.getHours() % 12 || 12);
                case 'H':
                    return d.getHours();
                case 'HH':
                    return zeroize(d.getHours());
                case 'm':
                    return d.getMinutes();
                case 'mm':
                    return zeroize(d.getMinutes());
                case 's':
                    return d.getSeconds();
                case 'ss':
                    return zeroize(d.getSeconds());
                case 'l':
                    return zeroize(d.getMilliseconds(), 3);
                case 'L':
                    let m = d.getMilliseconds();
                    if (m > 99) m = Math.round(m / 10);
                    return zeroize(m);
                case 'tt':
                    return d.getHours() < 12 ? 'am' : 'pm';
                case 'TT':
                    return d.getHours() < 12 ? 'AM' : 'PM';
                case 'Z':
                    return d.toUTCString().match(/[A-Z]+$/);
                // Return quoted strings with the surrounding quotes removed
                default:
                    return $0.substr(1, $0.length - 2);
            }
        });
    };

    // 搜索 .my-date 的项 , 使用日期组件渲染
    // 因为layDate不支持 传入复数的elem, 所以此处遍历 下 my-date 再执行 render
    $('.my-date').each(function (index, item) {
        let layDateObj = laydate.render({
            elem: item,
            type: 'datetime',
        });
    });

    exports(MOD_NAME, myDate);
});