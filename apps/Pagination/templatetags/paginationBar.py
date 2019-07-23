# -*- coding: UTF-8 -*-
from django import template
from django.template.defaultfilters import safe

import logging

logger = logging.getLogger(__name__)
register = template.Library()


@register.filter
def generateSelect(perPage):
    item = '<option value="%s" %s>%s 条/页</option>'
    pageNumList = [10, 20, 50, 100]

    html = ""
    #print("===perPage===", perPage)
    for i in pageNumList:
        selected = ''
        if i == int(perPage):
            selected = 'selected'

        html += item % (i, selected, i)
    return safe(html)
