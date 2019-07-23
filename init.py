# coding=utf-8
if __name__ == "__main__":
    from utils import environment

from module.Platform.models import User


def createSuperUser():
    user = User.objects.createSuperUser(
        'admin',
        'xxx@qq.com',
        '123456',
    )
    print('user==', user)


if __name__ == '__main__':
    createSuperUser()
