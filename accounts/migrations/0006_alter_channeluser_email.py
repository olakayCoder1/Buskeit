# Generated by Django 4.1.2 on 2022-11-10 02:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_alter_channeluser_channel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='channeluser',
            name='email',
            field=models.EmailField(max_length=254),
        ),
    ]
