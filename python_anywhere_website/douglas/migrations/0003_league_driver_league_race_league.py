# Generated by Django 4.0.4 on 2022-07-16 03:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('douglas', '0002_driver'),
    ]

    operations = [
        migrations.CreateModel(
            name='League',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='driver',
            name='league',
            field=models.ManyToManyField(null=True, to='douglas.league'),
        ),
        migrations.AddField(
            model_name='race',
            name='league',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='douglas.league'),
        ),
    ]