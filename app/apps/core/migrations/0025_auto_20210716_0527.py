# Generated by Django 3.0.14 on 2021-07-16 05:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0024_merge_20210716_0517'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inmueble',
            name='acepta_mascotas',
        ),
        migrations.AlterField(
            model_name='inmueble',
            name='se_admiten_mascotas',
            field=models.BooleanField(default=False, verbose_name='¿Acepta mascotas?'),
        ),
    ]
