# Generated by Django 4.2 on 2024-07-26 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product_module', '0004_productbrand_url_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productcategory',
            name='title',
            field=models.CharField(db_index=True, max_length=2, verbose_name='عنوان'),
        ),
    ]
