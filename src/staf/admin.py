from django.contrib import admin

# Register your models here.
from .models import *

class ChoiceAdmin(admin.ModelAdmin):
    autocomplete_fields = ['references']

class ProcessAdmin(admin.ModelAdmin):
    search_fields = ['name']

admin.site.register(Dataset, ChoiceAdmin)
admin.site.register(ProcessType)
admin.site.register(Process, ProcessAdmin)
admin.site.register(Material)
admin.site.register(MaterialCatalog)
admin.site.register(Unit)
admin.site.register(TimePeriod)
