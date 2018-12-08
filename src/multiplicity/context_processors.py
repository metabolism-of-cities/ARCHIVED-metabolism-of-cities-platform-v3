from django.contrib.sites.models import Site
from core.models import Event
from multiplicity.models import ProcessGroup
from datetime import datetime, timedelta, time

def site(request):
    site = Site.objects.get_current()
    today = datetime.now().date()
    event = Event.objects.filter(article__site=site, start__gte=today).order_by('start').first()
    processgroups = ProcessGroup.objects.order_by('name').exclude(pk__in=[13,14,12])

    return {'SITE_ID': site.id, 'SITE_URL': site.domain, 'SITE_NAME': site.name, 'EVENT': event, 'PROCESSGROUPS': processgroups}
