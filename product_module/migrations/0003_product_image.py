# Generated by Django 4.2 on 2024-06-30 05:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product_module', '0002_auto_20211220_2231'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='images/product', verbose_name='تصویر محصول'),
        ),
    ]
