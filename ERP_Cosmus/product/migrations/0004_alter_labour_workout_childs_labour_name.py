# Generated by Django 4.2.5 on 2024-09-13 05:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0003_delete_companymaster'),
    ]

    operations = [
        migrations.AlterField(
            model_name='labour_workout_childs',
            name='labour_name',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='product.ledger'),
            preserve_default=False,
        ),
    ]
