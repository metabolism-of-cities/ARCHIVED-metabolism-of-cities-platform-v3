from django.contrib import admin
from .models import Topic, DatasetType, ReferenceSpace, ReferenceSpaceType, ReferenceSpaceLocation, ReferenceSpaceFeature, Feature, ReferenceSpaceTypeDescription, DQIRating, DQI, Information, ReferenceSpaceCSV, GraphType, DatasetTypeStructure, Photo, ProcessGroup, License

class ReferenceSpaceTypeAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}

class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'position', 'deleted')

class ReferenceSpaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'type')
    search_fields = ['name']

class ReferenceSpaceFeatureAdmin(admin.ModelAdmin):
    list_display = ('space', 'feature', 'value')
    search_fields = ['space__name', 'feature__name']

class FeatureAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'unit')
    search_fields = ['name']

class DatasetTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'origin_process', 'destination_process', 'type', 'active']
    list_filter = ['active', 'category', 'type']
    list_editable = ['active', 'origin_process', 'destination_process']

admin.site.register(DatasetType, DatasetTypeAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(DQIRating)
admin.site.register(DQI)
admin.site.register(ReferenceSpace, ReferenceSpaceAdmin)
admin.site.register(ReferenceSpaceLocation)
admin.site.register(ReferenceSpaceType, ReferenceSpaceTypeAdmin)
admin.site.register(Feature, FeatureAdmin)
admin.site.register(Information)
admin.site.register(ReferenceSpaceFeature, ReferenceSpaceFeatureAdmin)
admin.site.register(ReferenceSpaceTypeDescription)
admin.site.register(ReferenceSpaceCSV)
admin.site.register(GraphType)
admin.site.register(DatasetTypeStructure)
admin.site.register(Photo)
admin.site.register(ProcessGroup)
admin.site.register(License)
