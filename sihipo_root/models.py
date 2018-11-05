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
    model_name = models.TextField('Nama Model', null=True, blank=True)
    note = models.TextField('Catatan', null=True, blank=True)
    active = models.BooleanField('Aktif', default=True)
    
    def __init__(self, *args, **kwargs):
        super(PlantBase, self).__init__(*args, **kwargs)
        self.model_name = self._meta.model_name
    
    sensor_type = (
        (None, 'N/A'),
        ('PH', 'Keasaman'),
        ('EC', 'Konduktifitas'),
        ('HT', 'Kelembapan'),
        ('TW', 'Suhu Air'),
        ('TA', 'Suhu Udara'),
        ('LW', 'Level Air'),
        ('BL', 'Level Baterai'),
        ('PA', 'Usia Tanam'),
    )
    
    control_type = (
        (None, 'N/A'),
        ('L', 'GROW LAMP'),
        ('S', 'SPRAY'),
        ('W', 'WATER PUMP'),
        ('A', 'AERIAL'),
        ('B', 'BLOWER'),
        ('M', 'MIXER'),
    )

    control_pin = (
        (None, 'N/A'),
        ('D0', 'Digital 0'),
        ('D1', 'Digital 1'),
        ('D2', 'Digital 2'),
        ('D3', 'Digital 3'),
        ('D4', 'Digital 4'),
        ('D5', 'Digital 5'),
        ('D6', 'Digital 6'),
        ('D7', 'Digital 7'),
    )

    rack_type = (
        (None, 'N/A'),
        ('NFT', 'Net Film'),
        ('DFT', 'Deep Flow'),
        ('WICK', 'Wick'),
    )

    log_state_type = (
        (None, 'N/A'),
        ('D', 'Draft'),
        ('P', 'To Do / Progress'),
        ('C', 'Done / Complete'),
    )
    
    alert_type = (
        (None, 'N/A'),
        ('N', 'Notice'),
        ('W', 'Warning'),
        ('S', 'Severe'),
    )
    
    device_type = (
        (None, 'N/A'),
        ('SIHIPO_C', 'Device Kontrol'),
        ('SIHIPO_S', 'Device Device'),
    )

# Create your models here.
class PlantEvalGroup(PlantBase):
    kode = models.CharField('Kode Group', unique=True, max_length=20)
    
    def __str__(self):
        return '%s' % (self.kode)
    
    class Meta:
        verbose_name = 'Group Logika'
    
class PlantEvalIf(PlantBase):
    kode = models.CharField('Kode Kondisi', unique=True, max_length=20)
    eval_if = models.TextField('Kode Python', unique=True)
    plant_eval_group = models.ForeignKey(PlantEvalGroup, models.PROTECT, verbose_name='Group', limit_choices_to={'active': True}, null=True, blank=True)
    prior = models.IntegerField('Prioritas', default=10)
    
    @property
    def execute(self):
        try:
            if eval(self.eval_if):
                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False
    
    def __str__(self):
        return '%s' % (self.kode)
    
    class Meta:
        verbose_name = 'Kondisi'
        unique_together = ('plant_eval_group', 'prior')
        ordering = ['plant_eval_group', 'prior']
        
class PlantEvalThen(PlantBase):
    kode = models.CharField('Kode Aksi', unique=True, max_length=20)
    eval_then = models.TextField('Kode Python', unique=True, default="# Gunakan __exec__ untuk mengembalikan nilai")
    
    @property
    def execute(self):
        __exec__ = True
        try:
            param = {'__exec__':__exec__}
            exec('from sihipo_root.models import *\r\n%s' % (self.eval_then), param)
            __exec__ = param['__exec__']
        except Exception as e:
            print(e)
            return False
        finally:
            return __exec__
    
    def __str__(self):
        return '%s' % (self.kode)
    
    class Meta:
        verbose_name = 'Aksi'

class PlantEval(PlantBase):
    plant_eval_if = models.ForeignKey(PlantEvalIf, models.PROTECT, verbose_name='Kondisi', limit_choices_to={'active': True})
    plant_eval_then = models.ForeignKey(PlantEvalThen, models.PROTECT, verbose_name='Aksi', limit_choices_to={'active': True})
    
    @property
    def execute(self):
        if self.plant_eval_if.execute:
            return self.plant_eval_then.execute
        else:
            return False
    
    def __str__(self):
        return '%s_%s' % (self.plant_eval_if.kode, self.plant_eval_then.kode)
    
    class Meta:
        verbose_name = 'Evaluasi Tanaman'
        unique_together = ('plant_eval_if', 'plant_eval_then')

class PlantEvalLog(PlantBase):
    dt = models.DateTimeField('Waktu', default=timezone.now, blank=True)
    plant_eval = models.ForeignKey(PlantEval, models.CASCADE, verbose_name='Evaluasi Tanaman', limit_choices_to={'active': True})
    
    class Meta:
        verbose_name = 'Log Evaluasi Tanaman'
        ordering = ['-dt']

class PlantPlant(PlantBase):
    kode = models.CharField('Kode Tanaman', unique=True, max_length=20)
    
    def __str__(self):
        return '%s' % (self.kode)
    
    class Meta:
        verbose_name = 'Tanaman'
        
class PlantOpt(PlantBase):
    plant_plant = models.ForeignKey(PlantPlant, models.PROTECT, verbose_name="Tanaman", limit_choices_to={'active': True})
    usia = models.FloatField('Usia Hari', default=0)
    
    def __str__(self):
        return '%s_%s' % (self.plant_plant.kode, self.usia)
    
    class Meta:
        verbose_name = 'Kondisi Optimal Tanaman'
        unique_together = ('plant_plant', 'usia')
        
class PlantOptDetail(PlantBase):
    plant_opt = models.ForeignKey(PlantOpt, models.PROTECT, verbose_name='Kondisi Optimal Tanaman', limit_choices_to={'active': True})
    kode = models.CharField('Kode', max_length=3, choices=PlantBase.sensor_type)
    val = models.FloatField('Nilai')
    tol = FloatRangeField('Toleransi (%)', default=10, min_value=0, max_value=100)
    
    def __str__(self):
        return '%s_%s_%s' % (self.plant_opt.plant_plant.kode, self.plant_opt.usia, self.kode)
    
    class Meta:
        verbose_name = 'Detail Kondisi Optimal Tanaman'
        unique_together = ('plant_opt', 'kode')
        
class PlantDevice(PlantBase):
    kode = models.CharField('Kode Device', max_length=20, unique=True)
    url = models.URLField('URL Device', unique=True)
    tipe = models.CharField('Tipe Device', max_length=10, choices=PlantBase.device_type)
    
    def __str__(self):
        return self.kode
    
    class Meta:
        verbose_name = 'Device Tanaman'
    
class PlantSensor(PlantDevice):    
    # dev_type = models.CharField('Tipe Device', max_length=10, choices=PlantBase.device_type, default='SIHIPO_S')
    
    def __init__(self, *args, **kwargs):
        super(PlantSensor, self).__init__(*args, **kwargs)
        self.tipe = 'SIHIPO_S'
    
    def __str__(self):
        return self.kode
    
    class Meta:
        verbose_name = 'Sensor Tanaman'
        
class PlantSensorDetail(PlantBase):
    plant_sensor = models.ForeignKey(PlantSensor, models.PROTECT, verbose_name='Sensor Tanaman', limit_choices_to={'active': True})
    kode = models.CharField('Kode', max_length=3, choices=PlantBase.sensor_type)
    
    class Meta:
        verbose_name = 'Detail Sensor Tanaman'
        unique_together = ('plant_sensor', 'kode')
    
class PlantControl(PlantDevice):    
    # dev_type = models.CharField('Tipe Device', max_length=10, choices=PlantBase.device_type, default='SIHIPO_C')
    
    def __init__(self, *args, **kwargs):
        super(PlantControl, self).__init__(*args, **kwargs)
        self.tipe = 'SIHIPO_C'
    
    def __str__(self):
        return self.kode
    
    class Meta:
        verbose_name = 'Kontrol Tanaman'
        
class PlantControlDetail(PlantBase):
    plant_control = models.ForeignKey(PlantControl, models.PROTECT, verbose_name='Kontrol Tanaman', limit_choices_to={'active': True})
    kode = models.CharField('Kode', max_length=3, choices=PlantBase.control_pin)
    val = models.CharField('Nilai', max_length=2, choices=PlantBase.control_type, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Detail Control Tanaman'
        unique_together = ('plant_control', 'kode')
        
class PlantRack(PlantBase):
    kode = models.CharField('Kode Rak', max_length=20)
    plant_sensor = models.ForeignKey(PlantSensor, models.PROTECT, verbose_name='Sensor Tanaman', limit_choices_to={'active': True})
    plant_control = models.ForeignKey(PlantControl, models.PROTECT, verbose_name='Kontrol Tanaman', limit_choices_to={'active': True})
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
    plant_plant = models.ForeignKey(PlantPlant, models.PROTECT, verbose_name='Tanaman', limit_choices_to={'active': True})
    plant_rack = models.ForeignKey(PlantRack, models.PROTECT, verbose_name='Rak Tanaman', limit_choices_to={'active': True})
    dt = models.DateTimeField('Tanggal Tanam', default=timezone.now, blank=True)
    p = models.FloatField('Panjang', null=True, blank=True)
    l = models.FloatField('Lebar', null=True, blank=True)
    t = models.FloatField('Tinggi', null=True, blank=True)
    
    def __str__(self):
        return '%s_%s' % (self.plant_plant.kode, self.plant_rack.kode)
    
    class Meta:
        verbose_name = 'Point Tanaman'
    
class PlantControlLog(PlantBase):
    dt = models.DateTimeField('Waktu', default=timezone.now, blank=True)
    state = models.CharField('Status', max_length=2, choices=PlantBase.log_state_type, null=True, blank=True)
    plant_control = models.ForeignKey(PlantControl, models.CASCADE, verbose_name='Kontrol Tanaman', limit_choices_to={'active': True})
    plant_rack = models.ForeignKey(PlantRack, models.SET_NULL, verbose_name='Rak Tanaman', limit_choices_to={'active': True}, null=True, blank=True)
    
    def __str__(self):
        return '%s_%s_%s' % (self.plant_control.kode, self.plant_rack and self.plant_rack.kode or '', self.dt)
    
    class Meta:
        verbose_name = 'Log Kontrol Tanaman'
        ordering = ['-dt']
        
class PlantControlLogDetail(PlantBase):
    plant_control_log = models.ForeignKey(PlantControlLog, models.CASCADE, verbose_name='Log Kontrol Tanaman', limit_choices_to={'active': True})
    kode = models.CharField('Kode', max_length=3, choices=PlantBase.control_pin)
    val = models.IntegerField('Nilai', default=0, choices=((0, 'Normally Close'), (1, 'Normally Open'), (2, 'Toggle')))
    
    class Meta:
        verbose_name = 'Detail Log Control Tanaman'
        unique_together = ('plant_control_log', 'kode')
        
class PlantSensorLog(PlantBase):
    dt = models.DateTimeField('Waktu', default=timezone.now, blank=True)
    state = models.CharField('Status', max_length=2, choices=PlantBase.log_state_type, null=True, blank=True)
    plant_sensor = models.ForeignKey(PlantSensor, models.CASCADE, verbose_name='Sensor Tanaman', limit_choices_to={'active': True})
    plant_rack = models.ForeignKey(PlantRack, models.SET_NULL, verbose_name='Rak Tanaman', limit_choices_to={'active': True}, null=True, blank=True)
    
    def __str__(self):
        return '%s_%s_%s' % (self.plant_sensor.kode, self.plant_rack and self.plant_rack.kode or '', self.dt)
    
    class Meta:
        verbose_name = 'Log Sensor Tanaman'
        ordering = ['-dt']
        
class PlantSensorLogDetail(PlantBase):
    plant_sensor_log = models.ForeignKey(PlantSensorLog, models.CASCADE, verbose_name='Log Sensor Tanaman', limit_choices_to={'active': True})
    kode = models.CharField('Kode', max_length=3, choices=PlantBase.sensor_type)
    val = models.FloatField('Nilai', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Detail Log Sensor Tanaman'
        unique_together = ('plant_sensor_log', 'kode')
        
class PlantAlert(PlantBase):
    dt = models.DateTimeField('Waktu', default=timezone.now, blank=True)
    url = models.CharField('URL Aksi', max_length=255, default='#')
    state = models.CharField('Status', max_length=2, choices=PlantBase.alert_type, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Berita Tanaman'
        ordering = ['-dt']
