from django.contrib.sites.models import Site
from core.models import Event, Article
from multiplicity.models import ProcessGroup
from datetime import datetime, timedelta, time
from django.conf import settings

def site(request):
    site = Site.objects.get_current()
    today = datetime.now().date()
    event = Event.objects.filter(article__site=site, article__active=True, start__gte=today).order_by('start').first()
    if site.id == 1:
        news = 61
        system = "city"
        systems = "cities"
        multiplicity_name = "Cities"
    else:
        news = 142
        system = "island"
        systems = "islands"
        multiplicity_name = "Data"
    latest_news = Article.objects.filter(parent=news, active=True).order_by('-date')[0]
    processgroups = ProcessGroup.objects.order_by('name').exclude(pk__in=[13,14,12])

    return {
        'SITE_ID': site.id, 
        'SITE_URL': site.domain, 
        'SITE_NAME': site.name, 
        'EVENT': event, 
        'PROCESSGROUPS': processgroups, 
        'MAPBOX_API_KEY': "pk.eyJ1IjoibWV0YWJvbGlzbW9mY2l0aWVzIiwiYSI6ImNqcHA5YXh6aTAxcmY0Mm8yMGF3MGZjdGcifQ.lVZaiSy76Om31uXLP3hw-Q", 
        'DEBUG': settings.DEBUG,
        'CURRENT_PAGE': request.get_full_path(),
        'LATEST_NEWS': latest_news,
        'SYSTEM': system,
        'SYSTEMS': systems,
        'MULTIPLICITY_NAME': multiplicity_name,
    }
