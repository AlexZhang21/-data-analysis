# Generated by Django 4.2.16 on 2024-11-29 09:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0013_productentry_uploaded_file_alter_productentry_origin_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productentry',
            name='origin',
            field=models.CharField(default='Unknown', max_length=255),
        ),
        migrations.AlterField(
            model_name='productentry',
            name='price',
            field=models.CharField(default='UnKnown', max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='productentry',
            name='product_group',
            field=models.CharField(choices=[('LPG', 'LPG'), ('Naphtha', 'Naphtha'), ('Fueloil', 'Fueloil'), ('Gasoil', 'Gasoil'), ('Gasoline', 'Gasoline'), ('Bitumen', 'Bitumen'), ('Crude', 'Crude'), ('Others', 'Others')], max_length=50),
        ),
        migrations.AlterField(
            model_name='productentry',
            name='quantity',
            field=models.CharField(default='Unknown', max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='productentry',
            name='tag1',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='productentry',
            name='tag2',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='productentry',
            name='tag3',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='productentry',
            name='year',
            field=models.IntegerField(choices=[(2000, 2000), (2001, 2001), (2002, 2002), (2003, 2003), (2004, 2004), (2005, 2005), (2006, 2006), (2007, 2007), (2008, 2008), (2009, 2009), (2010, 2010), (2011, 2011), (2012, 2012), (2013, 2013), (2014, 2014), (2015, 2015), (2016, 2016), (2017, 2017), (2018, 2018), (2019, 2019), (2020, 2020), (2021, 2021), (2022, 2022), (2023, 2023), (2024, 2024), (2025, 2025), (2026, 2026), (2027, 2027), (2028, 2028), (2029, 2029), (2030, 2030), (2031, 2031), (2032, 2032), (2033, 2033), (2034, 2034), (2035, 2035), (2036, 2036), (2037, 2037), (2038, 2038), (2039, 2039), (2040, 2040)]),
        ),
    ]
