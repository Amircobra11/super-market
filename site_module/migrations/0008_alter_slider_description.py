# Generated by Django 4.2 on 2024-07-27 06:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('site_module', '0007_alter_sitebanner_position'),
    ]

    operations = [
        migrations.AlterField(
            model_name='slider',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='توضیحات اسلایدر'),
        ),
    ]
