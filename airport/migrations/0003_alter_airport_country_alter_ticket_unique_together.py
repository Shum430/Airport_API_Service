# Generated by Django 4.1 on 2024-01-29 13:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("airport", "0002_alter_country_options"),
    ]

    operations = [
        migrations.AlterField(
            model_name="airport",
            name="country",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="airport_name",
                to="airport.country",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="ticket",
            unique_together={("seat", "row", "flight")},
        ),
    ]
