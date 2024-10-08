# Generated by Django 4.2.5 on 2024-10-05 04:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0025_cutting_room_c_user_cutting_room_company_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='godown_finished_goods',
            unique_together={('godown_name_finished',)},
        ),
        migrations.AlterUniqueTogether(
            name='godown_raw_material',
            unique_together={('godown_name_raw',)},
        ),
        migrations.RemoveField(
            model_name='godown_finished_goods',
            name='c_user',
        ),
        migrations.RemoveField(
            model_name='godown_finished_goods',
            name='company',
        ),
        migrations.RemoveField(
            model_name='godown_raw_material',
            name='c_user',
        ),
        migrations.RemoveField(
            model_name='godown_raw_material',
            name='company',
        ),
    ]
