# Generated by Django 4.1.2 on 2022-11-07 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0003_alter_channel_invitation_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='channel',
            name='invitation_code',
            field=models.CharField(blank=True, max_length=15, null=True, unique=True),
        ),
    ]
