# Generated by Django 3.1.1 on 2020-09-13 18:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('draftapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='champion',
            name='img',
            field=models.FilePathField(path='/home/mars/Workspace/Python/Loldraft.gg/draftapp/static/img/champion'),
        ),
        migrations.AlterField(
            model_name='summoneritem',
            name='name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='summonerspell',
            name='img',
            field=models.FilePathField(path='/home/mars/Workspace/Python/Loldraft.gg/draftapp/static/img/items'),
        ),
    ]