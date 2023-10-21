# Generated by Django 4.2.6 on 2023-10-21 21:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('professor', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='professor',
            name='rmp_url',
            field=models.CharField(default=None, max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='review',
            name='difficulty',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='review',
            name='rating',
            field=models.FloatField(),
        ),
    ]
