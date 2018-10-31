from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Dataset)
admin.site.register(ProcessType)
admin.site.register(Process)
admin.site.register(Material)
admin.site.register(MaterialCatalog)
admin.site.register(Unit)
admin.site.register(TimePeriod)
