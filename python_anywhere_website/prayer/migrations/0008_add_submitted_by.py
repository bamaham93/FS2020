# Generated migration to add submitted_by to PrayerMessage
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("prayer", "0007_person_sms_consent_person_sms_consent_date"),
    ]

    operations = [
        migrations.AddField(
            model_name="prayermessage",
            name="submitted_by",
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="prayer_requests",
                to="auth.user",
            ),
        ),
    ]
