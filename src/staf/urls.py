from django.urls import path

from . import views

app_name = 'staf'
urlpatterns = [
    path('', views.index, name='index'),
    path('search', views.search, name='search'),
    path('search/ajax', views.searchajax, name='searchajax'),

    path('processgroups', views.processgroups, name='processgroups'),
    path('processgroups/<int:id>', views.processgroup, name='processgroup'),

    path('materials', views.materiallist, name='materials'),
    path('materials/<int:id>', views.materiallist, name='materiallist'),
    path('materials/<int:id>/edit', views.materialform, name='material_edit'),
    path('materials/<int:id>/child', views.materialchild, name='material_child'),
    path('materials/create', views.materialform, name='material_create'),
    path('materials/ajax', views.materiallistajax, name='materialajax'),

    path('processes', views.processlist, name='processes'),
    path('processes/table', views.processtable, name='processtable'),
    path('processes/<int:id>', views.processlist, name='processlist'),
    path('processes/<int:id>/edit', views.processform, name='process_edit'),
    path('processes/<int:id>/child', views.processchild, name='process_child'),
    path('processes/create', views.processform, name='process_create'),
    path('processes/ajax', views.processlistajax, name='processajax'),

    path('processbrowser', views.processlisting, name='processlisting'),
    path('processbrowser/tree', views.processtree, name='processbrowsertree'),
    path('processbrowser/<int:id>', views.processlisting, name='processlisting'),

    path('units', views.units, name='units'),
    path('units/<int:id>', views.unit, name='unit'),

]
