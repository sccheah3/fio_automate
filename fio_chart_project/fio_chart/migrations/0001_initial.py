# Generated by Django 3.0.8 on 2020-08-06 19:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DriveBenchmark',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now_add=True)),
                ('drive_pn', models.CharField(default='NA', max_length=100)),
                ('drive_fw', models.CharField(default='NA', max_length=100)),
            ],
            options={
                'ordering': ['modified'],
            },
        ),
        migrations.CreateModel(
            name='DrivePerformance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('drive', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='drive_performances', to='fio_chart.DriveBenchmark')),
            ],
        ),
        migrations.CreateModel(
            name='BlockPerformance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('block_size', models.IntegerField()),
                ('read_speed', models.IntegerField()),
                ('write_speed', models.IntegerField()),
                ('drive_performance', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='block_performances', to='fio_chart.DrivePerformance')),
            ],
            options={
                'ordering': ['block_size'],
            },
        ),
    ]
