from django.conf.urls import url, include

from . import views


urlpatterns = [
    url(r'^plantplant/$', views.PlantPlantList.as_view(), name='plantplantlist'),
    url(r'^plantplant/create$', views.PlantPlantCreate.as_view(), name='plantplantcreate'),
    url(r'^plantplant/update/(?P<pk>\d+)$', views.PlantPlantUpdate.as_view(), name='plantplantupdate'),
    url(r'^plantplant/delete/(?P<pk>\d+)$', views.PlantPlantDelete.as_view(), name='plantplantdelete'),
    url(r'^plantopt/$', views.PlantOptList.as_view(), name='plantopt_list'),
    url(r'^plantopt/create$', views.PlantOptCreate.as_view(), name='plantopt_create'),
    url(r'^plantopt/update/(?P<pk>\d+)$', views.PlantOptUpdate.as_view(), name='plantopt_update'),
    url(r'^plantopt/delete/(?P<pk>\d+)$', views.PlantOptDelete.as_view(), name='plantopt_delete'),
    url(r'^plantoptdetail/$', views.PlantOptDetailList.as_view(), name='plantoptdetail_list'),
    url(r'^plantoptdetail/create/$', views.PlantOptDetailCreate.as_view(), name='plantoptdetail_create'),
    url(r'^plantoptdetail/update/(?P<pk>\d+)$', views.PlantOptDetailUpdate.as_view(), name='plantoptdetail_update'),
    url(r'^plantoptdetail/delete/(?P<pk>\d+)$', views.PlantOptDetailDelete.as_view(), name='plantoptdetail_delete'),
    url(r'^plantsensor/$', views.PlantSensorList.as_view(), name='plantsensor_list'),
    url(r'^plantsensor/create/$', views.PlantSensorCreate.as_view(), name='plantsensor_create'),
    url(r'^plantsensor/update/(?P<pk>\d+)$', views.PlantSensorUpdate.as_view(), name='plantsensor_update'),
    url(r'^plantsensor/delete/(?P<pk>\d+)$', views.PlantSensorDelete.as_view(), name='plantsensor_delete'),
    url(r'^plantsensordetail/$', views.PlantSensorDetailList.as_view(), name='plantsensordetail_list'),
    url(r'^plantsensordetail/create/$', views.PlantSensorDetailCreate.as_view(), name='plantsensordetail_create'),
    url(r'^plantsensordetail/update/(?P<pk>\d+)$', views.PlantSensorDetailUpdate.as_view(), name='plantsensordetail_update'),
    url(r'^plantsensordetail/delete/(?P<pk>\d+)$', views.PlantSensorDetailDelete.as_view(), name='plantsensordetail_delete'),
]