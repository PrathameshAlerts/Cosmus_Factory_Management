# Generated by Django 4.2.5 on 2024-09-27 05:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0022_item_color_shade_c_user_item_creation_c_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='set_prod_item_part_name',
            name='body_combi',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
