# coding=utf-8
from django import template
from django.template.defaultfilters import safe

from module.Platform.models import User
from module.Platform.templatetags.baseTag import formatDate
import logging

logger = logging.getLogger(__name__)

register = template.Library()


@register.filter
def generateStatus(status):
    if not status:
        status = "未知"
    item = '<span class="my-label %s">%s</span>'
    statusDict = {
        "启用": "my-label-success",
        "禁用": "my-label-important",
    }
    html = item % (statusDict.get(status, "my-label-info"), status)
    return safe(html)


@register.filter
def generateExpireTime(userInfo):
    item = '<span class="layui-badge %s">%s</span>'
    if not userInfo.isExpire():
        html = item % ('layui-bg-green', formatDate(userInfo.expireTime))
    else:
        html = item % ('', formatDate(userInfo.expireTime))
    return safe(html)


@register.tag
def generateUserStatus(parses, token):
    split = token.split_contents()
    return UserStatus(*split[1:])


class UserStatus(template.Node):
    def __init__(self, requstUser, userInfo):
        self.requstUserVar = template.Variable(requstUser)
        self.userInfoVar = template.Variable(userInfo)

    def render(self, context):
        self.requstUser = self.requstUserVar.resolve(context)
        self.userInfo = self.userInfoVar.resolve(context)
        if self.requstUser.id == self.userInfo.id:
            return ''

        html = """
        <div class="layui-form-item">
            <label class="layui-form-label my-required">状态</label>
            <div class="layui-input-inline">
                <select name="status" lay-verify="required">
                    %s
                </select>
            </div>
        </div>
        """
        options = []
        userStatus = self.userInfo.status
        for k, v in self.userInfo._meta.model.Status.choices:
            options.append(
                "<option value='%s' %s>%s</option>" % (k, (userStatus == k and 'selected'), v)
            )
        return safe(
            html % ''.join(options)
        )
