from django.urls import path

from . import views

app_name = 'multiplicity'
urlpatterns = [

    # Admin
    path('admin/locations', views.admin_locations, name='admin_locations'),
    path('admin/locations/<int:id>', views.admin_location, name='admin_location'),
    path('admin/locations/create', views.admin_location, name='admin_location_create'),

    path('admin/referencespaces/<slug:type>', views.admin_referencespaces, name='admin_referencespaces'),
    path('admin/referencespaces/<slug:type>/<int:id>', views.admin_referencespace, name='admin_referencespace'),
    path('admin/referencespaces/<slug:type>/<int:referencespace>/location', views.admin_location, name='admin_referencespace_location'),
    path('admin/referencespaces/<slug:type>/create', views.admin_referencespace, name='admin_referencespace_create'),

    path('admin/<slug:city>/overview', views.admin_data_overview, name='admin_data_overview'),

    path('admin/datasettype', views.admin_datasettypes, name='admin_datasettypes'),
    path('admin/datasettype/<int:id>', views.admin_datasettype, name='admin_datasettype'),
    path('admin/datasettype/create', views.admin_datasettype, name='admin_datasettype'),

    path('admin/referencephotos', views.admin_referencephoto, name='admin_referencephotos'),
    path('admin/referencephotos/<int:id>', views.admin_referencephoto, name='admin_referencephoto'),
    path('admin/referencephotos/create', views.admin_referencephoto, name='admin_referencephoto'),

    # General
    path('table/datasets/<int:dataset>', views.datatable, name='datatable_dataset'),

    path('', views.index, name='index'),
    path('<slug:city>/research', views.research, name='research'),

    #path('<slug:city>/material-stocks/<slug:type>', views.flow, name='stock'),

    path('<slug:city>/material-flows/<slug:topic>', views.datasets_overview, name='flows'),
    path('<slug:city>/material-stocks/<slug:topic>', views.datasets_overview, {'type': 'stocks' }, name='stocks'),
    path('<slug:city>/energy-flows/<slug:topic>', views.datasets_overview, {'type': 'energy'}, name='energy_flows'),

    #path('<slug:city>/material-flows/<slug:slug>', views.overview, name='overview_flows'),
    #path('<slug:city>/material-flows/<slug:slug>/<slug:type>', views.flow, name='flow'),
    #path('<slug:city>/material-stocks', views.overview, {'slug': 'material-stocks' }, name='overview_stocks'),

    path('<slug:city>/profile/<slug:topic>', views.topic, name='topic'),
    #path('<slug:city>/<slug:topic>', views.topic, name='topic'),

    path('<slug:city>/maps', views.map, name='map'),
    path('<slug:city>/maps/<slug:type>', views.map, name='map'),
    path('<slug:city>/maps/boundaries/<int:id>', views.map, name='map'),
    path('<slug:city>/maps/boundaries/<int:id>/download', views.download_location, name='download_location'),
    path('<slug:city>/datasets', views.datasets, name='datasets'),
    path('<slug:city>/resources/photos', views.photos, name='photos'),
    path('<slug:city>/resources/<slug:slug>', views.resources, name='resources'),
    path('<slug:city>/datasets/<int:id>', views.dataset, name='dataset'),
    path('<slug:city>/datasets/<int:id>/delete', views.delete_dataset, name='delete_dataset'),
    path('<slug:city>/datasets/<int:dataset>/graph/<int:id>', views.graph, name='graph'),
    path('<slug:city>/datasets/<int:id>/<slug:slug>', views.dataset, name='dataset_slice'),
    path('<slug:city>/information', views.information_form, name='information_form'),
    path('<slug:city>/information/topic/<int:topic>', views.information_form, name='information_form_topic'),
    path('<slug:city>/information/<int:id>', views.information_form, name='information_form'),
    path('<slug:city>/photo', views.photo_form, name='photo_form'),
    path('<slug:city>/photo/<int:id>', views.photo_form, name='photo_form'),
    path('<slug:city>/sectors/<slug:sector>', views.sector, name='sector'),

    # Uploading data
    path('<slug:city>/upload', views.upload, name='upload'),

    # Uploading infrastructure data
    path('<slug:city>/upload/infrastructure', views.upload_infrastructure, name='upload_infrastructure'),
    path('<slug:city>/upload/infrastructure/<slug:type>', views.upload_infrastructure_file, name='upload_infrastructure_file'),
    path('<slug:city>/upload/infrastructure/<slug:type>/<int:id>', views.upload_infrastructure_review, name='upload_infrastructure_review'),
    path('<slug:city>/upload/infrastructure/<slug:type>/<int:id>/meta', views.upload_infrastructure_meta, name='upload_infrastructure_meta'),

    # Uploading flows/stocks data
    path('<slug:city>/upload/flow', views.upload_flow, name='upload_flow'),
    path('<slug:city>/upload/flow/<int:id>', views.upload_flow_file, name='upload_flow_file'),
    path('<slug:city>/upload/flow/<int:type>/<int:id>', views.upload_flow_review, name='upload_flow_review'),
    path('<slug:city>/upload/flow/<int:type>/<int:id>/meta', views.upload_flow_meta, name='upload_flow_meta'),
    path('<slug:city>/upload/stock', views.upload_flow, {'type': 'stocks'}, name='upload_stock'),

    # Uploading geospatial data
    path('<slug:city>/upload/systemboundaries', views.upload_systemboundaries, name='upload_systemboundaries'),
    path('<slug:city>/upload/systemboundaries/create', views.upload_systemboundary, name='upload_systemboundary'),
    path('<slug:city>/upload/systemboundaries/<int:location>', views.upload_systemboundary, name='upload_systemboundary'),

    path('<slug:city>/upload/mtu', views.upload_mtu, name='upload_mtu'),
    path('<slug:city>/upload/mtu/review', views.upload_mtu_review, name='upload_mtu_review'),

    path('<slug:city>/infrastructure/<slug:type>/<slug:space>', views.space, name='space'),
    path('<slug:city>/infrastructure/<slug:type>', views.space_list, name='space_list'),
    path('<slug:city>/infrastructure/<slug:topic>', views.infrastructure_list, name='infrastructure_list'),
    path('<slug:city>/infrastructure', views.infrastructure_list, name='infrastructure_list'),
    path('<slug:city>/<slug:main>/<slug:topic>', views.topic, name='subtopic'),
    path('<slug:city>/<slug:main>/<slug:topic>/input', views.topic, {'tab': 'input'}, name='subtopic_input'),
    path('<slug:city>/<slug:main>/<slug:topic>/use', views.topic, {'tab': 'use' }, name='subtopic_use'),
    path('<slug:city>/<slug:main>/<slug:topic>/output', views.topic, {'tab': 'output'}, name='subtopic_output'),
    #path('<slug:city>/<slug:theme>/<slug:topic>/<slug:type>', views.space_list, name='space_list'),

    # This view is used to show the content of a slide, when recording a video
    path('<slug:city>/slide', views.temp_slide, name='temp_slide'),

    path('materials', views.materials, name='materials'),
    path('<slug:slug>', views.detail, name='city'),
    path('profile', views.detail, name='profile'),

]
