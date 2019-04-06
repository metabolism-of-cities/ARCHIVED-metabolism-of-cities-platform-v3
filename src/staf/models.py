from django.db import models
from multiplicity.models import ReferenceSpaceLocation, ReferenceSpace, DQIRating, Topic, GraphType
from core.models import Reference
from django.forms import ModelForm
from django.contrib.postgres.fields import ArrayField

from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
User = get_user_model()

# Meta datasets, catalogs, not containing actual data

class ProcessType(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

class Process(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    code = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    description = models.TextField(null=True, blank=True)
    slug = models.SlugField(db_index=True, max_length=255, null=True, blank=True)
    type = models.ForeignKey(ProcessType, on_delete=models.CASCADE, null=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    is_separator = models.BooleanField()
    def __str__(self):
        if self.code:
            return self.code + " - " + self.name
        else:
            return self.name

    class Meta:
        ordering = ["id"]

class ProcessForm(ModelForm):
    class Meta:
        model = Process
        exclude = ['id']

class ProcessTree(models.Model):
    root = models.ForeignKey(Process, related_name='+', on_delete=models.CASCADE)
    node = models.OneToOneField(Process, related_name='tree_process', primary_key=True, on_delete=models.CASCADE)
    ancestors = ArrayField(base_field=models.IntegerField())

    class Meta:
        managed = False

class MaterialCatalog(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

class Material(models.Model):
    name = models.TextField(db_index=True)
    code = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    catalog = models.ForeignKey(MaterialCatalog, on_delete=models.CASCADE, blank=True, null=True)
    is_separator = models.BooleanField()
    description = models.TextField(null=True, blank=True)
    def __str__(self):
        return self.code + " - " + self.name

class MaterialForm(ModelForm):
    class Meta:
        model = Material
        exclude = ['id', 'parent']

# See also https://schinckel.net/2016/01/23/adjacency-lists-in-django-with-postgres/
class MaterialTree(models.Model):
    root = models.ForeignKey(Material, related_name='+', on_delete=models.CASCADE)
    node = models.OneToOneField(Material, related_name='tree_material', primary_key=True, on_delete=models.CASCADE)
    ancestors = ArrayField(base_field=models.IntegerField())

    class Meta:
        managed = False

class Unit(models.Model):
    symbol = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    notes = models.TextField(null=True, blank=True)
    def __str__(self):
        return self.name

class TimePeriod(models.Model):
    start = models.DateField(db_index=True)
    end = models.DateField(db_index=True, null=True, blank=True)
    name = models.CharField(max_length=255, db_index=True)

    def __str__(self):
        return self.name

# All these classes relate to specific datasets and data

class Dataset(models.Model):
    name = models.CharField(max_length=255)
    primary_space = models.ForeignKey(ReferenceSpace, on_delete=models.CASCADE)
    references = models.ManyToManyField(Reference)
    reliability = models.ForeignKey(DQIRating, on_delete=models.CASCADE, blank=True, null=True, related_name='reliability')
    completeness = models.ForeignKey(DQIRating, on_delete=models.CASCADE, blank=True, null=True, related_name='completeness')
    geographical_correlation = models.ForeignKey(DQIRating, on_delete=models.CASCADE, blank=True, null=True, related_name='geographical_correlation')
    access = models.ForeignKey(DQIRating, on_delete=models.CASCADE, blank=True, null=True, related_name='access')
    notes = models.TextField(blank=True, null=True)
    replication = models.TextField(blank=True, null=True)
    type = models.ForeignKey('multiplicity.DatasetType', on_delete=models.CASCADE, null=True, blank=True)
    graph = models.ForeignKey('multiplicity.GraphType', on_delete=models.CASCADE, null=True, blank=True)
    topics = models.ManyToManyField(Topic, blank=True)
    process = models.ForeignKey(Process, on_delete=models.CASCADE, null=True, blank=True, limit_choices_to={'slug__isnull': False})
    deleted = models.BooleanField(default=False, db_index=True)
    def __str__(self):
        return self.name

    def timeframe(self):
        from django.db.models import Max
        from django.db.models import Min
        return Data.objects.filter(dataset=self.id).aggregate(start=Min('timeframe__start'), end=Max('timeframe__end'))
    
    def materials(self):
        return Data.objects.filter(dataset=self.id).values('material_name').order_by('material_name').distinct()

class DatasetForm(ModelForm):
    class Meta:
        model = Dataset
        fields = ['name']
        labels = {
            'name': 'Dataset name'
        }

class CSV(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255)
    original_name = models.CharField(max_length=255)
    imported = models.BooleanField()
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, null=True, blank=True)
    datasettype = models.ForeignKey('multiplicity.DatasetType', on_delete=models.CASCADE, null=True, blank=True)
    space = models.ForeignKey(ReferenceSpace, on_delete=models.CASCADE, null=True, blank=True, related_name='csv_import')
    active = models.BooleanField(default=True, db_index=True)

class Data(models.Model):
    quantity = models.FloatField(null=True, blank=True)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, null=True, blank=True)
    material = models.ForeignKey(Material, on_delete=models.CASCADE, null=True, blank=True)
    material_name = models.CharField(max_length=500, null=True, blank=True)
    subset = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='data')
    origin_space = models.ForeignKey(ReferenceSpace, on_delete=models.CASCADE, null=True, blank=True, related_name='origin_space')
    destination_space = models.ForeignKey(ReferenceSpace, on_delete=models.CASCADE, null=True, blank=True, related_name='destination_space')
    timeframe = models.ForeignKey(TimePeriod, on_delete=models.CASCADE)
    origin = models.ForeignKey(Process, on_delete=models.CASCADE, null=True, blank=True, related_name='origin')
    destination = models.ForeignKey(Process, on_delete=models.CASCADE, null=True, blank=True, related_name='destination')
    csv = models.ForeignKey(CSV, on_delete=models.CASCADE, null=True, blank=True)
    comments = models.TextField(null=True, blank=True)

class DataForm(ModelForm):
    class Meta:
        model = Data
        exclude = ['id', 'flow']
