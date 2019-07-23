# coding=utf-8
import json

from django import template
from django.core.cache import cache
from django.template.defaultfilters import safe

from entrance.routes import Type as RouterType
import logging

logger = logging.getLogger(__name__)

register = template.Library()


@register.tag
def generateBtn(parser, token):
    return BtnNode()


class BtnNode(template.Node):

    def _getCurMenuInfo(self, menuJson, url):
        # logger.debug('开始执行 _getCurMenuInfo')
        if isinstance(menuJson, str):
            menuJson = json.loads(menuJson)

        for item in menuJson:
            # logger.debug('当前 item===', item.get('display'))
            if item.get('url') == url:
                # logger.debug('命中 item===', item.get('display'))
                return item
            if 'child' in item:
                # logger.debug('item child===', item.get('display'))
                result = self._getCurMenuInfo(item['child'], url)
                if result:
                    return result
            else:
                continue
        return

    def _getPannelButton(self, menuJson, url):
        btnList = []
        btnType = RouterType.panelButton
        curMenuInfo = self._getCurMenuInfo(menuJson, url)
        # logger.debug('_getPannelButton===', curMenuInfo)
        if not curMenuInfo:
            return btnList

        if 'child' not in curMenuInfo:
            return btnList

        childs = curMenuInfo['child']
        for c in childs:
            # logger.debug('btn====', c)
            if c.get('rtype') == btnType:
                btnList.append(c)

        return btnList

    def render(self, context):
        request = context.request
        curUrl = request.path
        # logger.debug('curUrl===', curUrl)
        # menuJson = request.session.get('menuJson')
        menuJson = request.session.get('myAllMenu')
        # logger.debug('menuJSON===', menuJson)
        btnList = self._getPannelButton(menuJson, curUrl)
        # logger.debug('btnlist===', btnList)
        html = ''

        for btn in btnList:
            # logger.debug('btn=====', btn)
            if btn.get('link'):
                html += """
                    <a class="layui-btn layui-btn-sm {color}" href="{url}" my-filter="{filter}" link="{link}">
                        <i class="layui-icon {icon}"></i> {display}
                    </a>
                """.format(**btn)
            else:
                html += """
                    <button class="layui-btn layui-btn-sm {color}" href="{url}" my-filter="{filter}">
                        <i class="layui-icon {icon}"></i> {display}
                    </button>
                """.format(**btn)

        return safe(html)
