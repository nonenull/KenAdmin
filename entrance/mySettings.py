# coding=utf-8
DEBUG = True
LOG_LEVEL = DEBUG and 'DEBUG' or 'INFO'

# 内部用户列表， 主要作用于在生产模式下也可以获取调试信息
InternalUsers = [
    'admin',
]


class MySQLConf:
    Database = 'kenadmin'
    User = 'root'
    Password = '5818747@A'
    Host = '192.168.204.128'
    Port = '3306'


class RedisConf:
    Host = '192.168.204.128'
    Port = '6379'


class CeleryConf:
    User = 'guest'
    Host = '127.0.0.1'
    Port = 5672
