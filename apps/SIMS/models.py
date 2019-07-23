from django.db import models
from apps.Platform.config import Badge as BadgeConf, Table, Form, Filter


class SexMain:
    Male = '男'
    Female = '女'

    choices = (
        (Male, '男'),
        (Female, '女'),
    )

    Badge = {
        Male: BadgeConf.Green,
        Female: BadgeConf.Red,
    }


class Class(models.Model):
    """
    班级表
    """
    __cname__ = '班级'

    class Grade:
        One = '1'
        Second = '2'
        Third = '3'
        Fourth = '4'
        Fifth = '5'
        Sixth = '6'

        choices = (
            (One, '一'),
            (Second, '二'),
            (Third, '三'),
            (Fourth, '四'),
            (Fifth, '五'),
            (Sixth, '六'),
        )

        Badge = {
            One: BadgeConf.Red,
            Second: BadgeConf.Orange,
            Third: BadgeConf.Yellow,
            Fourth: BadgeConf.Green,
            Fifth: BadgeConf.Cyan,
            Sixth: BadgeConf.Gray,
        }

    name = models.CharField('班级名', max_length=50, help_text={
        **Table().init(),
        **Form().init(),
    })
    grade = models.CharField('年级', max_length=10, choices=Grade.choices, help_text={
        **Table().init(),
        **Form().init(),
        **Filter().init(),
    })
    headTeacher = models.ForeignKey(
        "Teacher", verbose_name="班主任", to_field="id",
        blank=True, null=True, db_constraint=False,
        on_delete=models.CASCADE, help_text={
            **Table().init(),
            **Form().init(),
        }
    )


class Teacher(models.Model):
    """
    教师表
    """
    __cname__ = '教师'

    class Sex(SexMain):
        pass

    class Course:
        Culture = 'culture'
        Mathematics = 'mathematics'
        English = 'english'
        Sports = 'sports'

        choices = (
            (Culture, "语文"),
            (Mathematics, "数学"),
            (English, "英语"),
            (Sports, "体育"),
        )

    name = models.CharField('姓名', max_length=50, help_text={
        **Table().init(),
        **Form().init(),
    })
    sex = models.CharField('性别', max_length=10, help_text={
        **Table().init(),
        **Form().init(),
        **Filter().init(),
    })
    course = models.CharField('所教课程', max_length=50, choices=Course.choices, help_text={
        **Table().init(),
        **Form().init(),
        **Filter().init(),
    })

    def __str__(self):
        return "{}:{}".format(self.name, self.course)


class Student(models.Model):
    """
    学生表
    """
    __cname__ = '学生'

    class Sex(SexMain):
        pass

    name = models.CharField('姓名', max_length=50, help_text={
        **Table().init(),
        **Form().init(),
    })
    sex = models.CharField('性别', max_length=10, help_text={
        **Table().init(),
        **Form().init(),
        **Filter().init(),
    })
    cls = models.ForeignKey(
        "Class", verbose_name="班级", to_field="id",
        blank=True, null=True, db_constraint=False,
        on_delete=models.CASCADE, help_text={
            **Table().init(),
            **Form().init(),
            **Filter().init(),
        }
    )

    def __str__(self):
        return "{}:{}".format(self.name, self.sex)

    class Meta:
        ordering = ['-id']
