# Generated by Django 2.2 on 2019-04-29 13:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('membership', '0004_auto_20190425_1559'),
    ]

    operations = [
        migrations.AlterField(
            model_name='race',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='race', to='membership.RaceCategory'),
        ),
        migrations.AlterField(
            model_name='race',
            name='types',
            field=models.ManyToManyField(blank=True, null=True, to='membership.RaceType'),
        ),
    ]
