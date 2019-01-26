from django.contrib.sites.models import Site
from core.models import Event
from multiplicity.models import ProcessGroup
from datetime import datetime, timedelta, time
from django.conf import settings

def site(request):
    site = Site.objects.get_current()
    today = datetime.now().date()
    event = Event.objects.filter(article__site=site, start__gte=today).order_by('start').first()
    processgroups = ProcessGroup.objects.order_by('name').exclude(pk__in=[13,14,12])

    return {'SITE_ID': site.id, 'SITE_URL': site.domain, 'SITE_NAME': site.name, 'EVENT': event, 'PROCESSGROUPS': processgroups, 'MAPBOX_API_KEY': "pk.eyJ1IjoibWV0YWJvbGlzbW9mY2l0aWVzIiwiYSI6ImNqcHA5YXh6aTAxcmY0Mm8yMGF3MGZjdGcifQ.lVZaiSy76Om31uXLP3hw-Q", 'DEBUG': settings.DEBUG}
