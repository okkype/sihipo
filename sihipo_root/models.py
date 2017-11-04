# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone

# Create your models here.

class FloatRangeField(models.FloatField):
    def __init__(self, verbose_name=None, name=None, min_value=None, max_value=None, **kwargs):
        self.min_value, self.max_value = min_value, max_value
        models.FloatField.__init__(self, verbose_name, name, **kwargs)
    
    def formfield(self, **kwargs):
        defaults = {'min_value': self.min_value, 'max_value':self.max_value}
        defaults.update(kwargs)
        return super(FloatRangeField, self).formfield(**defaults)
    
class PlantBase(models.Model):
    created = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey('auth.User', models.SET_NULL, related_name='created_by', null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey('auth.User', models.SET_NULL, related_name='updated_by', null=True, blank=True)
    note = models.TextField('Note', null=True, blank=True)
    active = models.BooleanField('Aktif', default=True)
    
    sensor_type = (
        (None, 'N/A'),
        ('PH', 'Keasaman'),
        ('EC', 'Konduktifitas'),
        ('HT', 'Kelembapan'),
        ('TW', 'Suhu Air'),
        ('TA', 'Suhu Udara'),
        ('LW', 'Level Air'),
    )
    
    control_type = (
        (None, 'N/A'),
        ('L', 'GROW LAMP'),
        ('S', 'SPRAY'),
        ('W', 'WATER PUMP'),
        ('A', 'AERIAL'),
        ('B', 'BLOWER'),
    )

    control_pin = (
        (None, 'N/A'),
        ('D1', 'Digital 1'),
        ('D2', 'Digital 2'),
        ('D3', 'Digital 3'),
        ('D4', 'Digital 4'),
        ('D5', 'Digital 5'),
        ('D6', 'Digital 6'),
        ('D7', 'Digital 7'),
        ('D8', 'Digital 8'),
    )

    rack_type = (
        (None, 'N/A'),
        ('NFT', 'Net Film'),
        ('DFT', 'Deep Flow'),
        ('WICK', 'Wick'),
    )

# Create your models here.
class PlantEvalIf(PlantBase):
    kode = models.CharField('Kode IF', unique=True, max_length=20)
    eval_if = models.TextField('Evaluate IF', unique=True)
    
    class Meta:
        verbose_name = 'Evaluasi Tanaman (IF)'
        
class PlantEvalThen(PlantBase):
    kode = models.CharField('Kode THEN', unique=True, max_length=20)
    eval_then = models.TextField('Evaluate THEN', unique=True)
    
    class Meta:
        verbose_name = 'Evaluasi Tanaman (THEN)'

class PlantEval(PlantBase):
    plant_eval_if = models.ForeignKey(PlantEvalIf, models.PROTECT, limit_choices_to={'active': True})
    plant_eval_then = models.ForeignKey(PlantEvalThen, models.PROTECT, limit_choices_to={'active': True})
    
    class Meta:
        verbose_name = 'Evaluasi Tanaman'
        unique_together = ('plant_eval_if', 'plant_eval_then')

class PlantEvalLog(PlantBase):
    plant_eval = models.ForeignKey(PlantEval, models.PROTECT, limit_choices_to={'active': True})
    
    class Meta:
        verbose_name = 'Log Evaluasi Tanaman'

class PlantPlant(PlantBase):
    kode = models.CharField('Kode Tanaman', unique=True, max_length=20)
    
    def __str__(self):
        return '%s' % (self.kode)
    
    class Meta:
        verbose_name = 'Tanaman'
        
class PlantOpt(PlantBase):
    plant_plant = models.ForeignKey(PlantPlant, models.PROTECT, verbose_name="Kode Tanaman", limit_choices_to={'active': True})
    usia = models.FloatField('Usia Hari', default=0)
    
    def __str__(self):
        return '%s_%s' % (self.plant_plant.kode, self.usia)
    
    class Meta:
        verbose_name = 'Kondisi Optimal Tanaman'
        unique_together = ('plant_plant', 'usia')
        
class PlantOptDetail(PlantBase):
    plant_opt = models.ForeignKey(PlantOpt, models.PROTECT, limit_choices_to={'active': True})
    kode = models.CharField('Kode', max_length=3, choices=PlantBase.sensor_type)
    val = models.FloatField('Nilai')
    tol = FloatRangeField('Toleransi (%)', default=10, min_value=0, max_value=100)
    
    def __str__(self):
        return '%s_%s_%s' % (self.plant_opt.plant_plant.kode, self.plant_opt.usia, self.kode)
    
    class Meta:
        verbose_name = 'Detail Kondisi Optimal Tanaman'
        unique_together = ('plant_opt', 'kode')
    
class PlantSensor(PlantBase):
    kode = models.CharField('Kode Sensor', max_length=20, unique=True)
    url = models.URLField('URL Sensor', unique=True)
    
    def __str__(self):
        return self.kode
    
    class Meta:
        verbose_name = 'Sensor Tanaman'
        
class PlantSensorDetail(PlantBase):
    plant_sensor = models.ForeignKey(PlantSensor, models.PROTECT, limit_choices_to={'active': True})
    kode = models.CharField('Kode', max_length=3, choices=PlantBase.sensor_type)
    
    class Meta:
        verbose_name = 'Detail Sensor Tanaman'
        unique_together = ('plant_sensor', 'kode')
    
class PlantControl(PlantBase):
    kode = models.CharField('Kode Kontrol', max_length=20, unique=True)
    url = models.URLField('URL Kontrol', unique=True)
    
    def __str__(self):
        return self.kode
    
    class Meta:
        verbose_name = 'Kontrol Tanaman'
        
class PlantControlDetail(PlantBase):
    plant_control = models.ForeignKey(PlantControl, models.PROTECT, limit_choices_to={'active': True})
    kode = models.CharField('Kode', max_length=3, choices=PlantBase.control_pin)
    val = models.CharField('Nilai', max_length=2, choices=PlantBase.control_type, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Detail Control Tanaman'
        unique_together = ('plant_control', 'kode')
        
class PlantRack(PlantBase):
    kode = models.CharField('Kode Rak', max_length=20)
    plant_sensor = models.ForeignKey(PlantSensor, models.PROTECT, limit_choices_to={'active': True})
    plant_control = models.ForeignKey(PlantControl, models.PROTECT, limit_choices_to={'active': True})
    dt = models.DateTimeField('Tanggal Pasang', default=timezone.now, blank=True)
    p = models.FloatField('Panjang', null=True, blank=True)
    l = models.FloatField('Lebar', null=True, blank=True)
    t = models.FloatField('Tinggi', null=True, blank=True)
    type = models.CharField('Type', max_length=4, choices=PlantBase.rack_type, null=True, blank=True)
    
    def __str__(self):
        return self.kode
    
    class Meta:
        verbose_name = 'Rak Tanaman'
        
class PlantRackPoint(PlantBase):
    plant_plant = models.ForeignKey(PlantPlant, models.PROTECT, limit_choices_to={'active': True})
    plant_rack = models.ForeignKey(PlantRack, models.PROTECT, limit_choices_to={'active': True})
    dt = models.DateTimeField('Tanggal Tanam', default=timezone.now, blank=True)
    p = models.FloatField('Panjang', null=True, blank=True)
    l = models.FloatField('Lebar', null=True, blank=True)
    t = models.FloatField('Tinggi', null=True, blank=True)
    
    def __str__(self):
        return '%s_%s' % (self.plant_plant.kode, self.plant_rack.kode)
    
    class Meta:
        verbose_name = 'Point Tanaman'
    
class PlantControlLog(PlantBase):
    dt = models.DateTimeField('Start', default=timezone.now, blank=True)
    plant_control = models.ForeignKey(PlantControl, models.PROTECT, limit_choices_to={'active': True})
    plant_rack = models.ForeignKey(PlantRack, models.PROTECT, limit_choices_to={'active': True})
    
    def __str__(self):
        return '%s_%s_%s' % (self.plant_control.kode, self.plant_rack.kode, self.dt)
    
    class Meta:
        verbose_name = 'Log Kontrol Tanaman'
        ordering = ['-dt']
        
class PlantControlLogDetail(PlantBase):
    plant_control_log = models.ForeignKey(PlantControlLog, models.PROTECT, limit_choices_to={'active': True})
    kode = models.CharField('Kode', max_length=3, choices=PlantBase.control_pin)
    val = models.BooleanField('Nilai')
    
    class Meta:
        verbose_name = 'Detail Log Control Tanaman'
        unique_together = ('plant_control_log', 'kode')
        
class PlantSensorLog(PlantBase):
    dt = models.DateTimeField('Start', default=timezone.now, blank=True)
    plant_sensor = models.ForeignKey(PlantSensor, models.PROTECT, limit_choices_to={'active': True})
    plant_rack = models.ForeignKey(PlantRack, models.PROTECT, limit_choices_to={'active': True})
    
    def __str__(self):
        return '%s_%s_%s' % (self.plant_sensor.kode, self.plant_rack.kode, self.dt)
    
    class Meta:
        verbose_name = 'Log Sensor Tanaman'
        ordering = ['-dt']
        
class PlantSensorLogDetail(PlantBase):
    plant_sensor_log = models.ForeignKey(PlantSensorLog, models.PROTECT, limit_choices_to={'active': True})
    kode = models.CharField('Kode', max_length=3, choices=PlantBase.sensor_type)
    val = models.FloatField('Nilai', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Detail Log Sensor Tanaman'
        unique_together = ('plant_sensor_log', 'kode')