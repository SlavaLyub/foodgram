# Generated by Django 3.2 on 2024-08-22 22:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodgram', '0003_shoppingcart'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(max_length=150, verbose_name='Last Name'),
        ),
    ]
