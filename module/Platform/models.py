# coding=utf-8
import datetime

from django.contrib.auth.models import AbstractUser, UserManager as OUserManager
from django.db import models
from django_mysql.models import JSONField, ListCharField

from module.Platform.config import Table, Form, Filter
from . import validator
from . import config as PlatformConfig


class Role(models.Model):
    """
    角色表
    """
    __cname__ = '角色'

    class Type:
        # 内置角色, 登录用户自动拥有此角色
        BuiltIn = 'builtin'
        Ordinary = 'ordinary'
        choices = (
            (Ordinary, '普通'),
            (BuiltIn, '内置'),
        )
        Badge = {
            Ordinary: PlatformConfig.Badge.Green,
            BuiltIn: PlatformConfig.Badge.Orange
        }

    roleName = models.CharField('角色名', max_length=100, unique=True, db_index=True, help_text={
        **Table().init(),
        **Form().init(),
    })
    type = models.CharField('角色类型', max_length=100, choices=Type.choices, help_text={
        **Table().init(),
        **Form().init(),
        **Filter().init(),
    })
    # 如果指定了 内置条件, 则符合条件的用户才会自动拥有
    condition = JSONField('内置条件', null=True, blank=True, help_text={
        **Table().init(),
        **Form(placeholder="默认为json格式").init(),
    })
    createTime = models.DateTimeField('创建时间', auto_now_add=True)
    comment = models.TextField('备注', max_length=100, default='', null=True, blank=True, help_text={
        **Table().init(),
        **Form().init(),
    })

    def __str__(self):
        return self.roleName

    class Meta:
        ordering = ['-id']


class UserManager(OUserManager):
    use_in_migrations = True

    def _createUser(self, account, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not account:
            raise ValueError('The given account must be set')
        email = self.normalize_email(email)
        account = self.model.normalize_username(account)
        user = self.model(account=account, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def createUser(self, account, email=None, password=None, **extra_fields):
        # extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('isSuperUser', False)
        return self._createUser(account, email, password, **extra_fields)

    def createSuperUser(self, username, email, password, **extra_fields):
        # extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('isSuperUser', True)

        # if extra_fields.get('is_staff') is not True:
        #     raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('isSuperUser') is not True:
            raise ValueError('Superuser must have isSuperUser=True.')

        return self._createUser(username, email, password, **extra_fields)


class User(AbstractUser):
    """
    用户信息扩展
    """
    __cname__ = '用户'
    # 注释掉无用的字段
    username = None
    first_name = None
    last_name = None
    is_staff = None
    is_superuser = None
    last_login = None
    is_active = None
    date_joined = None

    class Status:
        WaitActive = 'waitActive'
        Active = 'active'
        UnActive = 'unActive'
        Expired = 'expired'
        choices = (
            (WaitActive, "待启用"),
            (Active, "启用"),
            (UnActive, "禁用"),
            (Expired, "过期")
        )
        Badge = {
            Active: PlatformConfig.Badge.Green,
            UnActive: PlatformConfig.Badge.Red,
            Expired: PlatformConfig.Badge.Orange
        }

    class IsSuperUser:
        Super = True
        Ordinary = False
        choices = (
            (Super, "超级管理员"),
            (Ordinary, "普通用户"),
        )
        Badge = {
            Super: PlatformConfig.Badge.Orange,
            Ordinary: PlatformConfig.Badge.Blue
        }

    account = models.CharField("账户名", max_length=150, unique=True, null=True, blank=True, validators=[validator.AccountValidator()], help_text={
        **Table().init(),
        **Form().init(),
    })
    password = models.CharField('账户密码', max_length=128, validators=[validator.PasswordValidator()], help_text={
        **Form(formType='password').init(),
    })
    name = models.CharField('姓名', max_length=20, default='佚名', validators=[validator.NameValidator()], help_text={
        **Table().init(),
        **Form().init(),
    })
    mobile = models.CharField('手机号码', max_length=11, blank=True, validators=[validator.MobileValidator()], help_text={
        **Table().init(),
        **Form().init(),
    })
    email = models.EmailField('邮箱地址', blank=True, help_text={
        **Table().init(),
        **Form(verify=['companyEmail']).init(),
    })
    title = models.CharField('头衔', max_length=50, null=True, blank=True, help_text={
        **Table().init(),
    })
    isSuperUser = models.BooleanField('是否超管', default=False, choices=IsSuperUser.choices, help_text={
        **Table().init(),
        **Filter().init(),
    })
    status = models.CharField('用户状态', max_length=40, default=Status.Active, choices=Status.choices, help_text={
        **Table().init(),
        **Form().init(),
        **Filter().init(),
    })
    expireTime = models.DateTimeField("账户过期时间", null=True, default='2999-01-01 00:00:00', help_text={
        **Table().init(),
        **Form().init(),
    })
    ad = models.CharField("域", max_length=50, null=True, blank=True)
    createTime = models.DateTimeField("加入时间", auto_now_add=True)
    comment = models.TextField('备注', blank=True, help_text={
        **Table(truncatechars=40).init(),
        **Form().init(),
    })
    roles = models.ManyToManyField(Role, verbose_name="角色", through='User_Role')
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'account'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'

    def isExpire(self):
        """
        检查用户是否过期
        :return: bool
        """
        # 当前时间大于过期时间, 则说明用户过期了
        status = datetime.datetime.now() > self.expireTime
        # 更新用户状态
        if status:
            self.status = User.Status.Expired
            self.save()
        return status

    def __str__(self):
        return "{}:{}".format(self.name, self.account)


class User_Role(models.Model):
    """
    用户 => 角色 中间表
    """
    __cname__ = '用户 <=> 角色'

    user = models.ForeignKey(
        User, verbose_name="用户", to_field="id",
        blank=True, null=True, db_constraint=False,
        on_delete=models.CASCADE, help_text={
            **Table().init(),
            **Form().init(),
        }
    )
    role = models.ForeignKey(
        Role, verbose_name="角色", to_field="id",
        blank=True, null=True, db_constraint=False,
        on_delete=models.CASCADE, help_text={
            **Table().init(),
            **Form().init(),
        }
    )

    def __str__(self):
        return "{} => {}".format(self.role, self.user)

    class Meta:
        ordering = ['-id']


class User_Message(models.Model):
    """
    增加一个内部系统消息机制
    """
    user = models.ForeignKey(
        User, verbose_name="用户", to_field="id",
        blank=True, null=True, db_constraint=False,
        on_delete=models.SET_NULL
    )
    message = models.TextField('消息')
    isRead = models.BooleanField('是否已读')
    createTime = models.DateTimeField('创建时间', auto_now_add=True)
    readTime = models.DateTimeField('读取时间', null=True, blank=True)

    def __str__(self):
        return "{} 有消息 {} 投递给 {}".format(self.createTime, self.message, self.user)

    class Meta:
        ordering = ['-id']


class Perm(models.Model):
    """
    用户 => 菜单 中间权限表
    角色 => 菜单 中间权限表
    正常 userId 与 roleId 只填写一个
    """
    namespace = models.CharField('路由命名空间', max_length=50, default='')
    name = models.CharField('路由name', max_length=50, default='')
    user = models.ForeignKey(
        User, verbose_name="用户", to_field="id",
        blank=True, null=True, db_constraint=False,
        on_delete=models.SET_NULL
    )
    role = models.ForeignKey(
        Role, verbose_name="角色", to_field="id",
        blank=True, null=True, db_constraint=False,
        on_delete=models.SET_NULL
    )

    def __str__(self):
        return "{}:{}".format(self.namespace, self.name)

    class Meta:
        ordering = ['-id']


class Log(models.Model):
    """
     oms 操作日志
    """

    class Type:
        Login = 'login'
        Operation = 'operation'
        Setting = 'setting'
        Tasks = 'tasks'
        choices = (
            (Login, '登录历史'),
            (Operation, '操作历史'),
            (Setting, '用户设置'),
            (Tasks, '异步任务'),
        )

    class Method:
        Create = 'C'
        Update = 'U'
        Retrieve = 'R'
        Delete = 'D'
        choices = (
            (Create, "增加"),
            (Delete, "删除"),
            (Update, "修改"),
            (Retrieve, "查看"),
        )

    class Status:
        Success = True
        Fail = False
        choices = (
            (Success, "成功"),
            (Fail, "失败"),
        )

    userId = models.IntegerField('用户', null=True, db_index=True, help_text={
        **Table(proxy='user').init(),
    })
    type = models.CharField('操作类型', max_length=20, db_index=True, choices=Type.choices, help_text={
        **Table().init(),
        **Filter().init(),
    })
    method = models.CharField('操作方法', max_length=1, choices=Method.choices, help_text={
        **Table().init(),
        **Filter().init(),
    })
    status = models.BooleanField('日志状态', max_length=1, default=True, choices=Status.choices, help_text={
        **Table().init(),
        **Filter().init(),
    })
    module = models.CharField('操作模块', max_length=100, help_text={
        **Table().init(),
    })
    message = JSONField('日志信息', help_text={
        **Table().init(),
    })
    createTime = models.DateTimeField('记录日志时间', auto_now_add=True, help_text={
        **Table().init(),
    })

    @property
    def user(self):
        if not self.userId:
            return ''
        try:
            user = User.objects.get(id=self.userId)
            return user
        except User.DoesNotExist:
            return ''

    def __str__(self):
        return '%s %s' % (self.get_method_display(), self.get_type_display())

    class Meta:
        ordering = ['-id']


class ApiLog(models.Model):
    """
    记录 调用 告警组API
    """
    __cname__ = 'API日志'

    apiType = models.CharField('API类型', max_length=24, help_text={
        **Table().init(),
    })
    requestIp = models.CharField('请求IP', max_length=24, help_text={
        **Table().init(),
    })
    request = JSONField('请求参数', help_text={
        **Table().init(),
    })
    response = JSONField('响应结果', help_text={
        **Table().init(),
    })
    requestTime = models.DateTimeField('请求时间', auto_now_add=True, help_text={
        **Table().init(),
    })

    def __str__(self):
        return '{}-{}'.format(self.requestIp, self.requestTime)
