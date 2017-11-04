from sihipo_root.models import *

from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

# START BASIC VIEW MOD
def get_plant_context(obj, context):
    context['name'] = obj.model._meta.model_name
    context['verbose_name'] = obj.model._meta.verbose_name
    context['back_url'] = obj.success_url
    return context

class PlantListView(ListView):
    paginate_by = 10
    
    def get_paginate_by(self, queryset):
        if self.request.GET.get('filter'):
            return 0
        return ListView.get_paginate_by(self, queryset)
        
    def get_context_data(self, **kwargs):
        context = get_plant_context(self, super(PlantListView, self).get_context_data(**kwargs))
        context['filter'] = self.request.GET.get('filter', '')
        if context['filter']:
            context['object_list'] = self.model.objects.filter(kode__icontains=context['filter'])
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
