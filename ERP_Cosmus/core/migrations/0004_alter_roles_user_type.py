# Generated by Django 4.2.5 on 2024-07-11 11:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_customuser_is_active_customuser_is_admin_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='roles',
            name='user_type',
            field=models.CharField(choices=[('developer-backend', 'developer-backend'), ('developer-frontend', 'developer-frontend')], default='developer-backend'),
        ),
    ]
