# Generated by Django 4.2.16 on 2024-11-28 06:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0012_productentry'),
    ]

    operations = [
        migrations.AddField(
            model_name='productentry',
            name='uploaded_file',
            field=models.FileField(blank=True, null=True, upload_to='uploaded_files/'),
        ),
        migrations.AlterField(
            model_name='productentry',
            name='origin',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='productentry',
            name='price',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='productentry',
            name='product_group',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='productentry',
            name='quantity',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='productentry',
            name='tag1',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='productentry',
            name='tag2',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='productentry',
            name='tag3',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='productentry',
            name='year',
            field=models.PositiveIntegerField(),
        ),
    ]
