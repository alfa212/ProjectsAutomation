# Generated by Django 4.0.1 on 2022-01-30 10:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('automation', '0005_lonelystudent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='discord_username',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Discord'),
        ),
    ]
