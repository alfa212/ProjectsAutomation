from django.db import models


class Student(models.Model):
    class Level(models.TextChoices):
        NOVICE = 'novice', 'Новичок'
        NOVICE_PLUS = 'novice+', 'Новичок+'
        JUNIOR = 'junior', 'Джуниор'

    name = models.CharField(max_length=255, verbose_name='Имя')
    level = models.CharField(
        max_length=255,
        choices=Level.choices,
        default=Level.NOVICE,
        verbose_name='Уровень'
    )
    tg_username = models.CharField(
        max_length=255,
        primary_key=True,
        verbose_name='Telegram'
    )
    discord_username = models.CharField(
        max_length=255,
        verbose_name='Discord',
        blank=True
    )
    is_far_east = models.BooleanField(verbose_name='Ученик с ДВ')
    time = models.TimeField(
        verbose_name='Время созвона',
        blank=True,
        null=True
    )

    def __str__(self):
        return '[{telegram}] {name} [{level}]'.format(
            telegram=self.tg_username,
            name=self.name,
            level=self.get_level_display()
        )


class Manager(models.Model):
    name = models.CharField(max_length=255, verbose_name='Имя')
    tg_username = models.CharField(
        max_length=255,
        primary_key=True,
        verbose_name='Telegram'
    )
    time_from = models.TimeField(verbose_name='Работает с')
    time_to = models.TimeField(verbose_name='Работает по')

    def __str__(self):
        return '[{telegram}] {name} [{time_from}-{time_to}]'.format(
            telegram=self.tg_username,
            name=self.name,
            time_from=self.time_from.isoformat(timespec='minutes'),
            time_to=self.time_to.isoformat(timespec='minutes')
        )


class Group(models.Model):
    time = models.TimeField(verbose_name='Время созвона')
    manager = models.ForeignKey(
        Manager,
        verbose_name='ПМ',
        on_delete=models.PROTECT
    )
    students = models.ManyToManyField(Student, verbose_name='Студенты')

    def __str__(self):
        return '[{time}] {name} ({tg})'.format(
            time=self.time.isoformat(timespec='minutes'),
            name=self.manager.name,
            tg=self.manager.tg_username
        )

class Project(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название проекта')
    groups = models.ManyToManyField(Group, verbose_name='Группы', blank=True)

    def __str__(self):
        return self.name
