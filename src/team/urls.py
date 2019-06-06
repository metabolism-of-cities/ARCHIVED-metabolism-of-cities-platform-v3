from django.urls import path
from django.contrib.auth import urls
from django.conf.urls import include

from . import views

app_name = 'team'

urlpatterns = [
    path('', views.index, name='homepage'),
    path('controlpanel', views.controlpanel, name='controlpanel'),
    path('export', views.export, name='export'),
    path('category/<int:id>', views.category),
    path('taskforce/<int:id>', views.taskforce, name='taskforce'),
    path('taskforce/<int:category>/task', views.ticket, name='newticket'),
    path('taskforce/<int:id>/leave', views.leavetaskforce, name='leavetaskforce'),
    path('tickets', views.ticketlist, name='tickets'),
    path('tickets/<int:id>', views.ticketdetails, name='ticket'),
    path('tickets/<int:id>/status/<slug:status>', views.ticketstatus, name='ticketstatus'),
    path('tickets/<int:id>/startdiscussion', views.ticketdiscussion, name='ticketdiscussion'),
    path('tickets/<int:id>/progress', views.ticketprogress, name='ticketprogress'),
    path('tickets/<int:id>/assign_to/<int:person>', views.ticketperson, name='ticketperson'),
    path('tickets/<int:id>/edit', views.ticket, name='editticket'),
    path('category/<int:id>/view', views.opencategory, name='viewcategory'),
    path('category/<int:id>/config', views.categoryconfig, name='categoryconfig'),
    path('category/<int:id>/config/save', views.saveconfig, name='saveconfig'),
    path('category/<int:id>/<int:topic>', views.category),
    path('topic/<int:id>', views.topic),
    path('topic/<int:id>/view', views.opentopic, name='topic'),
    path('topic/<int:id>/subscription/<slug:type>', views.subscribetopic, name='topic_subscribe'),
    path('topic/<int:id>/edit', views.edittopic, name='edittopic'),
    path('topic/create', views.createtopic, name='createtopic'),
    path('topic/<int:id>/message', views.createmessage),
    path('message/<int:id>/delete', views.deletemessage, name='deletemessage'),
    path('register', views.register),
    path('taskforces', views.taskforces, name='taskforces'),
    path('search', views.search, name='search'),
    path('profile', views.profile, name='memberprofile'),
    path('profile/save', views.saveprofile, name='saveprofile'),
    path('reports/tickets', views.ticketreport, name='ticketreport'),
    path('projects', views.projects, name='projects'),
    path('projects/<int:id>', views.project, name='project'),
    path('projects/create', views.project, name='createproject'),
]
