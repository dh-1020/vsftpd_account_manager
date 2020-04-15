# Generated by Django 2.1.8 on 2020-03-23 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RegisterUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=50)),
                ('password', models.CharField(max_length=50)),
                ('homedir', models.CharField(max_length=20)),
                ('can_upload', models.CharField(max_length=20)),
                ('can_download', models.CharField(max_length=20)),
                ('can_createdir', models.CharField(max_length=20)),
                ('can_deletion', models.CharField(max_length=20)),
            ],
        ),
    ]