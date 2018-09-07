from sihipo_root.models import *

from django.db.models.aggregates import Max
from datetime import datetime

import threading
import requests
import time
import json

class SensorThread(threading.Thread):
    interval = 1
    hours = range(0, 24)
    minutes = range(0, 60)
    seconds = range(0, 60)
    stop = False
    
    def __init__(self, group=None, target=None, name='thread_sensor', args=(), kwargs=None, verbose=None, interval=1):
        self.interval = interval
        threading.Thread.__init__(self, group=group, target=target, name=name, args=args, kwargs=kwargs, verbose=verbose)
         
    def run(self):
        while True:
            hour = datetime.now().hour
            minute = datetime.now().minute
            second = datetime.now().second
            if self.stop:
                break
            elif (hour in self.hours) and (minute in self.minutes) and (second in self.seconds):
                try :
                    sensors = PlantSensor.objects.filter(active=True)
                    for sensor in sensors:
                        data = json.loads(requests.get(sensor.url).text)
                        # data = json.loads('{"id":"S01","type":"SIHIPO_S","value":{"PH":7.0,"EC":2.8,"HT":80.0,"TW":20.0,"TA":30.0,"LW":1.0}}')
                        sensor_log = PlantSensorLog()
                        sensor_log.plant_sensor = sensor
                        racks = PlantRack.objects.filter(plant_sensor=sensor, active=True)
                        for rack in racks:
                            sensor_log.plant_rack = rack
                        sensor_log.save()
                        sensor_log_empty = True
                        for sensor_type in PlantBase.sensor_type:
                            sensor_detail_off = PlantSensorDetail.objects.filter(plant_sensor=sensor, kode=sensor_type[0], active=False).count()
                            if sensor_detail_off:
                                pass
                            else:
                                value = data and data.get('value') and data.get('value').get(sensor_type[0])
                                if value:
                                    sensor_log_empty = False
                                    sensor_log_detail = PlantSensorLogDetail()
                                    sensor_log_detail.plant_sensor_log = sensor_log
                                    sensor_log_detail.kode = sensor_type[0]
                                    sensor_log_detail.val = value
                                    sensor_log_detail.save()
                        if sensor_log_empty:
                            sensor_log.delete()
                except Exception as e:
                    print(e)
            time.sleep(self.interval)

class ControlThread(threading.Thread):
    interval = 1
    hours = range(0, 24)
    minutes = range(0, 60)
    seconds = range(0, 60)
    stop = False
    
    def __init__(self, group=None, target=None, name='thread_control', args=(), kwargs=None, verbose=None, interval=1):
        self.interval = interval
        threading.Thread.__init__(self, group=group, target=target, name=name, args=args, kwargs=kwargs, verbose=verbose)
         
    def run(self):
        while True:
            hour = datetime.now().hour
            minute = datetime.now().minute
            second = datetime.now().second
            if self.stop:
                break
            elif (hour in self.hours) and (minute in self.minutes) and (second in self.seconds):
                controls_max = PlantControlLog.objects.filter(state__in=['P', 'C']).values('plant_control').annotate(Max('dt')).order_by()
                for control_max in controls_max:
                    control = PlantControlLog.objects.filter(plant_control=control_max['plant_control'], dt=control_max['dt__max']).first()
                    pins_on = control.plantcontrollogdetail_set.filter(val=True)
                    pins_off = control.plantcontrollogdetail_set.filter(val=False)
                    pins_on_list = []
                    pins_off_list = []
                    for pin_on in pins_on:
                        pins_on_list.append('p=%s' % (pin_on.kode[1:]))
                    for pin_off in pins_off:
                        pins_off_list.append('p=%s' % (pin_off.kode[1:]))
                    if pins_on_list:
                        url = '%s/1?%s' % (control.plant_control.url.strip('/'), '&'.join(pins_on_list))
                        res = ''
                        try:
                            res = requests.get(url).text
                        except Exception as e:
                            res = e
                        finally:
                            pass
                        control.note = res
                        control.state = 'C'
                        racks = PlantRack.objects.filter(plant_control=control.plant_control, active=True)
                        for rack in racks:
                            control.plant_rack = rack
                        control.save()
                    if pins_off_list:
                        url = '%s/0?%s' % (control.plant_control.url.strip('/'), '&'.join(pins_off_list))
                        res = ''
                        try:
                            res = requests.get(url).text
                        except Exception as e:
                            res = e
                        finally:
                            pass
                        control.note = res
                        control.state = 'C'
                        racks = PlantRack.objects.filter(plant_control=control.plant_control, active=True)
                        for rack in racks:
                            control.plant_rack = rack
                        control.save()
            time.sleep(self.interval)

class EvalThread(threading.Thread):
    interval = 1
    hours = range(0, 24)
    minutes = range(0, 60)
    seconds = range(0, 60)
    stop = False
    
    def __init__(self, group=None, target=None, name='thread_eval', args=(), kwargs=None, verbose=None, interval=1):
        self.interval = interval
        threading.Thread.__init__(self, group=group, target=target, name=name, args=args, kwargs=kwargs, verbose=verbose)
         
    def run(self):
        while True:
            hour = datetime.now().hour
            minute = datetime.now().minute
            second = datetime.now().second
            if self.stop:
                break
            elif (hour in self.hours) and (minute in self.minutes) and (second in self.seconds):
                eifs = PlantEvalIf.objects.filter(active=True, plant_eval_group__isnull=True)
                for eif in eifs:
                    if eif.execute:
                        es = PlantEval.objects.filter(active=True, plant_eval_if=eif)
                        for e in es:
                            if e.plant_eval_then.execute:
                                PlantEvalLog(plant_eval=e).save()
                        # break
                egs = PlantEvalGroup.objects.filter(active=True)
                for eg in egs:
                    eifs = PlantEvalIf.objects.filter(active=True, plant_eval_group=eg)
                    for eif in eifs:
                        if eif.execute:
                            es = PlantEval.objects.filter(active=True, plant_eval_if=eif)
                            for e in es:
                                if e.plant_eval_then.execute:
                                    PlantEvalLog(plant_eval=e).save()
                            break
            time.sleep(self.interval)
            
#         while not self.stop:
#             evls = PlantEval.objects.filter(active=True)
#             for evl in evls:
#                 if evl.plant_eval_if.execute:
#                     if evl.plant_eval_then.execute:
#                         PlantEvalLog(plant_eval=evl).save()
#             time.sleep(self.interval)