# Generated by Django 3.0.14 on 2022-03-17 02:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0030_inmueble_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='prospectovendedor',
            name='inmueble',
        ),
    ]
