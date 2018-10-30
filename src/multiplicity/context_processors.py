from django.contrib.sites.models import Site

def site(request):
    site = Site.objects.get_current()
    return {'SITE_ID': site.id, 'SITE_URL': site.domain, 'SITE_NAME': site.name}
