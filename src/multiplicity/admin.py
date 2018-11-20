from django.contrib import admin
from .models import Topic, DatasetType, ReferenceSpace, ReferenceSpaceType, ReferenceSpaceLocation, ReferenceSpaceFeature, Feature, ReferenceSpaceTypeDescription, DQIRating, DQI, Information, ReferenceSpaceCSV, GraphType, DatasetTypeStructure

class ReferenceSpaceTypeAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}

class ReferenceSpaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'type')

admin.site.register(DatasetType)
admin.site.register(Topic)
admin.site.register(DQIRating)
admin.site.register(DQI)
admin.site.register(ReferenceSpace, ReferenceSpaceAdmin)
admin.site.register(ReferenceSpaceLocation)
admin.site.register(ReferenceSpaceType, ReferenceSpaceTypeAdmin)
admin.site.register(Feature)
admin.site.register(Information)
admin.site.register(ReferenceSpaceFeature)
admin.site.register(ReferenceSpaceTypeDescription)
admin.site.register(ReferenceSpaceCSV)
admin.site.register(GraphType)
admin.site.register(DatasetTypeStructure)
