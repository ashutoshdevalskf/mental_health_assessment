# Generated by Django 5.1.6 on 2025-04-10 13:25

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Assessment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('disorders', models.JSONField()),
                ('reverse_scored', models.BooleanField(default=False)),
                ('weight', models.IntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='AssessmentAttempt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.FloatField()),
                ('attempted_at', models.DateTimeField(auto_now_add=True)),
                ('responses', models.JSONField()),
                ('raw_scores', models.JSONField()),
                ('severity_scores', models.JSONField()),
                ('assessment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assessments.assessment')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
