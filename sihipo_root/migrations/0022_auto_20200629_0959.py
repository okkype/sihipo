# Generated by Django 3.0.7 on 2020-06-29 09:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sihipo_root', '0021_auto_20190709_0211'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plantcontroldetail',
            name='plant_control',
            field=models.ForeignKey(limit_choices_to={'active': True}, on_delete=django.db.models.deletion.PROTECT, to='sihipo_root.PlantControl', verbose_name='Kontrol Tanaman'),
        ),
        migrations.AlterField(
            model_name='plantcontrollog',
            name='plant_control',
            field=models.ForeignKey(limit_choices_to={'active': True}, on_delete=django.db.models.deletion.CASCADE, to='sihipo_root.PlantControl', verbose_name='Kontrol Tanaman'),
        ),
        migrations.AlterField(
            model_name='plantcontrollog',
            name='plant_rack',
            field=models.ForeignKey(blank=True, limit_choices_to={'active': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, to='sihipo_root.PlantRack', verbose_name='Rak Tanaman'),
        ),
        migrations.AlterField(
            model_name='plantcontrollogdetail',
            name='plant_control_log',
            field=models.ForeignKey(limit_choices_to={'active': True}, on_delete=django.db.models.deletion.CASCADE, to='sihipo_root.PlantControlLog', verbose_name='Log Kontrol Tanaman'),
        ),
        migrations.AlterField(
            model_name='planteval',
            name='plant_eval_if',
            field=models.ForeignKey(limit_choices_to={'active': True}, on_delete=django.db.models.deletion.PROTECT, to='sihipo_root.PlantEvalIf', verbose_name='Kondisi'),
        ),
        migrations.AlterField(
            model_name='planteval',
            name='plant_eval_then',
            field=models.ForeignKey(limit_choices_to={'active': True}, on_delete=django.db.models.deletion.PROTECT, to='sihipo_root.PlantEvalThen', verbose_name='Aksi'),
        ),
        migrations.AlterField(
            model_name='plantevalif',
            name='plant_eval_group',
            field=models.ForeignKey(blank=True, limit_choices_to={'active': True}, null=True, on_delete=django.db.models.deletion.PROTECT, to='sihipo_root.PlantEvalGroup', verbose_name='Group'),
        ),
        migrations.AlterField(
            model_name='plantevallog',
            name='plant_eval',
            field=models.ForeignKey(limit_choices_to={'active': True}, on_delete=django.db.models.deletion.CASCADE, to='sihipo_root.PlantEval', verbose_name='Evaluasi Tanaman'),
        ),
        migrations.AlterField(
            model_name='plantopt',
            name='plant_plant',
            field=models.ForeignKey(limit_choices_to={'active': True}, on_delete=django.db.models.deletion.PROTECT, to='sihipo_root.PlantPlant', verbose_name='Tanaman'),
        ),
        migrations.AlterField(
            model_name='plantoptdetail',
            name='plant_opt',
            field=models.ForeignKey(limit_choices_to={'active': True}, on_delete=django.db.models.deletion.PROTECT, to='sihipo_root.PlantOpt', verbose_name='Kondisi Optimal Tanaman'),
        ),
        migrations.AlterField(
            model_name='plantrack',
            name='plant_control',
            field=models.ForeignKey(limit_choices_to={'active': True}, on_delete=django.db.models.deletion.PROTECT, to='sihipo_root.PlantControl', verbose_name='Kontrol Tanaman'),
        ),
        migrations.AlterField(
            model_name='plantrack',
            name='plant_sensor',
            field=models.ForeignKey(limit_choices_to={'active': True}, on_delete=django.db.models.deletion.PROTECT, to='sihipo_root.PlantSensor', verbose_name='Sensor Tanaman'),
        ),
        migrations.AlterField(
            model_name='plantrackpoint',
            name='plant_plant',
            field=models.ForeignKey(limit_choices_to={'active': True}, on_delete=django.db.models.deletion.PROTECT, to='sihipo_root.PlantPlant', verbose_name='Tanaman'),
        ),
        migrations.AlterField(
            model_name='plantrackpoint',
            name='plant_rack',
            field=models.ForeignKey(limit_choices_to={'active': True}, on_delete=django.db.models.deletion.PROTECT, to='sihipo_root.PlantRack', verbose_name='Rak Tanaman'),
        ),
        migrations.AlterField(
            model_name='plantsensordetail',
            name='plant_sensor',
            field=models.ForeignKey(limit_choices_to={'active': True}, on_delete=django.db.models.deletion.PROTECT, to='sihipo_root.PlantSensor', verbose_name='Sensor Tanaman'),
        ),
        migrations.AlterField(
            model_name='plantsensorlog',
            name='plant_rack',
            field=models.ForeignKey(blank=True, limit_choices_to={'active': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, to='sihipo_root.PlantRack', verbose_name='Rak Tanaman'),
        ),
        migrations.AlterField(
            model_name='plantsensorlog',
            name='plant_sensor',
            field=models.ForeignKey(limit_choices_to={'active': True}, on_delete=django.db.models.deletion.CASCADE, to='sihipo_root.PlantSensor', verbose_name='Sensor Tanaman'),
        ),
        migrations.AlterField(
            model_name='plantsensorlogdetail',
            name='plant_sensor_log',
            field=models.ForeignKey(limit_choices_to={'active': True}, on_delete=django.db.models.deletion.CASCADE, to='sihipo_root.PlantSensorLog', verbose_name='Log Sensor Tanaman'),
        ),
    ]
