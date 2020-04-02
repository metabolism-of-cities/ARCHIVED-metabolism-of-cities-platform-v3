from django.contrib import admin

# Register your models here.
from .models import *

class ArticleAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ['title', 'site', 'parent']
    search_fields = ['title',]

class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ['people', 'site']

class PeopleAdmin(admin.ModelAdmin):
    list_display = ['firstname', 'lastname', 'city', 'email']
    search_fields = ['firstname', 'lastname']

class ReferenceAdmin(admin.ModelAdmin):
    search_fields = ['title']

class OrganizationAdmin(admin.ModelAdmin):
    autocomplete_fields = ['processes', 'reference_spaces']

class DataVizAdmin(admin.ModelAdmin):
    autocomplete_fields = ['space', 'reference']

class ProjectOrgAdmin(admin.ModelAdmin):
    autocomplete_fields = ['project']
    list_display = ['project', 'organization', 'type']
    search_fields = ['organization__name', 'project__name', 'type']

class ReferenceOrgAdmin(admin.ModelAdmin):
    autocomplete_fields = ['reference']
    list_display = ['reference', 'organization', 'type']
    search_fields = ['organization__name', 'reference__title', 'type']

class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent_tag', 'hidden', 'is_accounting_method']
    search_fields = ['name', 'parent_tag__name']

class MethodAdmin(admin.ModelAdmin):
    list_display = ['tag', 'category', 'method_class', 'status']
    search_fields = ['tag__name']

class ProjectAdmin(admin.ModelAdmin):
    search_fields = ['name']
    autocomplete_fields = ['reference_spaces', 'references']
    list_display = ['name', 'start_date', 'end_date', 'type', 'methodologies', 'cityloops']

admin.site.register(Journal)
admin.site.register(Publisher)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Video)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Color)
admin.site.register(Tag, TagAdmin)
admin.site.register(MethodClassification)
admin.site.register(MaterialGroup)
admin.site.register(Method, MethodAdmin)
admin.site.register(MethodTemporalBoundary)
admin.site.register(MethodData)
admin.site.register(MethodCategory)
admin.site.register(CaseStudy)
admin.site.register(UserAction)
admin.site.register(UserLog)
admin.site.register(People, PeopleAdmin)
admin.site.register(Timeline)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectOrganization, ProjectOrgAdmin)
admin.site.register(ReferenceType)
admin.site.register(NewsletterSubscriber, NewsletterSubscriberAdmin)
admin.site.register(DataViz, DataVizAdmin)
admin.site.register(ReferenceOrganization, ReferenceOrgAdmin)
admin.site.register(Reference, ReferenceAdmin)
