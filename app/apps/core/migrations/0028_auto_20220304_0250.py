# Generated by Django 3.0.14 on 2022-03-04 02:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0027_auto_20211125_0352'),
    ]

    operations = [
        migrations.AddField(
            model_name='prospectocomprador',
            name='correo',
            field=models.CharField(default='jesus_acosta1996@hotmail.com', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='prospectocomprador',
            name='nombre',
            field=models.CharField(default='chicho', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='prospectovendedor',
            name='correo',
            field=models.CharField(default='jesus_acosta1996@hotmail.com', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='prospectovendedor',
            name='nombre',
            field=models.CharField(default='chicho', max_length=255),
            preserve_default=False,
        ),
    ]