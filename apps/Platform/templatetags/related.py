# coding=utf-8
from django import template

import logging

logger = logging.getLogger(__name__)
register = template.Library()


@register.filter
def getUrl(request, action: str):
    path = request.path
    # logger.debug("action==={}".format(action))
    # logger.debug("path==={}".format(path))
    return path.replace('related', 'related/{}'.format(action))
