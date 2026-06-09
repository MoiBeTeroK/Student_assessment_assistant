from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_userprofile_delete_teacherprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='active_jti',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Активный токен JTI'),
        ),
    ]
