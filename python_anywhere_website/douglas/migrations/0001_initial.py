# Generated by Django 4.0.4 on 2022-04-16 15:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Track',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Race',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('datetime', models.DateTimeField()),
                ('laps', models.IntegerField()),
                ('day_race', models.BooleanField()),
                ('raining', models.BooleanField()),
                ('track', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='douglas.track')),
            ],
        ),
    ]
