# Generated by Django 3.1.1 on 2020-09-13 19:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('draftapp', '0003_auto_20200913_1407'),
    ]

    operations = [
        migrations.AlterField(
            model_name='summonerspell',
            name='name',
            field=models.CharField(max_length=12),
        ),
    ]