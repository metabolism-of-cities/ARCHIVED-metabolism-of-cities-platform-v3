from django.contrib import admin

# Register your models here.

from .models import Topic, Category, Message, TaskForceMember, Project, Service, TaskForceUnit

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}

class SlugAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}

admin.site.register(Topic)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Message)
admin.site.register(TaskForceMember)
admin.site.register(TaskForceUnit)
admin.site.register(Project)
admin.site.register(Service, SlugAdmin)
