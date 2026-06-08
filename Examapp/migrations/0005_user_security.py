from django.contrib.auth.hashers import identify_hasher, make_password
from django.db import migrations, models


def secure_existing_users(apps, schema_editor):
    UserInfo = apps.get_model('Examapp', 'UserInfo')
    for user in UserInfo.objects.all():
        try:
            identify_hasher(user.password)
        except ValueError:
            user.password = make_password(user.password)
        user.is_active = True
        user.save(update_fields=['password', 'is_active'])


class Migration(migrations.Migration):

    dependencies = [
        ('Examapp', '0004_userinfo_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='password',
            field=models.CharField(max_length=128),
        ),
        migrations.AlterField(
            model_name='userinfo',
            name='mobile_no',
            field=models.CharField(max_length=15, unique=True),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='failed_login_attempts',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='locked_until',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='otp_code',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='otp_created_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.RunPython(secure_existing_users, migrations.RunPython.noop),
    ]
