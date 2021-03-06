from django.urls import path
from django.contrib.auth import urls
from django.conf.urls import include

from django.views.generic.base import RedirectView

from . import views

# both for the link names and the view names, try to stick to this:

# projects -> list
# if the singular version already has an 's' at the end, use:
# thesis_list -> list

# project -> project view
# project_form -> add new/edit existing project

app_name = 'core'
# site_url = 'https://metabolismofcities.org'
site_url = ''
archive_url = 'https://archive.metabolismofcities.org'

urlpatterns = [

    # Redirecting old URLs
    path('curso', RedirectView.as_view(url='https://forms.gle/GZRHD7tY53EjcFY28', permanent=True)),
    path('curso/', RedirectView.as_view(url='https://forms.gle/GZRHD7tY53EjcFY28', permanent=True)),
    path('page/about', RedirectView.as_view(url=site_url+'/about/our-story', permanent=True)),
    path('page/team', RedirectView.as_view(url=site_url+'/about/team', permanent=True)),
    path('page/wishlist', RedirectView.as_view(url=site_url+'/about/mission', permanent=True)),
    path('page/wishlist', RedirectView.as_view(url=site_url+'/about/mission', permanent=True)),
    path('page/contact', RedirectView.as_view(url=site_url+'/contact', permanent=True)),
    path('page/version', RedirectView.as_view(url=site_url+'/about/version-history', permanent=True)),
    path('page/mailinglist', RedirectView.as_view(url=site_url+'/about/subscribe', permanent=True)),
    path('news', RedirectView.as_view(url=site_url+'/community/news', permanent=True)),
    path('blog', RedirectView.as_view(url=site_url+'/community/blog', permanent=True)),
    path('research/list', RedirectView.as_view(url=site_url+'/community/research/projects', permanent=True)),
    path('research/add', RedirectView.as_view(url=site_url+'/community/research/create', permanent=True)),
    path('people', RedirectView.as_view(url=site_url+'/community/people', permanent=True)),
    path('news/<int:year>/<int:month>', RedirectView.as_view(url=site_url+'/community/news', permanent=True)),
    path('vancouver/', RedirectView.as_view(url=site_url+'/community/news/214', permanent=False)),
    path('vancouver', RedirectView.as_view(url=site_url+'/community/news/214', permanent=False)),
    path('cities/page/datasets', RedirectView.as_view(url=site_url+'/cities/datasets/', permanent=True)),

    path('videos', RedirectView.as_view(url=site_url+'/resources/videos', permanent=True)),
    path('mooc', RedirectView.as_view(url=site_url+'/resources/mooc', permanent=True)),
    path('journals', RedirectView.as_view(url=site_url+'/resources/journals', permanent=True)),

    path('publications', RedirectView.as_view(url=site_url+'/resources/publications', permanent=True)),
    path('publications/collections', RedirectView.as_view(url=site_url+'/resources/publications', permanent=True)),
    path('publications/add', RedirectView.as_view(url=site_url+'/resources/publications/add', permanent=True)),
    path('publications/search', RedirectView.as_view(url=site_url+'/resources/publications', permanent=True)),
    path('page/map', RedirectView.as_view(url=site_url+'/resources/publications', permanent=True)),
    path('publications/all', RedirectView.as_view(url=site_url+'/resources/publications', permanent=True)),
    path('collections/<int:id>', RedirectView.as_view(url=site_url+'/resources/publications', permanent=True)),
    path('tags/<int:id>/<slug:slug>', RedirectView.as_view(url=site_url+'/resources/publications/tags/%(id)s', permanent=True)),
    path('people/<int:id>-<slug:slug>', RedirectView.as_view(url=site_url+'/community/people/%(id)s', permanent=True)),
    path('publication/<int:id>', RedirectView.as_view(url=site_url+'/resources/publications/%(id)s', permanent=True)),
    path('source/<int:id>', RedirectView.as_view(url=site_url+'/resources/journals/%(id)s', permanent=True)),

    path('blog/<int:id>-<slug:slug>', RedirectView.as_view(url=site_url+'/community/blog/%(id)s', permanent=True)),

    path('data/', RedirectView.as_view(url=site_url+'/resources/data/datasets', permanent=True)),
    path('data', RedirectView.as_view(url=site_url+'/resources/data/datasets', permanent=True)),
    path('data/add', RedirectView.as_view(url=site_url+'/about/join', permanent=True)),

    path('omat', RedirectView.as_view(url=site_url+'/resources/omat', permanent=True)),
    path('omat/<slug:slug>', RedirectView.as_view(url=archive_url+'/omat/%(slug)s', permanent=False)),
    path('page/casestudies', RedirectView.as_view(url=archive_url+'/page/casestudies', permanent=False)),
    path('page/casestudies/<slug:slug>', RedirectView.as_view(url=archive_url+'/page/casestudies/%(slug)s', permanent=False)),
    path('casestudy/<slug:slug>', RedirectView.as_view(url=archive_url+'/casestudy/%(slug)s', permanent=False)),
    path('data/areas/<slug:slug>', RedirectView.as_view(url=archive_url+'/data/areas/%(slug)s', permanent=False)),
    path('data/subareas/<slug:slug>', RedirectView.as_view(url=archive_url+'/data/subareas/%(slug)s', permanent=False)),
    path('stakeholders', RedirectView.as_view(url=archive_url+'/stakeholders', permanent=False)),
    path('stakeholders/<slug:slug>', RedirectView.as_view(url=archive_url+'/stakeholders/%(slug)s', permanent=False)),
    path('datavisualization', RedirectView.as_view(url=site_url+'/resources/datavisualisations/', permanent=True)),
    path('datavisualization/examples', RedirectView.as_view(url=site_url+'/resources/datavisualisations/', permanent=True)),
    path('datavisualizations/<int:id>-<slug:slug>', RedirectView.as_view(url=site_url+'/resources/datavisualisations/%(id)s', permanent=True)),

    # Fixing URLs
    path('resources/starters-kit', RedirectView.as_view(url=site_url+'/resources/starter-kit', permanent=True)),

    # Pending:
    path('research/<int:id>', RedirectView.as_view(url=site_url+'/community/research/projects', query_string=True, permanent=True)),
    path('news/<int:id>-<slug:slug>', RedirectView.as_view(url=site_url+'/community/news', permanent=True)),

    path('', views.index, name='homepage'),
    path('home', views.home, name='home'),
    path('search', views.search, name='search'),
    path('more', views.empty, name='more'),

    path('glossary/', views.glossary, name='glossary'),

    path('resources/videos', views.videos, name='videos'),
    path('resources/videos/collections/<int:collection>', views.videos, name='videocollection'),
    path('resources/videos/<int:id>', views.video, name='video'),
    path('resources/videos/all', views.videos, { 'all': True }, name='videos_all'),

    path('resources/datavisualisations/', views.datavisualizations, name='datavisualizations'),
    path('resources/datavisualisations/<int:id>/', views.datavisualization, name='datavisualization'),

    path('community/news', views.articles, {'parent': 'news'}, name='news'),
    path('community/news/<int:id>', views.article, name='news'),
    path('community/blog', views.articles, {'parent': 'blog'}, name='blog'),
    path('community/blog/<int:id>', views.article, name='blog'),
    path('community/events', views.articles, {'parent': 'events'}, name='events'),
    path('community/events/<int:id>', views.article, name='event'),

    path('methodologies', views.methodologies, name='methodologies'),
    path('methods', views.methods, name='methods'),
    path('resources/material-accounting-methods', views.methods, name='methods'),

    path('about', views.section_home, {'slug': 'about'}, name='about'),
    path('community', views.section_home, {'slug': 'community'}, name='community_home'),
    path('resources', views.section_home, {'slug': 'resources'}, name='resources_home'),
    path('resources/', views.section_home, {'slug': 'resources'}, name='resources_home'),

    path('news_events', views.news_and_events, name='news_and_events'),
    path('page/<slug:slug>', views.page, name='page'),
    path('cities', views.sectionpage, { 'id': 33}, name='citieshomepage'),
    path('cities/page/<slug:slug>', views.sectionpage, name='sectionpage'),
    path('about/team', views.team, name='team'),
    path('about/moi-team', views.team, name='moi-team'),
    path('about/task-forces', views.taskforces, name='taskforces'),
    path('about/task-forces/<slug:slug>', views.taskforce, name='taskforce'),
    path('about/task-forces/<slug:taskforce>/join', views.register, name='jointaskforce'),

    path('community/people', views.people, name='people'),
    path('community/people/<int:id>', views.peopledetails, name='peopledetails'),
    path('community/user/<int:id>', views.userdetails, name='userdetails'),

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

    path('register', views.register),
    path('contributor', views.register, {'contributor': True}),
    path('signup/contributor', views.register, {'contributor': True}, name='contributor'),
    path('signup/teammember', views.register, name='contributor'),

    path('notfound', views.notfound),

    path('about/<slug:slug>', views.page, name='about'),
    path('community/<slug:slug>', views.page, name='community'),
    path('resources/data/<slug:slug>', views.page, name='data'),
    path('resources/tools/<slug:slug>', views.page, name='tools'),
    path('services/support/<slug:slug>', views.page, name='support'),
    path('services/research/<slug:slug>', views.page, name='research'),
    path('services/stakeholders-engagement/<slug:slug>', views.page, name='engagement'),
    path('services/support/<slug:slug>', views.page, name='support'),
    path('contact', views.contact, name='contact'),
    path('subscribe', views.page, { 'slug': 'subscribe'}, name='subscribe'),
    path('contact/form', views.contact),
    path('about/subscribe/form/', views.subscribe),
    path('literature', views.literature, name='literature'),
    path('publishers', views.publishers, name='publishers'),
    path('publishers/<int:id>', views.publisher, name='publisher'),
    path('resources/podcasts', views.references, {'type': 24}),
    path('resources/reports', views.references, {'type': 27}),
    path('resources/presentations', views.references, {'type': 25}),
    path('resources/publications', views.references, name='references'),
    path('resources/publications/casestudies', views.case_studies, name='case_studies'),
    path('resources/publication/<int:id>', views.reference),
    path('resources/publications/<int:id>', views.reference, name='reference'),
    path('resources/publications/<int:id>/edit', views.referenceform, name='editreference'),
    path('resources/publications/<int:id>/edit/authors', views.referenceform_authors, name='editreference_authors'),
    path('resources/publications/<int:id>/edit/authors/<int:delete>/delete', views.referenceform_authors, name='editreference_authors_delete'),
    path('resources/publications/<int:id>/edit/tags', views.referenceform_tags, name='editreference_tags'),
    path('resources/publications/<int:id>/edit/multiplicity', views.referenceform_multiplicity, name='editreference_multiplicity'),
    path('resources/publications/add', views.referenceform, name='newreference'),
    path('resources/publications/create/<int:dataset>', views.referenceform, name='newflowreference'),
    path('resources/publications/tags/all', views.references, {"all": True }, name='tag_all'),
    path('resources/publications/tags/<int:tag>', views.references, name='tag_search'),
    path('resources/publications/<slug:slug>', views.page, name='publications'),
    path('resources/<slug:slug>', views.page, name='resources'),
    path('resources/publications/search/ajax', views.reference_search_ajax, name='reference_search_ajax'),
    path('resources/publications/list/ajax', views.reference_list_ajax, name='reference_list_ajax'),
    path('tags/ajax', views.tag_ajax, name='tag_ajax'),
    path('tags/ajax/folder', views.tag_ajax_folder, name='tag_ajax_folder'),

    path('theme/<slug:theme>', views.set_theme, name='set_theme'),
    path('<slug:slug>', views.section_home, name='section_home'),

    path('admin/people', views.admin_people_list, name='admin_people_list'),
    path('admin/members', views.admin_member_list, name='admin_member_list'),
    path('admin/members/<int:id>', views.admin_member_profile, name='admin_member_profile'),
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
    path('admin/tags', views.admin_tag_list, name='admin_tag_list'),
    path('admin/tags/create', views.admin_tag, name='admin_tag'),
    path('admin/tags/<int:id>', views.admin_tag, name='admin_tag'),
    path('admin/tags/<int:parent>/child', views.admin_tag, name='admin_tag'),
    path('admin/methods', views.admin_method_list, name='admin_method_list'),
    path('admin/methods/create', views.admin_method, name='admin_method'),
    path('admin/methods/<int:id>', views.admin_method, name='admin_method'),
    path('admin/publications/<int:id>', views.referenceform, name='admin_reference'),
    path('admin/publications', views.admin_references, name='admin_references'),
    path('admin/publications/time-period-review/', views.pending_time_period, name='pending_time_period'),

    path('admin/organizations', views.admin_organization_list, name='admin_organization_list'),
    path('admin/organizations/<int:id>', views.admin_organization, name='admin_organization'),
    path('admin/organizations/create', views.admin_organization, name='admin_organization'),
    path('admin/organizations/create/<slug:slug>', views.admin_organization, name='admin_organization_referencespace'),

    path('cityloops/projects/', views.cityloops_projects),
    path('temp/import/', views.temp_import_projects),
    path('temp/ref/', views.temp_import_references),
    path('zotero/import/', views.zotero_import),
    path('zotero/csv/', views.zotero_csv),

]
