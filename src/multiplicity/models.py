from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from tinymce import HTMLField
from django.forms import ModelForm

# Used for image resizing
from stdimage.models import StdImageField
import re

User = get_user_model()

class TimestampedModel(models.Model):
    # A timestamp representing when this object was created.
    created_at = models.DateTimeField(auto_now_add=True)

    # A timestamp reprensenting when this object was last updated.
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

        # By default, any model that inherits from `TimestampedModel` should
        # be ordered in reverse-chronological order. We can override this on a
        # per-model basis as needed, but reverse-chronological is a good
        # default ordering for most models.
        ordering = ['-created_at', '-updated_at']

class Topic(models.Model):
    name = models.CharField(max_length=255)
    icon = models.CharField(max_length=255, null=True, blank=True)
    slug = models.SlugField(db_index=True, max_length=255, unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    position = models.PositiveSmallIntegerField()
    description = models.TextField(null=True, blank=True)
    materials = models.ManyToManyField('staf.Material', blank=True)
    deleted = models.BooleanField(default=False, db_index=True)
    def __str__(self):
        return self.name
    class Meta:
        ordering = ["position"]

class ReferenceSpaceType(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(db_index=True, max_length=255, unique=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, null=True, blank=True)
    process = models.ForeignKey('staf.Process', on_delete=models.CASCADE, null=True, blank=True, limit_choices_to={'slug__isnull': False})
    SPACE_TYPE = (
        ('SOC', 'Socio-economic System'),
        ('NAT', 'Natural Environment'),
    )
    type = models.CharField(max_length=3, choices=SPACE_TYPE)
    COLORS = (
        ('blue', 'Blue'),
        ('red', 'Red'),
        ('green', 'Green'),
        ('darkblue', 'Dark Blue'),
        ('purple', 'Purple'),
        ('yellow', 'yellow'),
        ('orange', 'Orange'),
        ('black', 'Black'),
        ('grey', 'Grey'),
        ('pink', 'Pink'),
        ('brightgreen', 'Bright green'),
        ('white', 'White'),
    )
    marker_color = models.CharField(max_length=10, choices=COLORS, null=True, blank=True, default='blue')
    user_accessible = models.BooleanField()
    def __str__(self):
        return self.name

    def features(self):
        return Feature.objects.filter(type=self.id, show_in_table=True)

class DatasetTypeStructure(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(db_index=True, max_length=255)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    icon = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name

class DatasetType(models.Model):
    name = models.CharField(max_length=255)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    origin_process = models.ForeignKey('staf.Process', on_delete=models.CASCADE, null=True, blank=True, related_name='origindataset')
    destination_process = models.ForeignKey('staf.Process', on_delete=models.CASCADE, null=True, blank=True, related_name='destinationdataset')
    standard_material = models.ForeignKey('staf.Material', on_delete=models.CASCADE, null=True, blank=True)
    origin_reference_type = models.ForeignKey(ReferenceSpaceType, on_delete=models.CASCADE, null=True, blank=True, related_name='originreferencetype')
    destination_reference_type = models.ForeignKey(ReferenceSpaceType, on_delete=models.CASCADE, null=True, blank=True, related_name='destinationreferencetype')
    FLOWS = (
        ('destination_only', 'Destination only'),
        ('origin_only', 'Origin only'),
        ('origin_and_destination', 'Origin and destination'),
    )
    flows = models.CharField(max_length=25, choices=FLOWS, default='origin_and_destination')
    TYPES = (
        ('stocks', 'Stocks'),
        ('flows', 'Flows'),
    )
    type = models.CharField(max_length=6, choices=TYPES, default='flows')
    image = models.ImageField(null=True, blank=True, upload_to='datasettype')
    category = models.ForeignKey(DatasetTypeStructure, on_delete=models.CASCADE, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True)
    active = models.BooleanField()

    def __str__(self):
        if self.category:
            return '%s (%s)' % (self.name, self.category.name)
        else:
            return self.name

    class Meta:
        ordering = ["name"]

class DatasetTypeForm(ModelForm):
    class Meta:
        model = DatasetType
        fields = ['name', 'description', 'flows', 'type', 'category', 'topic', 'slug', 'active']


class ReferenceSpace(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    type = models.ForeignKey(ReferenceSpaceType, on_delete=models.CASCADE)
    city = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='city_location')
    country = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='country_location')
    description = models.TextField(null=True, blank=True)
    url = models.CharField(max_length=255, null=True, blank=True)
    slug = models.SlugField(db_index=True, max_length=255, null=True)
    location = models.ForeignKey('multiplicity.ReferenceSpaceLocation', on_delete=models.SET_NULL, null=True, blank=True)
    csv = models.ForeignKey('multiplicity.ReferenceSpaceCSV', on_delete=models.CASCADE, null=True, blank=True)
    tag = models.ForeignKey('core.Tag', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name + " (" + self.type.name + ")"
    def save(self, *args, **kwargs):
        if not self.id:
            # Newly created object, so set slug
            self.slug = slugify(self.name)
        super(ReferenceSpace, self).save(*args, **kwargs)

    class Meta:
        ordering = ["name"]

class ReferenceSpaceForm(ModelForm):
    class Meta:
        model = ReferenceSpace
        fields = ['name', 'type', 'country']

class ReferenceSpaceLocation(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    space = models.ForeignKey(ReferenceSpace, on_delete=models.CASCADE)
    lat = models.CharField(max_length=20, null=True, blank=True)
    lng = models.CharField(max_length=20, null=True, blank=True)
    area = models.FloatField(null=True, blank=True)
    default_zoom = models.PositiveSmallIntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    timeframe = models.CharField(max_length=255, null=True, blank=True)
    source = models.CharField(max_length=255, null=True, blank=True)
    geojson = models.TextField(null=True, blank=True)
    def __str__(self):
        return self.name or 'Location for ' + self.space.name
    class Meta:
        ordering = ["-timeframe"]

class ReferenceSpaceLocationForm(ModelForm):
    class Meta:
        model = ReferenceSpaceLocation
        exclude = ['id', 'space']

class Feature(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    type = models.ForeignKey(ReferenceSpaceType, on_delete=models.CASCADE)
    unit = models.ForeignKey('staf.Unit', on_delete=models.CASCADE, null=True, blank=True)
    exclusively_for = models.ForeignKey(ReferenceSpace, on_delete=models.CASCADE, null=True, blank=True)
    show_in_table = models.BooleanField(default=False)
    def __str__(self):
        return self.name
    class Meta:
        ordering = ["id"]

class ReferenceSpaceFeature(models.Model):
    space = models.ForeignKey(ReferenceSpace, on_delete=models.CASCADE)
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE)
    value = models.TextField()
    def __str__(self):
        return '%s for %s' % (self.feature, self.space)

class ReferenceSpaceTypeDescription(models.Model):
    type = models.ForeignKey(ReferenceSpaceType, on_delete=models.CASCADE)
    space = models.ForeignKey(ReferenceSpace, on_delete=models.CASCADE)
    description = models.TextField()

class MTU(models.Model):
    type = models.ForeignKey(ReferenceSpaceType, on_delete=models.CASCADE)
    space = models.ForeignKey(ReferenceSpace, on_delete=models.CASCADE)
    timeframe = models.CharField(max_length=255)
    source = models.CharField(max_length=255)
    file = models.CharField(max_length=255)
    description = models.TextField()

class ReferenceSpaceCSV(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.ForeignKey(ReferenceSpaceType, on_delete=models.CASCADE)
    space = models.ForeignKey(ReferenceSpace, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255)
    original_name = models.CharField(max_length=255)
    imported = models.BooleanField()
    how_obtained = models.TextField(null=True, blank=True)
    gaps = models.TextField(null=True, blank=True)
    source = models.CharField(max_length=255, null=True, blank=True)

class DQI(models.Model):
    name = models.CharField(max_length=40)
    def __str__(self):
        return self.name

class DQIRating(models.Model):
    indicator = models.ForeignKey(DQI, on_delete=models.CASCADE, null=True, blank=True)
    score = models.PositiveSmallIntegerField()
    description = models.CharField(max_length=255)
    def __str__(self):
        return "Rating " + str(self.score) + " - " + self.indicator.name
    class Meta:
        ordering = ["score"]

class ProcessGroup(models.Model):
    name = models.CharField(max_length=255)
    icon = models.CharField(max_length=255, null=True, blank=True)
    slug = models.SlugField(db_index=True, max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    processes = models.ManyToManyField('staf.Process', blank=True)

    def __str__(self):
        return self.name

class License(models.Model):
    name = models.CharField(max_length=255)
    url = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return self.name

class Photo(TimestampedModel):
    image = StdImageField(upload_to='photos', variations={'thumbnail': (200, 150), 'large': (1024, 780), 'medium': (640, 480)})
    author = models.CharField(max_length=255)
    source_url = models.CharField(max_length=255, null=True, blank=True)
    process = models.ForeignKey('staf.Process', on_delete=models.CASCADE, null=True, blank=True, limit_choices_to={'slug__isnull': False})
    description = models.TextField(null=True, blank=True)
    primary_space = models.ForeignKey(ReferenceSpace, on_delete=models.CASCADE, related_name='photo_gallery') # This is the main system this photo belongs to
    secondary_space = models.ForeignKey(ReferenceSpace, on_delete=models.CASCADE, related_name='photos', null=True, blank=True) # A specific space (e.g. Airport or Factory) this photo belongs to
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False, db_index=True)
    license = models.ForeignKey(License, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        if self.description:
          cleanr = re.compile('<.*?>')
          description = re.sub(cleanr, '', self.description)
          description = description[:30] + " - " + self.author + " - #" + str(self.id)
        else:
          description = "Photo by " + self.author + " - #" + str(self.id)
        return description

class PhotoForm(ModelForm):
    class Meta:
        model = Photo
        exclude = ['id', 'uploaded_by', 'primary_space', 'process']
        labels = {
            'deleted': 'Do not show in the gallery',
            'secondary_space': 'Reference space (optional)'
        }

class ReferencePhoto(models.Model):
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE)
    type = models.ForeignKey(ReferenceSpaceType, on_delete=models.CASCADE)
    space = models.ForeignKey(ReferenceSpace, on_delete=models.CASCADE)
    def __str__(self):
        description = "Photo for " + self.type + " in " + self.space

class ReferencePhotoForm(ModelForm):
    class Meta:
        model = ReferencePhoto
        exclude = ['id']

class Information(TimestampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = HTMLField('Content')
    space = models.ForeignKey(ReferenceSpace, on_delete=models.CASCADE)
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, null=True, blank=True)
    position = models.IntegerField(null=True, blank=True)
    references = models.ManyToManyField("core.Reference", blank=True)
    dataset_types = models.ManyToManyField(DatasetType, blank=True, limit_choices_to={'active': True})
    process = models.ForeignKey("staf.Process", on_delete=models.CASCADE, blank=True, null=True, limit_choices_to={'slug__isnull': False})
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title

class InformationForm(ModelForm):
    class Meta:
        model = Information
        fields = ['title', 'content', 'photo', 'position']

class GraphType(models.Model):
    title = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    url = models.CharField(max_length=255, null=True, blank=True)
    notes = HTMLField('Content', null=True, blank=True)
    TIMEFRAMES = (
        ('single', 'Single timeframe'),
        ('multiple', 'Multiple timeframes'),
        ('both', 'Does not matter'),
    )
    timeframes = models.CharField(max_length=25, choices=TIMEFRAMES, default='both')
    MATERIALS = (
        ('single', 'Single material'),
        ('multiple', 'Multiple materials'),
        ('both', 'Does not matter'),
    )
    materials = models.CharField(max_length=25, choices=MATERIALS, default='both')

    def __str__(self):
        return self.title

