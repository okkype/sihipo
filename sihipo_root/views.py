from sihipo_root.models import *

from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.db.models import Q
from django.http.response import HttpResponse

# START BASIC VIEW MOD
def get_plant_context(obj, context):
    context['name'] = obj.model._meta.model_name
    context['verbose_name'] = obj.model._meta.verbose_name
    context['referer'] = obj.request.META.get('HTTP_REFERER')
    return context

class PlantListView(ListView):
    paginate_by = 10
    
    def get_paginate_by(self, queryset):
        if self.request.GET.get('filter'):
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
        context['table_fields'] = self.fields
        context['filter'] = self.request.GET.get('filter')
        if context['filter']:
            self.paginate_by = False
            eval_obj = []
            for table_field in context['table_fields']:
                if self.model._meta.get_field(table_field).get_internal_type() in [u'CharField', u'TextField']:
                    eval_obj.append('Q(%s__icontains=context[\'filter\'])' % (table_field))
            if eval_obj:
                context['object_list'] = eval('self.model.objects.filter(%s)' % ('|'.join(eval_obj)))
        context['table_fields'] = self.fields
        context['table_headers'] = {}
        for table_field in context['table_fields']:
            context['table_headers'][table_field] = self.model._meta.get_field(table_field).verbose_name
        return context

class PlantCreateView(CreateView):
    def get_context_data(self, **kwargs):
        context = get_plant_context(self, super(PlantCreateView, self).get_context_data(**kwargs))
        return context

class PlantUpdateView(UpdateView):
    def get_context_data(self, **kwargs):
        context = get_plant_context(self, super(PlantUpdateView, self).get_context_data(**kwargs))
        return context

class PlantDeleteView(DeleteView):
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
            }
        ]
        self.request.session['parent_id'] = context['object'].id
        return context

class PlantSensorDelete(PlantSensorView, PlantDeleteView):
    pass

# PlantSensorDetail
class PlantSensorDetailView(object):
    model = PlantSensorDetail
    fields = ['plant_sensor', 'kode', 'active']
    success_url = reverse_lazy('plantsensordetail_list')

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
                'name':'Detail Sensor',
                'link':reverse_lazy('plantcontroldetail_list')
            }
        ]
        self.request.session['parent_id'] = context['object'].id
        return context

class PlantControlDelete(PlantControlView, PlantDeleteView):
    pass

# PlantControlDetail
class PlantControlDetailView(object):
    model = PlantControlDetail
    fields = ['plant_control', 'kode', 'val', 'active']
    success_url = reverse_lazy('plantcontroldetail_list')

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
    fields = ['dt', 'plant_sensor', 'plant_rack', 'state']
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
    fields = ['plant_sensor_log', 'kode', 'val']
    success_url = reverse_lazy('plantsensorlogdetail_list')

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
    pass

class PlantSensorLogDetailDelete(PlantSensorLogDetailView, PlantDeleteView):
    pass
    
# PlantControlLog
class PlantControlLogView(object):
    model = PlantControlLog
    fields = ['dt', 'plant_control', 'plant_rack', 'state']
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
    fields = ['plant_control_log', 'kode', 'val']
    success_url = reverse_lazy('plantcontrollogdetail_list')

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
    pass

class PlantControlLogDetailDelete(PlantControlLogDetailView, PlantDeleteView):
    pass

# PlantEvalIf
class PlantEvalIfView(object):
    model = PlantEvalIf
    fields = ['kode', 'eval_if', 'active']
    success_url = reverse_lazy('plantevalif_list')

class PlantEvalIfList(PlantEvalIfView, PlantListView):
    pass

class PlantEvalIfCreate(PlantEvalIfView, PlantCreateView):
    pass

class PlantEvalIfUpdate(PlantEvalIfView, PlantUpdateView):
    pass

class PlantEvalIfDelete(PlantEvalIfView, PlantDeleteView):
    pass

# PlantEvalThen
class PlantEvalThenView(object):
    model = PlantEvalThen
    fields = ['kode', 'eval_then', 'active']
    success_url = reverse_lazy('plantevalthen_list')

class PlantEvalThenList(PlantEvalThenView, PlantListView):
    pass

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

class PlantEvalList(PlantEvalView, PlantListView):
    pass

class PlantEvalCreate(PlantEvalView, PlantCreateView):
    pass

class PlantEvalUpdate(PlantEvalView, PlantUpdateView):
    pass

class PlantEvalDelete(PlantEvalView, PlantDeleteView):
    pass

# PlantEvalLog
class PlantEvalLogView(object):
    model = PlantEvalLog
    fields = ['dt', 'plant_eval']
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
    fields = ['dt', 'note', 'state', 'active']
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
    body = '''
    <li>
        <a href="#">
            <div style="color:green;">
                <i class="fa fa-check-circle fa-fw"></i> New Comment
                <span class="pull-right text-muted small">4 minutes ago</span>
            </div>
        </a>
    </li>
    <li class="divider"></li>
    <li>
        <a href="#">
            <div style="color:yellow;">
                <i class="fa fa-exclamation-circle fa-fw"></i> New Comment
                <span class="pull-right text-muted small">4 minutes ago</span>
            </div>
        </a>
    </li>
    <li class="divider"></li>
    <li>
        <a href="#">
            <div style="color:red;">
                <i class="fa fa-times-circle fa-fw"></i> New Comment
                <span class="pull-right text-muted small">4 minutes ago</span>
            </div>
        </a>
    </li>
    <li class="divider"></li>
    '''
    foot = '''
    <li>
        <a class="text-center" href="%s">
            <strong>Lihat Semua Berita</strong>
            <i class="fa fa-angle-right"></i>
        </a>
    </li>
    ''' % (reverse_lazy('plantalert_list'))
    return HttpResponse('%s%s' % (body, foot))
