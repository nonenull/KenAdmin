import re
from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class NameValidator(validators.RegexValidator):
    """
    姓名验证器
    """

    regex = r'^[\u4E00-\u9FA5A-Za-z]+$'
    message = _(
        '姓名非法. 仅支持 中文和英文'
    )
    flags = 0


@deconstructible
class AccountValidator(validators.RegexValidator):
    """
    账户名验证器
    """

    regex = r'^[a-zA-Z0-9_-]{4,16}$'
    message = _(
        '账户名非法. 仅支持 4到16位 (字母，数字，下划线，减号)'
    )
    flags = 0


@deconstructible
class PasswordValidator(validators.RegexValidator):
    """
    账户密码验证器
    """

    regex = r'^.*(?=.{6,})(?=.*\d)(?=.*[A-Z])(?=.*[a-z]).*$'
    message = _(
        '密码强度不符合 最少6位，包括至少1个大写字母，1个小写字母，1个数字'
    )
    flags = 0

@deconstructible
class MobileValidator(validators.RegexValidator):
    """
    手机号码验证器
    """

    regex = r'^((13[0-9])|(14[5,7])|(15[0-3,5-9])|(17[0,3,5-8])|(18[0-9])|166|198|199|(147))\d{8}$'
    message = _(
        '手机号码格式不正确'
    )
    flags = 0
