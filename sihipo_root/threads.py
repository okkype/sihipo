from sihipo_root.models import *

from django.db.models.aggregates import Max

import threading
import requests
import time

class SensorThread(threading.Thread):
    stop = False
    interval = 1
    
    def __init__(self, group=None, target=None, name='thread_sensor', args=(), kwargs=None, verbose=None, interval=1):
        self.interval = interval
        threading.Thread.__init__(self, group=group, target=target, name=name, args=args, kwargs=kwargs, verbose=verbose)
         
    def run(self):
        while not self.stop:
            print self.name
            time.sleep(self.interval)

class ControlThread(threading.Thread):
    stop = False
    interval = 1
    
    def __init__(self, group=None, target=None, name='thread_control', args=(), kwargs=None, verbose=None, interval=1):
        self.interval = interval
        threading.Thread.__init__(self, group=group, target=target, name=name, args=args, kwargs=kwargs, verbose=verbose)
         
    def run(self):
        while not self.stop:
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
                    control.save()
            time.sleep(self.interval)

class EvalThread(threading.Thread):
    stop = False
    interval = 1
    
    def __init__(self, group=None, target=None, name='thread_eval', args=(), kwargs=None, verbose=None, interval=1):
        self.interval = interval
        threading.Thread.__init__(self, group=group, target=target, name=name, args=args, kwargs=kwargs, verbose=verbose)
         
    def run(self):
        while not self.stop:
            evls = PlantEval.objects.filter(active=True)
            for evl in evls:
                if evl.plant_eval_if.execute:
                    if evl.plant_eval_then.execute:
                        PlantEvalLog(plant_eval=evl).save()
            time.sleep(self.interval)