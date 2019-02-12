from django.contrib import admin

# Register your models here.
from .models import *

class ArticleAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ('title', 'site', 'parent')
    search_fields = ('title',)

class PeopleAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'lastname', 'city', 'email')

admin.site.register(Journal)
admin.site.register(Publisher)
admin.site.register(Organization)
admin.site.register(Video)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Color)
admin.site.register(Tag)
admin.site.register(UserAction)
admin.site.register(UserLog)
admin.site.register(People, PeopleAdmin)
admin.site.register(Timeline)
admin.site.register(Project)
admin.site.register(ReferenceType)
admin.site.register(Reference)
