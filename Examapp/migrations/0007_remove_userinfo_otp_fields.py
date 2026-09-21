from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Examapp', '0006_subject'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userinfo',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='userinfo',
            name='otp_code',
        ),
        migrations.RemoveField(
            model_name='userinfo',
            name='otp_created_at',
        ),
    ]
