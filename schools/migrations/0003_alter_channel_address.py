# Generated by Django 4.1.2 on 2022-11-10 01:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0002_rename_company_name_channel_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='channel',
            name='address',
            field=models.TextField(blank=True, null=True),
        ),
    ]