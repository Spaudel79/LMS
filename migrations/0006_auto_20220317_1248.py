# Generated by Django 3.2.3 on 2022-03-17 07:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0005_auto_20220316_1543'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='studentassignment',
            name='assignment_file',
        ),
        migrations.CreateModel(
            name='AssignmentFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assignment_file', models.FileField(blank=True, null=True, upload_to='')),
                ('student_assignment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assignment_files', to='resources.studentassignment')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
