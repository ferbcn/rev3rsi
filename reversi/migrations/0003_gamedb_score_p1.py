# Generated by Django 2.2.6 on 2019-10-23 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reversi', '0002_auto_20191023_1307'),
    ]

    operations = [
        migrations.AddField(
            model_name='gamedb',
            name='score_p1',
            field=models.IntegerField(default=0),
        ),
    ]