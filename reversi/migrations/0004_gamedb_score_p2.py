# Generated by Django 2.2.6 on 2019-10-23 12:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reversi', '0003_gamedb_score_p1'),
    ]

    operations = [
        migrations.AddField(
            model_name='gamedb',
            name='score_p2',
            field=models.IntegerField(default=0),
        ),
    ]