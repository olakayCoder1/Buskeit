# Generated by Django 4.1.2 on 2022-10-31 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_rename_user_mail_accountactivation_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='schooladmin',
            name='phone_number',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
