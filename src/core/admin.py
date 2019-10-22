from django.contrib import admin

# Register your models here.
from .models import *

class ArticleAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ['title', 'site', 'parent']
    search_fields = ['title',]

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

class ProjectAdmin(admin.ModelAdmin):
    search_fields = ['name']

admin.site.register(Journal)
admin.site.register(Publisher)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Video)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Color)
admin.site.register(Tag)
admin.site.register(MethodClassification)
admin.site.register(MethodScale)
admin.site.register(UserAction)
admin.site.register(UserLog)
admin.site.register(People, PeopleAdmin)
admin.site.register(Timeline)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectOrganization, ProjectOrgAdmin)
admin.site.register(ReferenceType)
admin.site.register(DataViz, DataVizAdmin)
admin.site.register(ReferenceOrganization, ReferenceOrgAdmin)
admin.site.register(Reference, ReferenceAdmin)
