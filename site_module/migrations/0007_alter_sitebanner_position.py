# Generated by Django 4.2 on 2024-07-25 07:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('site_module', '0006_sitebanner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sitebanner',
            name='position',
            field=models.CharField(choices=[('product_list', 'صفحه لیست محصولات'), ('product_detail', 'صفحه جزییات محصولات'), ('about_us', 'درباره ما')], max_length=200, verbose_name='جایگاه نمایشی'),
        ),
    ]
