# Generated by Django 4.1.2 on 2022-11-13 00:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0006_channelactivationcode_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='channel',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='channel',
            name='phone_number',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='channel',
            name='rc_number',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
