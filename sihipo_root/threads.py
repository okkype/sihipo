from sihipo_root.models import *

from django.db.models.aggregates import Max, Min
from datetime import datetime

import threading
import requests
import time
import json

import telegram
from sihipo.settings import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from telegram.ext import CommandHandler, Updater


class SensorThread(threading.Thread):
    interval = 1
#     hours = range(0, 24)
#     minutes = range(0, 60)
#     seconds = range(0, 60)
    stop = False
    
    def __init__(self, group=None, target=None, name='thread_sensor', args=(), kwargs=None, interval=1):
        self.interval = interval
        threading.Thread.__init__(self, group=group, target=target, name=name, args=args, kwargs=kwargs)
         
    def run(self):
        while True:
#             hour = datetime.now().hour
#             minute = datetime.now().minute
#             second = datetime.now().second
            if self.stop:
                break
            else:  # elif (hour in self.hours) and (minute in self.minutes) and (second in self.seconds):
                try:
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
#     hours = range(0, 24)
#     minutes = range(0, 60)
#     seconds = range(0, 60)
    stop = False
    
    def __init__(self, group=None, target=None, name='thread_control', args=(), kwargs=None, interval=1):
        self.interval = interval
        threading.Thread.__init__(self, group=group, target=target, name=name, args=args, kwargs=kwargs)
        
    def normalize(self, res, control):
        res_json = json.loads(res)
        values = res_json.get('value')
        if values:
            for i, value in enumerate(values):
                pins = control.plantcontrollogdetail_set.filter(kode='D%s' % (i))
                if pins:
                    for pin in pins:
                        pin.val = value
                        pin.save()
                else:
                    plant_control_log_detail = PlantControlLogDetail()
                    plant_control_log_detail.plant_control_log = control
                    plant_control_log_detail.kode = 'D%s' % (i)
                    plant_control_log_detail.val = value
                    plant_control_log_detail.save()
         
    def run(self):
        while True:
#             hour = datetime.now().hour
#             minute = datetime.now().minute
#             second = datetime.now().second
            if self.stop:
                break
            else:  # elif (hour in self.hours) and (minute in self.minutes) and (second in self.seconds):
                controls_min = PlantControlLog.objects.filter(state__in=['P']).values('plant_control').annotate(Min('dt')).order_by()
                for control_min in controls_min:
                    control = PlantControlLog.objects.filter(plant_control=control_min['plant_control'], dt=control_min['dt__min']).first()
                    pins_on = control.plantcontrollogdetail_set.filter(val=1)
                    pins_off = control.plantcontrollogdetail_set.filter(val=0)
                    pins_toggle = control.plantcontrollogdetail_set.filter(val=2)
                    pins_on_list = []
                    pins_off_list = []
                    pins_toggle_list = []
                    for pin_on in pins_on:
                        pins_on_list.append('p=%s' % (pin_on.kode[1:]))
                    for pin_off in pins_off:
                        pins_off_list.append('p=%s' % (pin_off.kode[1:]))
                    for pin_toggle in pins_toggle:
                        pins_toggle_list.append('p=%s' % (pin_toggle.kode[1:]))
                    if pins_on_list:
                        url = '%s/1?%s' % (control.plant_control.url.strip('/'), '&'.join(pins_on_list))
                        res = ''
                        try:
                            res = requests.get(url).text
                            self.normalize(res, control)
                        except Exception as e:
                            print(e)
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
                            self.normalize(res, control)
                        except Exception as e:
                            print(e)
                            res = e
                        finally:
                            pass
                        control.note = res
                        control.state = 'C'
                        racks = PlantRack.objects.filter(plant_control=control.plant_control, active=True)
                        for rack in racks:
                            control.plant_rack = rack
                        control.save()
                    if pins_toggle_list:
                        url = '%s/2?%s' % (control.plant_control.url.strip('/'), '&'.join(pins_toggle_list))
                        res = ''
                        try:
                            res = requests.get(url).text
                            self.normalize(res, control)
                        except Exception as e:
                            print(e)
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
#     hours = range(0, 24)
#     minutes = range(0, 60)
#     seconds = range(0, 60)
    stop = False
    
    def __init__(self, group=None, target=None, name='thread_eval', args=(), kwargs=None, interval=1):
        self.interval = interval
        threading.Thread.__init__(self, group=group, target=target, name=name, args=args, kwargs=kwargs)
         
    def run(self):
        while True:
#             hour = datetime.now().hour
#             minute = datetime.now().minute
#             second = datetime.now().second
            if self.stop:
                break
            else:  # elif (hour in self.hours) and (minute in self.minutes) and (second in self.seconds):
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

            
class TelegramThread(threading.Thread):
    stop = False
    text = ''
    __text__ = ''
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    updater = Updater(token=TELEGRAM_TOKEN)
    chat_id = TELEGRAM_CHAT_ID

    def __init__(self, group=None, target=None, name='thread_telegram', args=(), kwargs=None, verbose=None):
        threading.Thread.__init__(self, group=group, target=target, name=name, args=args, kwargs=kwargs, verbose=verbose)

    def run(self):
        try:

            def start(bot, update):
                chat_id = update.message.chat_id
                bot.send_message(chat_id=chat_id, text='Chat ID yang anda dapatkan adalah %s\nUntuk mengubah Chat ID bawaan perangkat anda, silahkan buka sihipo/settings.py kemudian cari TELEGRAM_CHAT_ID' % (chat_id))
    
            dispatcher = self.updater.dispatcher
            start_handler = CommandHandler('start', start)
            dispatcher.add_handler(start_handler)
            self.updater.start_polling()
            while True:
                if self.stop:
                    self.updater.stop()
                    break
                else:
                    try:
                        if self.text and (self.text != self.__text__):
                            if not self.chat_id or (self.chat_id == '0'):
                                self.chat_id = TELEGRAM_CHAT_ID
                            self.bot.send_message(chat_id=self.chat_id, text='%s\nhttp://sihipo.net' % (self.text))
                            self.__text__ = self.text
                    except Exception as e:
                        print(e)
        except Exception as e:
            print(e)
