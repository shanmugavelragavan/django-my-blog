# Generated by Django 5.2.1 on 2025-05-10 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="post",
            name="img_url",
            field=models.URLField(null=True),
        ),
    ]
