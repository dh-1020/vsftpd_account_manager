# Generated by Django 2.1.8 on 2020-04-09 10:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ftp_account', '0002_auto_20200409_0744'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='permission',
            name='access_page',
        ),
        migrations.AddField(
            model_name='permission',
            name='delete',
            field=models.BooleanField(default=True, verbose_name='删除用户'),
        ),
        migrations.AddField(
            model_name='permission',
            name='modify',
            field=models.BooleanField(default=True, verbose_name='修改用户'),
        ),
        migrations.AddField(
            model_name='permission',
            name='regist',
            field=models.BooleanField(default=True, verbose_name='注册用户'),
        ),
        migrations.AddField(
            model_name='permission',
            name='select',
            field=models.BooleanField(default=True, verbose_name='查看用户'),
        ),
        migrations.AlterField(
            model_name='permission',
            name='username',
            field=models.BooleanField(max_length=50),
        ),
    ]
