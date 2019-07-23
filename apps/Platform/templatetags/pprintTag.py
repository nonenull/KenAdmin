# coding=utf-8
from django import template
import pprint
import logging

from django.template.defaultfilters import safe

logger = logging.getLogger(__name__)

register = template.Library()


@register.filter
def pretty(text):
    return safe(
        pprint.pformat(text)
    )
