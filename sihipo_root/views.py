from sihipo_root.models import *

from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.db.models import Q

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
                if self.model._meta.get_field(table_field).get_internal_type() == u'CharField':
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
