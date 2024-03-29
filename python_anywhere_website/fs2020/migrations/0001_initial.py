# Generated by Django 4.0.4 on 2022-04-15 20:06

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Aircraft",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("n_num", models.CharField(max_length=10)),
                ("make", models.CharField(max_length=100)),
                ("model", models.CharField(max_length=100)),
                ("icao_location", models.CharField(max_length=100)),
                ("notes", models.TextField(blank=True, null=True)),
            ],
        ),
    ]
