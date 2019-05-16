from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.db.models.aggregates import Avg, Count
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.datetime_safe import strftime
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from sihipo.settings import TELEGRAM_CHAT_ID, PWA_APP_SINGLE
from sihipo_root.models import *
from sihipo_root.threads import *
import subprocess
import threading
import time, datetime


# START HOME
class HomeView(TemplateView):
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['pwa_app_single'] = PWA_APP_SINGLE
        try:
            context['git_version'] = subprocess.check_output(['git', 'describe', '--tags']).strip().split('-')[0]
        except:
            context['git_version'] = ''
        return context
    
# END HOME


# START DASHBOARD
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'main.html'
    login_url = '/login/'
    
    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        # context['verbose_name'] = 'Dashboard'
        context['pwa_app_single'] = PWA_APP_SINGLE
        
        day_count = 10
        xdata_line = []
        days = day_count
        while days >= 0:
            xdata_line.append(int(time.mktime((datetime.datetime.now() - datetime.timedelta(days=days)).timetuple()) * 1000))
            days -= 1
        tooltip_date_line = "%d %b %Y %H:%M:%S %p"
        extra_serie_line = {"tooltip": {"y_start": "", "y_end": ""},
                       "date_format": tooltip_date_line}
        
        chartdata_sensor = {'x': xdata_line}
        chartseq_sensor = 1
        for sensor_type in PlantBase.sensor_type:
            if sensor_type[0] is not None:
                chartdata_sensor['name%s' % (chartseq_sensor)] = sensor_type[1]
                chartdata_sensor['extra%s' % (chartseq_sensor)] = extra_serie_line
                ydata_sensor = []
                days = day_count
                while days >= 0:
                    last_day = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime('%Y-%m-%d')
                    val = PlantSensorLogDetail.objects.filter(kode=sensor_type[0], plant_sensor_log__dt__range=('%s 00:00:00' % (last_day), '%s 23:59:59' % (last_day))).aggregate(Avg('val'))
                    ydata_sensor.append(val['val__avg'] or 0.0)
                    days -= 1
                chartdata_sensor['y%s' % (chartseq_sensor)] = ydata_sensor
                chartseq_sensor += 1
        
        context['charttype_sensor'] = 'lineChart'
        context['chartdata_sensor'] = chartdata_sensor
        context['extra_sensor'] = {
            'x_is_date': True,
            'x_axis_format': '%d/%b/%y',
        }
        
        xdata_plant = []
        ydata_plant = []
        extra_serie_plant = {"tooltip": {"y_start": "", "y_end": ""}}
        plant_types = PlantPlant.objects.filter(active=True)
        valAll = PlantRackPoint.objects.aggregate(Count('plant_plant'))
        for plant_type in plant_types:
            val = PlantRackPoint.objects.filter(plant_plant=plant_type).aggregate(Count('plant_plant'))
            if val['plant_plant__count']:
                xdata_plant.append("%s (%s/%s)" % (plant_type.kode, val['plant_plant__count'], valAll['plant_plant__count']))
                ydata_plant.append(val['plant_plant__count'])
        chartdata_plant = {'x': xdata_plant, 'y1': ydata_plant, 'extra1': extra_serie_plant}
        
        context['charttype_plant'] = 'pieChart'
        context['chartdata_plant'] = chartdata_plant

        return context

# END DASHBOARD


# START SETTING
class SettingView(LoginRequiredMixin, TemplateView):
    template_name = 'setting.html'
    login_url = '/login/'
    
    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(SettingView, self).get_context_data(**kwargs)
        context['verbose_name'] = 'Setting'
        context['pwa_app_single'] = PWA_APP_SINGLE

        for t in threading.enumerate():
            if t.getName() == 'thread_sensor':
                context['thread_sensor_run'] = True
                context['intval_sensor_run'] = t.interval
                if str(self.request.POST.get('thread_sensor')).startswith('Stop'):
                    context['thread_sensor_run'] = False
                    t.stop = True
            if t.getName() == 'thread_control':
                context['thread_control_run'] = True
                context['intval_control_run'] = 1 # t.interval
                if str(self.request.POST.get('thread_control')).startswith('Stop'):
                    context['thread_control_run'] = False
                    t.stop = True
            if t.getName() == 'thread_eval':
                context['thread_eval_run'] = True
                context['intval_eval_run'] = 1 # t.interval
                if str(self.request.POST.get('thread_eval')).startswith('Stop'):
                    context['thread_eval_run'] = False
                    t.stop = True
            if t.getName() == 'thread_telegram':
                context['thread_telegram_run'] = True
                context['intval_telegram_run'] = t.chat_id
                if str(self.request.POST.get('thread_telegram')).startswith('Stop'):
                    context['thread_telegram_run'] = False
                    context['intval_telegram_run'] = '0'
                    t.stop = True
                    
        if str(self.request.POST.get('thread_sensor')).startswith('Start'):
            context['thread_sensor_run'] = True
            context['intval_sensor_run'] = int(self.request.POST.get('intval_sensor', 1))
            tf = SensorThread(interval=context['intval_sensor_run'])
            tf.start()
        if str(self.request.POST.get('thread_control')).startswith('Start'):
            context['thread_control_run'] = True
            context['intval_control_run'] = int(self.request.POST.get('intval_control', 1))
            tf = ControlThread() # (interval=context['intval_control_run'])
            tf.start()
        if str(self.request.POST.get('thread_eval')).startswith('Start'):
            context['thread_eval_run'] = True
            context['intval_eval_run'] = int(self.request.POST.get('intval_eval', 1))
            tf = EvalThread() # (interval=context['intval_eval_run'])
            tf.start()
        if str(self.request.POST.get('thread_telegram')).startswith('Start'):
            context['thread_telegram_run'] = True
            context['intval_telegram_run'] = int(self.request.POST.get('intval_telegram', TELEGRAM_CHAT_ID)) or TELEGRAM_CHAT_ID
            tf = TelegramThread()
            tf.chat_id = context['intval_telegram_run']
            tf.start()
        if self.request.POST.get('command') == 'Clear All Log':
            PlantEvalLog.objects.all().update(active=False)
            PlantControlLog.objects.all().update(active=False)
            PlantSensorLog.objects.all().update(active=False)
        if self.request.POST.get('command') == 'trash' and self.request.POST.get('model'):
            eval("%s.objects.filter(pk__in=%s, active=True).update(active=False)" % (self.request.POST.get('model'), self.request.POST.get('pks')))
#             filter_str = str(self.request.POST.get('filter')).strip()
#             filter_query = str(self.request.POST.get('filter_query')).strip()
#             if (filter_str != 'None') and (filter_query != 'None'):
#                 eval("%s.objects.filter(%s).update(active=False)" % (self.request.POST.get('model'), filter_query.replace('context[&#39;filter&#39;]', "'%s'" % (filter_str))))
#             else:
#                 eval("%s.objects.all().update(active=False)" % (self.request.POST.get('model')))
        if self.request.POST.get('command') == 'empty' and self.request.POST.get('model'):
            eval("%s.objects.filter(active=False).delete()" % (self.request.POST.get('model')))
#             filter_str = str(self.request.POST.get('filter')).strip()
#             filter_query = str(self.request.POST.get('filter_query')).strip()
#             if (filter_str != 'None') and (filter_query != 'None'):
#                 eval("%s.objects.filter(Q(active=False)&(%s)).delete()" % (self.request.POST.get('model'), filter_query.replace('context[&#39;filter&#39;]', "'%s'" % (filter_str))))
#             else:
#                 eval("%s.objects.filter(active=False).delete()" % (self.request.POST.get('model')))
        try:
            f = open('/var/lib/misc/dnsmasq.leases', 'r')
            context['ip_list'] = f.read()
            if self.request.POST.get('command') == 'Tambahkan ke Sensor/Kontrol':
                split_lines = str(self.request.POST.get('ip_list')).split('\n')
                for split_line in split_lines:
                    split_spaces = split_line.split(' ')
                    if len(split_spaces) > 3:
                        try:
                            url = 'http://%s' % (split_spaces[2])
                            res_json = requests.get(url, timeout=5).json()
                            tipe = res_json.get('type')
                            kode = str(split_spaces[1]).upper() if (split_spaces[1] not in ['', '*']) else split_spaces[3] if (split_spaces[3] not in ['', '*']) else res_json.get('id')
                            if tipe:
                                if tipe.upper() == 'SIHIPO_C':
                                    controls = PlantControl.objects.filter(Q(kode=kode) | Q(url=url))
                                    if controls:
                                        for control in controls:
                                            control.kode = kode
                                            control.url = url
                                            control.save()
                                    else:
                                        control = PlantControl()
                                        control.kode = kode
                                        control.url = url
                                        control.save()
                                elif tipe.upper() == 'SIHIPO_S':
                                    sensors = PlantSensor.objects.filter(Q(kode=kode) | Q(url=url))
                                    if sensors:
                                        for sensor in sensors:
                                            sensor.kode = kode
                                            sensor.url = url
                                            sensor.save()
                                    else:
                                        sensor = PlantSensor()
                                        sensor.kode = kode
                                        sensor.url = url
                                        sensor.save()
                        except Exception as e:
                            print(e)
        except Exception as e:
            context['ip_list'] = '%s' % (e)
        return context
    
# END SETTING


# START BASIC VIEW MOD
def get_plant_context(obj, context):
    context['name'] = obj.model._meta.model_name
    context['verbose_name'] = obj.model._meta.verbose_name
    context['referer'] = obj.request.META.get('HTTP_REFERER')
    context['search_field'] = [u'CharField', u'TextField']
    context['numeric_field'] = [u'IntegerField', u'FloatField']
    context['datetime_fields'] = []
    context['pwa_app_single'] = PWA_APP_SINGLE
    for field in obj.fields:
        if obj.model._meta.get_field(field).get_internal_type() in [u'DateTimeField']:
            context['datetime_fields'].append(field)
    return context


class PlantListView(LoginRequiredMixin, ListView):
    login_url = '/login/'
    paginate_by = 10
    is_child = False
    
    def get_paginate_by(self, queryset):
        if self.request.GET.get('filter') or (self.is_child and self.request.session.get('parent_id')):
            return 0
        return ListView.get_paginate_by(self, queryset)
    
    def get_ordering(self):
        sort = self.request.GET.get('sort') or self.request.session.get('sort')
        if sort and (sort in self.fields):
            self.request.session['sort'] = sort
            return sort
        else:
            return super(PlantListView, self).get_ordering()
        
    def get_context_data(self, **kwargs):
        context = get_plant_context(self, super(PlantListView, self).get_context_data(**kwargs))
        if not self.is_child and self.request.session.get('parent_id'):
            del self.request.session['parent_id']
        # if self.request.GET.get('filter') or (self.is_child and self.request.session.get('parent_id')):
        # if self.is_child and self.request.session.get('parent_id'):
        #     context['table_extra'] = False
        # else:
        context['table_extra'] = True
        context['table_fields'] = self.fields
        context['table_model'] = self.model.__name__
        context['filter'] = self.request.GET.get('filter')
        context['filter_query'] = None
        # context['is_child'] = self.is_child
        # context['parent_id'] = self.request.session.get('parent_id')
        if context['filter']:
            self.paginate_by = False
            context['pwa_app_single'] = False
            eval_obj = []
            for table_field in self.fields:
                if self.model._meta.get_field(table_field).get_internal_type() in context['search_field']:
                    eval_obj.append('Q(%s__icontains=context[\'filter\'])' % (table_field))
            if eval_obj:
                context['filter_query'] = '|'.join(eval_obj)
                context['object_list'] = eval('self.model.objects.filter(%s)' % (context['filter_query']))
        context['table_fields'] = self.fields
        context['table_headers'] = {}
        for table_field in context['table_fields']:
            context['table_headers'][table_field] = self.model._meta.get_field(table_field).verbose_name
        return context


class PlantCreateView(LoginRequiredMixin, CreateView):
    login_url = '/login/'
    
    def form_valid(self, form):
        ret = super(PlantCreateView, self).form_valid(form)
        obj = form.save()
        obj.created_by = self.request.user
        obj.updated_by = self.request.user
        obj.save()
        return ret
    
    def get_context_data(self, **kwargs):
        context = get_plant_context(self, super(PlantCreateView, self).get_context_data(**kwargs))
        return context


class PlantUpdateView(LoginRequiredMixin, UpdateView):
    login_url = '/login/'
    
    def form_valid(self, form):
        ret = super(PlantUpdateView, self).form_valid(form)
        obj = form.save()
        # obj.created_by = self.request.user
        obj.updated_by = self.request.user
        obj.save()
        return ret
    
    def get_context_data(self, **kwargs):
        context = get_plant_context(self, super(PlantUpdateView, self).get_context_data(**kwargs))
        return context


class PlantDeleteView(LoginRequiredMixin, DeleteView):
    login_url = '/login/'
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.active:
            self.object.active = False
            self.object.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return super(PlantDeleteView, self).delete(self, request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = get_plant_context(self, super(PlantDeleteView, self).get_context_data(**kwargs))
        return context

# END BASIC VIEW MOD

    
# PlantPlant
class PlantPlantView(object):
    model = PlantPlant
    fields = ['kode', 'note', 'active']
    success_url = reverse_lazy('plantplant_list')


class PlantPlantList(PlantPlantView, PlantListView):
    pass


class PlantPlantCreate(PlantPlantView, PlantCreateView):
    pass


class PlantPlantUpdate(PlantPlantView, PlantUpdateView):
    pass


class PlantPlantDelete(PlantPlantView, PlantDeleteView):
    pass


# PlantOpt
class PlantOptView(object):
    model = PlantOpt
    fields = ['plant_plant', 'usia', 'note', 'active']
    success_url = reverse_lazy('plantopt_list')


class PlantOptList(PlantOptView, PlantListView):
    pass


class PlantOptCreate(PlantOptView, PlantCreateView):
    pass


class PlantOptUpdate(PlantOptView, PlantUpdateView):

    def get_context_data(self, **kwargs):
        context = super(PlantOptUpdate, self).get_context_data(**kwargs)
        context['link_list'] = [
            {
                'name':'Detail Kondisi Optimal Tanaman',
                'link':reverse_lazy('plantoptdetail_list')
            }
        ]
        self.request.session['parent_id'] = context['object'].id
        return context


class PlantOptDelete(PlantOptView, PlantDeleteView):
    pass


# PlantOptDetail
class PlantOptDetailView(object):
    model = PlantOptDetail
    fields = ['plant_opt', 'kode', 'val', 'tol', 'active']
    success_url = reverse_lazy('plantoptdetail_list')
    is_child = True


class PlantOptDetailList(PlantOptDetailView, PlantListView):

    def get_context_data(self, **kwargs):
        context = super(PlantOptDetailList, self).get_context_data(**kwargs)
        context['object_list'] = self.model.objects.filter(plant_opt=self.request.session.get('parent_id'))
        return context


class PlantOptDetailCreate(PlantOptDetailView, PlantCreateView):

    def get_initial(self):
        context = super(PlantOptDetailCreate, self).get_initial()
        context['plant_opt'] = self.request.session.get('parent_id')
        return context


class PlantOptDetailUpdate(PlantOptDetailView, PlantUpdateView):
    pass


class PlantOptDetailDelete(PlantOptDetailView, PlantDeleteView):
    pass

    
# PlantSensor
class PlantSensorView(object):
    model = PlantSensor
    fields = ['kode', 'url', 'active']
    success_url = reverse_lazy('plantsensor_list')


class PlantSensorList(PlantSensorView, PlantListView):
    pass


class PlantSensorCreate(PlantSensorView, PlantCreateView):
    pass


class PlantSensorUpdate(PlantSensorView, PlantUpdateView):

    def get_context_data(self, **kwargs):
        context = super(PlantSensorUpdate, self).get_context_data(**kwargs)
        context['link_list'] = [
            {
                'name':'Detail Sensor',
                'link':reverse_lazy('plantsensordetail_list')
            },
            {
                'name':'Dashboard Sensor',
                'link':reverse_lazy('plantsensor_dashboard')
            }
        ]
        self.request.session['parent_id'] = context['object'].id
        return context


class PlantSensorDelete(PlantSensorView, PlantDeleteView):
    pass


class PlantSensorDashboard(TemplateView):
    template_name = 'dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super(PlantSensorDashboard, self).get_context_data(**kwargs)
        context['verbose_name'] = 'Rata-rata Sensor'
        
        day_count = 30
        xdata = []
        days = day_count
        while days >= 0:
            xdata.append(int(time.mktime((datetime.datetime.now() - datetime.timedelta(days=days)).timetuple()) * 1000))
            days -= 1
        tooltip_date = "%d %b %Y %H:%M:%S %p"
        extra_serie = {"tooltip": {"y_start": "", "y_end": ""},
                       "date_format": tooltip_date}
        
        chartdata = {'x': xdata}
        chartseq = 1
        for sensor_type in PlantBase.sensor_type:
            if sensor_type[0] is not None:
                chartdata['name%s' % (chartseq)] = sensor_type[1]
                chartdata['extra%s' % (chartseq)] = extra_serie
                ydata = []
                days = day_count
                while days >= 0:
                    last_day = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime('%Y-%m-%d')
                    val = PlantSensorLogDetail.objects.filter(kode=sensor_type[0], plant_sensor_log__plant_sensor=self.request.session.get('parent_id'), plant_sensor_log__dt__range=('%s 00:00:00' % (last_day), '%s 23:59:59' % (last_day))).aggregate(Avg('val'))
                    ydata.append(val['val__avg'] or 0.0)
                    days -= 1
                chartdata['y%s' % (chartseq)] = ydata
                chartseq += 1
        context['charttype'] = 'lineWithFocusChart'
        context['chartdata'] = chartdata
        context['extra'] = {
            'x_is_date': True,
            'x_axis_format': '%d/%b/%y',
        }

        return context


# PlantSensorDetail
class PlantSensorDetailView(object):
    model = PlantSensorDetail
    fields = ['plant_sensor', 'kode', 'active']
    success_url = reverse_lazy('plantsensordetail_list')
    is_child = True


class PlantSensorDetailList(PlantSensorDetailView, PlantListView):

    def get_context_data(self, **kwargs):
        context = super(PlantSensorDetailList, self).get_context_data(**kwargs)
        context['object_list'] = self.model.objects.filter(plant_sensor=self.request.session.get('parent_id'))
        return context


class PlantSensorDetailCreate(PlantSensorDetailView, PlantCreateView):

    def get_initial(self):
        context = super(PlantSensorDetailCreate, self).get_initial()
        context['plant_sensor'] = self.request.session.get('parent_id')
        return context


class PlantSensorDetailUpdate(PlantSensorDetailView, PlantUpdateView):
    pass


class PlantSensorDetailDelete(PlantSensorDetailView, PlantDeleteView):
    pass

    
# PlantControl
class PlantControlView(object):
    model = PlantControl
    fields = ['kode', 'url', 'active']
    success_url = reverse_lazy('plantcontrol_list')


class PlantControlList(PlantControlView, PlantListView):
    pass


class PlantControlCreate(PlantControlView, PlantCreateView):
    pass


class PlantControlUpdate(PlantControlView, PlantUpdateView):

    def get_context_data(self, **kwargs):
        context = super(PlantControlUpdate, self).get_context_data(**kwargs)
        context['link_list'] = [
            {
                'name':'Detail Kontrol',
                'link':reverse_lazy('plantcontroldetail_list')
            },
            {
                'name':'Dashboard Kontrol',
                'link':reverse_lazy('plantcontrol_dashboard')
            }
        ]
        self.request.session['parent_id'] = context['object'].id
        return context


class PlantControlDelete(PlantControlView, PlantDeleteView):
    pass


class PlantControlDashboard(TemplateView):
    template_name = 'dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super(PlantControlDashboard, self).get_context_data(**kwargs)
        context['verbose_name'] = 'Total Kontrol'
        
        day_count = 30
        xdata = []
        days = day_count
        while days >= 0:
            xdata.append(int(time.mktime((datetime.datetime.now() - datetime.timedelta(days=days)).timetuple()) * 1000))
            days -= 1
        tooltip_date = "%d %b %Y %H:%M:%S %p"
        extra_serie = {"tooltip": {"y_start": "", "y_end": ""},
                       "date_format": tooltip_date}
        
        chartdata = {'x': xdata}
        chartseq = 1
        for control_type in PlantBase.control_type:
            if control_type[0] is not None:
                control_details = PlantControlDetail.objects.filter(val=control_type[0], plant_control=self.request.session.get('parent_id'))
                for control_detail in control_details:
                    chartdata['name%s' % (chartseq)] = control_detail.get_val_display()
                    chartdata['extra%s' % (chartseq)] = extra_serie
                    ydata = []
                    days = day_count
                    while days >= 0:
                        last_day = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime('%Y-%m-%d')
                        val = PlantControlLogDetail.objects.filter(val=1, kode=control_detail.kode, plant_control_log__plant_control=self.request.session.get('parent_id'), plant_control_log__dt__range=('%s 00:00:00' % (last_day), '%s 23:59:59' % (last_day))).aggregate(Count('val'))
                        ydata.append(val['val__count'] or 0.0)
                        days -= 1
                    chartdata['y%s' % (chartseq)] = ydata
                    chartseq += 1
        context['charttype'] = 'lineWithFocusChart'
        context['chartdata'] = chartdata
        context['extra'] = {
            'x_is_date': True,
            'x_axis_format': '%d/%b/%y',
        }

        return context


# PlantControlDetail
class PlantControlDetailView(object):
    model = PlantControlDetail
    fields = ['plant_control', 'kode', 'val', 'active']
    success_url = reverse_lazy('plantcontroldetail_list')
    is_child = True


class PlantControlDetailList(PlantControlDetailView, PlantListView):

    def get_context_data(self, **kwargs):
        context = super(PlantControlDetailList, self).get_context_data(**kwargs)
        context['object_list'] = self.model.objects.filter(plant_control=self.request.session.get('parent_id'))
        return context


class PlantControlDetailCreate(PlantControlDetailView, PlantCreateView):

    def get_initial(self):
        context = super(PlantControlDetailCreate, self).get_initial()
        context['plant_control'] = self.request.session.get('parent_id')
        return context


class PlantControlDetailUpdate(PlantControlDetailView, PlantUpdateView):
    pass


class PlantControlDetailDelete(PlantControlDetailView, PlantDeleteView):
    pass

    
# PlantRack
class PlantRackView(object):
    model = PlantRack
    fields = ['kode', 'plant_control', 'plant_sensor', 'dt', 'p', 'l', 't', 'type', 'active']
    success_url = reverse_lazy('plantrack_list')


class PlantRackList(PlantRackView, PlantListView):
    pass


class PlantRackCreate(PlantRackView, PlantCreateView):
    pass


class PlantRackUpdate(PlantRackView, PlantUpdateView):

    def get_context_data(self, **kwargs):
        context = super(PlantRackUpdate, self).get_context_data(**kwargs)
        context['link_list'] = [
            {
                'name':'Titik Tanam',
                'link':reverse_lazy('plantrackpoint_list')
            }
        ]
        self.request.session['parent_id'] = context['object'].id
        return context


class PlantRackDelete(PlantRackView, PlantDeleteView):
    pass


# PlantRackPoint
class PlantRackPointView(object):
    model = PlantRackPoint
    fields = ['plant_rack', 'plant_plant', 'dt', 'p', 'l', 't', 'active']
    success_url = reverse_lazy('plantrackpoint_list')
    is_child = True


class PlantRackPointList(PlantRackPointView, PlantListView):

    def get_context_data(self, **kwargs):
        context = super(PlantRackPointList, self).get_context_data(**kwargs)
        context['object_list'] = self.model.objects.filter(plant_rack=self.request.session.get('parent_id'))
        return context


class PlantRackPointCreate(PlantRackPointView, PlantCreateView):

    def get_initial(self):
        context = super(PlantRackPointCreate, self).get_initial()
        context['plant_rack'] = self.request.session.get('parent_id')
        return context


class PlantRackPointUpdate(PlantRackPointView, PlantUpdateView):
    pass


class PlantRackPointDelete(PlantRackPointView, PlantDeleteView):
    pass


# PlantSensorLog
class PlantSensorLogView(object):
    model = PlantSensorLog
    fields = ['dt', 'plant_sensor', 'plant_rack', 'state', 'active']
    success_url = reverse_lazy('plantsensorlog_list')


class PlantSensorLogList(PlantSensorLogView, PlantListView):
    pass


class PlantSensorLogCreate(PlantSensorLogView, PlantCreateView):
    pass


class PlantSensorLogUpdate(PlantSensorLogView, PlantUpdateView):

    def get_context_data(self, **kwargs):
        context = super(PlantSensorLogUpdate, self).get_context_data(**kwargs)
        context['link_list'] = [
            {
                'name':'Detail Log Sensor',
                'link':reverse_lazy('plantsensorlogdetail_list')
            }
        ]
        self.request.session['parent_id'] = context['object'].id
        return context


class PlantSensorLogDelete(PlantSensorLogView, PlantDeleteView):
    pass


# PlantSensorLogDetail
class PlantSensorLogDetailView(object):
    model = PlantSensorLogDetail
    fields = ['plant_sensor_log', 'kode', 'val', 'note', 'active']
    success_url = reverse_lazy('plantsensorlogdetail_list')
    is_child = True


class PlantSensorLogDetailList(PlantSensorLogDetailView, PlantListView):

    def get_context_data(self, **kwargs):
        context = super(PlantSensorLogDetailList, self).get_context_data(**kwargs)
        context['object_list'] = self.model.objects.filter(plant_sensor_log=self.request.session.get('parent_id'))
        return context


class PlantSensorLogDetailCreate(PlantSensorLogDetailView, PlantCreateView):

    def get_initial(self):
        context = super(PlantSensorLogDetailCreate, self).get_initial()
        context['plant_sensor_log'] = self.request.session.get('parent_id')
        return context


class PlantSensorLogDetailUpdate(PlantSensorLogDetailView, PlantUpdateView):
    fields = ['kode', 'val', 'note', 'active']


class PlantSensorLogDetailDelete(PlantSensorLogDetailView, PlantDeleteView):
    pass

    
# PlantControlLog
class PlantControlLogView(object):
    model = PlantControlLog
    fields = ['dt', 'plant_control', 'plant_rack', 'state', 'note', 'active']
    success_url = reverse_lazy('plantcontrollog_list')


class PlantControlLogList(PlantControlLogView, PlantListView):
    pass


class PlantControlLogCreate(PlantControlLogView, PlantCreateView):
    pass


class PlantControlLogUpdate(PlantControlLogView, PlantUpdateView):

    def get_context_data(self, **kwargs):
        context = super(PlantControlLogUpdate, self).get_context_data(**kwargs)
        context['link_list'] = [
            {
                'name':'Detail Log Control',
                'link':reverse_lazy('plantcontrollogdetail_list')
            }
        ]
        self.request.session['parent_id'] = context['object'].id
        return context


class PlantControlLogDelete(PlantControlLogView, PlantDeleteView):
    pass


# PlantControlLogDetail
class PlantControlLogDetailView(object):
    model = PlantControlLogDetail
    fields = ['plant_control_log', 'kode', 'val', 'active']
    success_url = reverse_lazy('plantcontrollogdetail_list')
    is_child = True


class PlantControlLogDetailList(PlantControlLogDetailView, PlantListView):

    def get_context_data(self, **kwargs):
        context = super(PlantControlLogDetailList, self).get_context_data(**kwargs)
        context['object_list'] = self.model.objects.filter(plant_control_log=self.request.session.get('parent_id'))
        return context


class PlantControlLogDetailCreate(PlantControlLogDetailView, PlantCreateView):

    def get_initial(self):
        context = super(PlantControlLogDetailCreate, self).get_initial()
        context['plant_control_log'] = self.request.session.get('parent_id')
        return context


class PlantControlLogDetailUpdate(PlantControlLogDetailView, PlantUpdateView):
    fields = ['kode', 'val', 'active']


class PlantControlLogDetailDelete(PlantControlLogDetailView, PlantDeleteView):
    pass


# PlantEvalGroup
class PlantEvalGroupView(object):
    model = PlantEvalGroup
    fields = ['kode', 'active']
    success_url = reverse_lazy('plantevalgroup_list')


class PlantEvalGroupList(PlantEvalGroupView, PlantListView):
    pass


class PlantEvalGroupCreate(PlantEvalGroupView, PlantCreateView):
    pass


class PlantEvalGroupUpdate(PlantEvalGroupView, PlantUpdateView):
    pass


class PlantEvalGroupDelete(PlantEvalGroupView, PlantDeleteView):
    pass


# PlantEvalIf
class PlantEvalIfView(object):
    model = PlantEvalIf
    fields = ['kode', 'eval_if', 'plant_eval_group', 'prior', 'active']
    success_url = reverse_lazy('plantevalif_list')


class PlantEvalIfList(PlantEvalIfView, PlantListView):
    fields = ['kode', 'plant_eval_group', 'prior', 'active']


class PlantEvalIfCreate(PlantEvalIfView, PlantCreateView):
    pass


class PlantEvalIfUpdate(PlantEvalIfView, PlantUpdateView):

    def get_context_data(self, **kwargs):
        context = super(PlantEvalIfUpdate, self).get_context_data(**kwargs)
        context['link_list'] = [
            {
                'name':'Aksi',
                'link':reverse_lazy('planteval_list')
            }
        ]
        self.request.session['parent_id'] = context['object'].id
        return context


class PlantEvalIfDelete(PlantEvalIfView, PlantDeleteView):
    pass


# PlantEvalThen
class PlantEvalThenView(object):
    model = PlantEvalThen
    fields = ['kode', 'eval_then', 'active']
    success_url = reverse_lazy('plantevalthen_list')


class PlantEvalThenList(PlantEvalThenView, PlantListView):
    fields = ['kode', 'active']


class PlantEvalThenCreate(PlantEvalThenView, PlantCreateView):
    pass


class PlantEvalThenUpdate(PlantEvalThenView, PlantUpdateView):
    pass


class PlantEvalThenDelete(PlantEvalThenView, PlantDeleteView):
    pass


# PlantEval
class PlantEvalView(object):
    model = PlantEval
    fields = ['plant_eval_if', 'plant_eval_then', 'active']
    success_url = reverse_lazy('planteval_list')
    is_child = True


class PlantEvalList(PlantEvalView, PlantListView):
    fields = ['plant_eval_then', 'active']
    
    def get_context_data(self, **kwargs):
        context = super(PlantEvalList, self).get_context_data(**kwargs)
        context['object_list'] = self.model.objects.filter(plant_eval_if=self.request.session.get('parent_id'))
        return context


class PlantEvalCreate(PlantEvalView, PlantCreateView):

    def get_initial(self):
        context = super(PlantEvalCreate, self).get_initial()
        context['plant_eval_if'] = self.request.session.get('parent_id')
        return context


class PlantEvalUpdate(PlantEvalView, PlantUpdateView):
    pass


class PlantEvalDelete(PlantEvalView, PlantDeleteView):
    pass


# PlantEvalLog
class PlantEvalLogView(object):
    model = PlantEvalLog
    fields = ['dt', 'plant_eval', 'active']
    success_url = reverse_lazy('plantevallog_list')


class PlantEvalLogList(PlantEvalLogView, PlantListView):
    pass


class PlantEvalLogCreate(PlantEvalLogView, PlantCreateView):
    pass


class PlantEvalLogUpdate(PlantEvalLogView, PlantUpdateView):
    pass


class PlantEvalLogDelete(PlantEvalLogView, PlantDeleteView):
    pass

    
# PlantAlert
class PlantAlertView(object):
    model = PlantAlert
    fields = ['dt', 'note', 'url', 'state', 'active']
    success_url = reverse_lazy('plantalert_list')


class PlantAlertList(PlantAlertView, PlantListView):
    pass


class PlantAlertCreate(PlantAlertView, PlantCreateView):
    pass


class PlantAlertUpdate(PlantAlertView, PlantUpdateView):
    pass


class PlantAlertDelete(PlantAlertView, PlantDeleteView):
    pass


def PlantAlertSimple(request):
    body = ''
    alerts = PlantAlert.objects.filter(active=True)[:10]
    for alert in alerts:
        color = 'black'
        icon = ''
        if alert.state == 'N':
            color = 'green'
            icon = 'fa-check-circle'
        elif alert.state == 'W':
            color = 'orange'
            icon = 'fa-exclamation-circle'
        elif alert.state == 'S':
            color = 'red'
            icon = 'fa-times-circle'
        body += '''
        <li>
            <a href="#" onclick="notif_go(%s,'%s')">
                <div style="color:%s;">
                    <i class="fa %s fa-fw"></i> %s
                    <span class="pull-right text-muted small">%s</span>
                </div>
            </a>
        </li>
        <li class="divider"></li>
        ''' % (alert.id, alert.url, color, icon, alert.note, strftime(alert.dt, '%d/%b/%y %H:%M'))
    foot = '''
    <li>
        <a class="text-center" href="%s">
            <strong>Lihat Semua Berita</strong>
            <i class="fa fa-angle-right"></i>
        </a>
    </li>
    ''' % (reverse_lazy('plantalert_list'))
    return HttpResponse('%s%s' % (body, foot), content_type='text/plain')


def PlantAlertCount(request):
    alerts = PlantAlert.objects.filter(active=True).count()
    return HttpResponse('%s' % (alerts), content_type='text/plain')


def PlantAlertDe(request, pk=False):
    if pk:
        alert = PlantAlert.objects.get(pk=pk)
        alert.active = False
        alert.save()
    return HttpResponse('%s' % (1), content_type='text/plain')
