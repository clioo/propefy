# Generated by Django 3.0.14 on 2021-04-24 18:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_inmueble_destacado'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dueno',
            options={'ordering': ('nombre',)},
        ),
        migrations.AlterModelOptions(
            name='estado',
            options={'ordering': ('nombre',)},
        ),
        migrations.AlterModelOptions(
            name='municipio',
            options={'ordering': ('nombre',)},
        ),
    ]