from django.contrib.sites.models import Site
from core.models import Event
from datetime import datetime, timedelta, time

def site(request):
    site = Site.objects.get_current()
    today = datetime.now().date()
    event = Event.objects.filter(article__site=site, start__gte=today).order_by('start').first()

    return {'SITE_ID': site.id, 'SITE_URL': site.domain, 'SITE_NAME': site.name, 'EVENT': event}
