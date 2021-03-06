# Generated by Django 3.2.3 on 2022-03-11 12:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('resources', '0002_assignment'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('grade', models.CharField(blank=True, max_length=2)),
                ('assignment_file', models.FileField(blank=True, null=True, upload_to='')),
                ('assignment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='student_assignments', to='resources.assignment')),
                ('student', models.ManyToManyField(related_name='student_assignment', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
