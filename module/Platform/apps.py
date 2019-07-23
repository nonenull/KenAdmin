from django.apps import AppConfig

from django.core import exceptions


def validate(self, value, model_instance):
    """
    为 JSONField 重写 validate 方法
    """
    if not self.editable:
        # Skip validation for non-editable fields.
        return

    if self.choices and value not in self.empty_values:
        for option_key, option_value in self.choices:
            if isinstance(option_value, (list, tuple)):
                # This is an optgroup, so look inside the group for
                # options.
                for optgroup_key, optgroup_value in option_value:
                    if isinstance(value, list) and optgroup_key in value:
                        return
                    if value == optgroup_key:
                        return
            elif value == option_key or (isinstance(value, list) and option_key in value):
                return
        raise exceptions.ValidationError(
            self.error_messages['invalid_choice'],
            code='invalid_choice',
            params={'value': value},
        )

    if value is None and not self.null:
        raise exceptions.ValidationError(self.error_messages['null'], code='null')

    if not self.blank and value in self.empty_values:
        raise exceptions.ValidationError(self.error_messages['blank'], code='blank')


class PlatformConfig(AppConfig):
    name = 'module.Platform'
    AdminUserName = 'admin'

    def ready(self):
        from django_mysql.models import JSONField
        JSONField.validate = validate

        # self.iniUser()

    def iniUser(self):
        """
        检查超级用户是否存在, 如果不存在, 自动创建一个, 初始化密码在log中查看
        :return:
        """
        import logging
        from module.Platform.models import User
        from utils.secretUtil import getRandPassword
        logger = logging.getLogger(__name__)
        if not User.objects.filter(account=self.AdminUserName).exists():
            randPasswd = getRandPassword()
            User.objects.createSuperUser(
                self.AdminUserName,
                '',
                randPasswd,
            )
            logger.warning('检测到超级用户不存在, 新创建 admin 用户, 初始化密码为: %s', randPasswd)
