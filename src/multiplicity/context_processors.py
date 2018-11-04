from django.contrib.sites.models import Site
from core.models import Event

def site(request):
    site = Site.objects.get_current()
    event = Event.objects.filter(article__site=site, start__lte='2006-01-01')[:1]

    return {'SITE_ID': site.id, 'SITE_URL': site.domain, 'SITE_NAME': site.name, 'EVENT': event}
