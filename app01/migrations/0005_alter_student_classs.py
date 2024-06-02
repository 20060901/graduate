# Generated by Django 5.0.3 on 2024-04-05 04:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app01", "0004_student_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="student",
            name="classs",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="students",
                to="app01.class",
                verbose_name="所在班级",
            ),
        ),
    ]
