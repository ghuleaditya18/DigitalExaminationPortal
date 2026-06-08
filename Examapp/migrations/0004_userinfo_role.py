from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Examapp', '0003_feedback'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinfo',
            name='role',
            field=models.CharField(
                choices=[('student', 'Student'), ('teacher', 'Teacher')],
                default='student',
                max_length=10,
            ),
        ),
    ]
