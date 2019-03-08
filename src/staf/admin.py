from django.contrib import admin

# Register your models here.
from .models import *

class ChoiceAdmin(admin.ModelAdmin):
    autocomplete_fields = ['references']

admin.site.register(Dataset, ChoiceAdmin)
admin.site.register(ProcessType)
admin.site.register(Process)
admin.site.register(Material)
admin.site.register(MaterialCatalog)
admin.site.register(Unit)
admin.site.register(TimePeriod)
