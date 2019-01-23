from django.urls import path
from django.contrib.auth import urls
from django.conf.urls import include

from . import views

# both for the link names and the view names, try to stick to this:

# projects -> list
# if the singular version already has an 's' at the end, use:
# thesis_list -> list

# project -> project view
# project_form -> add new/edit existing project

app_name = 'core'

urlpatterns = [
    path('', views.index, name='homepage'),
    path('home', views.home, name='home'),
    path('search', views.search, name='search'),
    path('more', views.empty, name='more'),
    path('resources/videos', views.videos, name='videos'),
    path('resources/videos/<int:id>', views.video, name='video'),

    path('community/news', views.articles, {'parent': 'news'}, name='news'),
    path('community/news/<int:id>', views.article, name='news'),
    path('community/blog', views.articles, {'parent': 60}, name='blog'),
    path('community/blog/<int:id>', views.article, name='blog'),
    path('community/events', views.articles, {'parent': 'events'}, name='events'),
    path('community/events/<int:id>', views.article, name='event'),

    path('news_events', views.news_and_events, name='news_and_events'),
    path('page/<slug:slug>', views.page, name='page'),
    path('cities', views.sectionpage, { 'id': 33}, name='sectionpage'),
    path('cities/page/<slug:slug>', views.sectionpage, name='sectionpage'),
    path('about', views.team, name='about'),
    path('about/team', views.team, name='team'),
    path('about/task-forces', views.taskforces, name='taskforces'),
    path('about/task-forces/<slug:slug>', views.taskforce, name='taskforce'),

    path('community/people', views.people, name='people'),
    path('community/people/<int:id>', views.peopledetails, name='peopledetails'),
    path('community/user/<int:id>', views.peopledetails, name='userdetails'),

    #path('community/research', views.projects, {'type': 'research', 'status': 'ongoing', 'page': 50}, name='research_projects'),
    #path('community/research/<int:id>', views.project_view, {'type': 'research', 'status': 'ongoing'}, name='research_project'),
    #path('community/research/past', views.projects, {'type': 'research', 'status': 'finished', 'page': 51}, name='past_research_projects'),
    #path('community/research/past/<int:id>', views.project_view, {'type': 'research', 'status': 'finished'}, name='past_research_project'),
    #path('community/projects', views.projects, {'type': 'projects', 'status': 'ongoing', 'page': 57}, name='projects'),
    #path('community/projects/<int:id>', views.project_view, {'type': 'projects', 'status': 'ongoing'}, name='project'),
    #path('community/projects/past', views.projects, {'type': 'projects', 'status': 'finished', 'page': 56}, name='past_projects'),
    #path('community/projects/past/<int:id>', views.project_view, {'type': 'projects', 'status': 'finished'}, name='past_project'),
    
    path('resources/journals', views.journals, name='journals'),
    path('resources/journals/<int:id>', views.journal, name='journal'),

    path('community/organizations/<int:id>', views.organization, name='organization'),
    path('community/organizations/<slug:type>', views.organizations, name='organizations'),

    path('community/research/create', views.project_form, name='project_form'),
    path('community/research/<slug:type>', views.projects, name='projects'),
    path('community/research/<slug:type>/<int:id>', views.project, name='project'),

    path('resources', views.journals, name='resources_home'),
    path('community', views.empty, name='community_home'),
    path('register', views.register),

    path('<slug:slug>', views.section_home, name='section_home'),

    path('about/<slug:slug>', views.page, name='about'),
    path('community/<slug:slug>', views.page, name='community'),
    path('resources/data/<slug:slug>', views.page, name='data'),
    path('resources/tools/<slug:slug>', views.page, name='tools'),
    path('services/support/<slug:slug>', views.page, name='support'),
    path('services/research/<slug:slug>', views.page, name='research'),
    path('services/stakeholders-engagement/<slug:slug>', views.page, name='engagement'),
    path('services/support/<slug:slug>', views.page, name='support'),
    path('contact', views.contact, name='contact'),
    path('literature', views.literature, name='literature'),
    path('publishers', views.publishers, name='publishers'),
    path('publishers/<int:id>', views.publisher, name='publisher'),
    path('resources/podcasts', views.references, {'type': 24}),
    path('resources/reports', views.references, {'type': 27}),
    path('resources/presentations', views.references, {'type': 25}),
    path('resources/publications', views.references, name='references'),
    path('resources/publication/<int:id>', views.reference),
    path('resources/publications/<int:id>', views.reference, name='reference'),
    path('resources/publications/<int:id>/edit', views.referenceform, name='editreference'),
    path('resources/publications/<int:id>/<str:export_method>', views.export_reference, name = 'export_reference'),
    path('resources/publications/add', views.referenceform, name='newreference'),
    path('resources/publications/create/<int:dataset>', views.referenceform, name='newflowreference'),
    path('resources/publications/tags/<int:tag>', views.references, name='tag_search'),
    path('resources/publications/<slug:slug>', views.page, name='publications'),
    path('resources/<slug:slug>', views.page, name='resources'),
    path('resources/publications/search/ajax', views.reference_search_ajax, name='reference_search_ajax'),
    path('tags/ajax', views.tag_ajax, name='tag_ajax'),

    path('admin/people', views.admin_people_list, name='admin_people_list'),
    path('admin/members', views.admin_member_list, name='admin_member_list'),
    path('admin/people/create', views.admin_people, name='admin_people_create'),
    path('admin/people/<int:id>', views.admin_people, name='admin_people'),
    path('admin/videos', views.admin_video_list, name='admin_video_list'),
    path('admin/videos/create', views.admin_video, name='admin_video_create'),
    path('admin/videos/<int:id>', views.admin_video, name='admin_video'),
    path('admin/videocollections', views.admin_videocollections, name='admin_videocollections'),
    path('admin/videocollections/create', views.admin_videocollection, name='admin_videocollection_create'),
    path('admin/videocollections/<int:id>', views.admin_videocollection, name='admin_videocollection'),
    path('admin/articles/<int:id>', views.admin_article, name='admin_article'),
    path('admin/events/create', views.admin_article, {'type': 'event'}, name='admin_article'),
    path('admin/articles/create/parent=<int:parent>', views.admin_article, name='admin_article_parent'),
    path('admin/project/create', views.admin_project, name='admin_project_create'),
    path('admin/project/<int:id>', views.admin_project, name='admin_project'),
    path('admin/projects', views.admin_project_list, name='admin_project_list'),
    path('admin/projects/<slug:status>', views.admin_project_list, name='admin_project_list'),
    path('admin/tags', views.admin_tag_list, name='admin_tag_list'),
    path('admin/tags/create', views.admin_tag, name='admin_tag'),
    path('admin/tags/<int:id>', views.admin_tag, name='admin_tag'),
    path('admin/tags/<int:parent>/child', views.admin_tag, name='admin_tag'),
    path('admin/publications/<int:id>', views.referenceform, name='admin_reference'),
    path('admin/publications/<int:id>/tags', views.admin_referencetags, name='admin_referencetags'),
    path('admin/publications', views.admin_references, name='admin_references'),

    path('admin/organizations', views.admin_organization_list, name='admin_organization_list'),
    path('admin/organizations/<int:id>', views.admin_organization, name='admin_organization'),
    path('admin/organizations/create', views.admin_organization, name='admin_organization'),
    path('admin/organizations/create/<slug:slug>', views.admin_organization, name='admin_organization_referencespace'),

#temp
    path('updateorgs', views.updateorgs),
]
