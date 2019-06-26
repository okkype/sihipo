'''
Created on 26 Jun 2019

@author: alif
'''
from django.contrib.staticfiles.management.commands.runserver import (
    Command as StaticRunserverCommand
)
from sihipo_root.threads import *
import threading


class Command(StaticRunserverCommand):
    
#     def handle(self, *args, **options):
#         super(Command, self).handle(*args, **options)

    def inner_run(self, *args, **options):
        thread_sensor_run = False
        thread_control_run = False
        thread_eval_run = False
         
        for t in threading.enumerate():
            if t.getName() == 'thread_sensor':
                thread_sensor_run = True
            if t.getName() == 'thread_control':
                thread_control_run = True
            if t.getName() == 'thread_eval':
                thread_eval_run = True
        
        if not thread_sensor_run:
            tf_sensor = SensorThread(interval=36000)
            tf_sensor.start()
            self.stdout.write(self.style.SUCCESS('Successfully start Sensor Thread'))
        if not thread_control_run:
            tf_control = ControlThread()
            tf_control.start()
            self.stdout.write(self.style.SUCCESS('Successfully start Control Thread'))
        if not thread_eval_run:
            tf_eval = EvalThread()
            tf_eval.start()
            self.stdout.write(self.style.SUCCESS('Successfully start Eval Thread'))
        self.stdout.write('')
        super(Command, self).inner_run(*args, **options)
