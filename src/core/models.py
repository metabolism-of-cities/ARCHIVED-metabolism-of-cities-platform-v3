from django.db import models
from multiplicity.models import ReferenceSpace, License
from django.forms import ModelForm
from django.template.defaultfilters import slugify
from tinymce import HTMLField
from django.contrib.auth.models import User

from django.contrib.auth import get_user_model
User = get_user_model()

from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from django.conf import settings

# Used for image resizing
from stdimage.models import StdImageField
import re

from django.urls import reverse

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

class ReferenceType(models.Model):
    name = models.CharField(max_length=255)
    icon = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name
    class Meta:
        ordering = ["name"]

class Organization(models.Model):
    name = models.CharField(max_length=255)
    url = models.CharField(max_length=255, null=True, blank=True)
    twitter = models.CharField(max_length=255, null=True, blank=True)
    linkedin = models.CharField(max_length=255, null=True, blank=True)
    researchgate = models.CharField(max_length=255, null=True, blank=True)
    logo = models.ImageField(null=True, blank=True, upload_to='organizations')
    processes = models.ManyToManyField('staf.Process', blank=True, limit_choices_to={'slug__isnull': False})
    reference_spaces = models.ManyToManyField(ReferenceSpace, blank=True)
    description = HTMLField(null=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    ORG_TYPE = (
        ('academic', 'Research Institution'),
        ('universities', 'Universities'),
        ('city_government', 'City Government'),
        ('regional_government', 'Regional Government'),
        ('national_government', 'National Government'),
        ('statistical_agency', 'Statistical Agency'),
        ('private_sector', 'Private Sector'),
        ('publisher', 'Publishers'),
        ('ngo', 'NGO'),
        ('other', 'Other'),
    )
    type = models.CharField(max_length=20, choices=ORG_TYPE)

    def __str__(self):
        return self.name
    class Meta:
        ordering = ["name"]

class OrganizationForm(ModelForm):
    class Meta:
        model = Organization
        exclude = ['id', 'processes']

class Publisher(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    class Meta:
        ordering = ["name"]

class Journal(models.Model):
    name = models.CharField(max_length=255)
    website = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(null=True, blank=True, upload_to='journals')

    def __str__(self):
        return self.name
    class Meta:
        ordering = ["name"]

class People(models.Model):
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    affiliation = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    email_public = models.BooleanField()
    city = models.ForeignKey(ReferenceSpace, on_delete=models.SET_NULL, null=True, blank=True, related_name='people_city', limit_choices_to={'type': 3})
    country = models.ForeignKey(ReferenceSpace, on_delete=models.SET_NULL, null=True, blank=True, related_name='people_country', limit_choices_to={'type': 2})
    profile = models.TextField(null=True, blank=True)
    research_interests = models.TextField(null=True, blank=True)
    website = models.CharField(max_length=255, null=True, blank=True)
    twitter = models.CharField(max_length=255, null=True, blank=True)
    google_scholar = models.CharField(max_length=255, null=True, blank=True)
    orcid = models.CharField(max_length=255, null=True, blank=True)
    researchgate = models.CharField(max_length=255, null=True, blank=True)
    linkedin = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    member_since = models.DateField(null=True, blank=True, db_index=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(null=True, blank=True, upload_to='people', help_text="Square photos are best - please resize to 350x350 pixels")
    PEOPLE_STATUS = (
        ('active', 'Active'),
        ('retired', 'Retired'),
        ('deceased', 'Deceased'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending Review'),
    )
    status = models.CharField(max_length=8, choices=PEOPLE_STATUS, default='active')
    site = models.ForeignKey(Site, on_delete=models.CASCADE, default=settings.SITE_ID)
    organizations = models.ManyToManyField(Organization, blank=True)
    objects = models.Manager()
    on_site = CurrentSiteManager()

    def __str__(self):
        return '%s %s' % (self.firstname, self.lastname)

    class Meta:
        ordering = ["firstname", "lastname"]

class PeopleForm(ModelForm):
    class Meta:
        model = People
        exclude = ['id']

class PeopleNote(models.Model):
    people = models.ForeignKey(People, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    note = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    class Meta:
        ordering = ["date"]

class Article(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(db_index=True, max_length=255, null=True, blank=True)
    introduction = models.TextField(null=True, blank=True)
    head = models.TextField(null=True, blank=True)
    includes_form = models.BooleanField(default=False)
    content = HTMLField('Content')
    image = models.ImageField(null=True, blank=True, upload_to='articles')

    parent = models.ForeignKey(
        'core.Article', on_delete=models.CASCADE, related_name='sectionparent', null=True, blank=True
    )
    authors = models.ManyToManyField(People, blank=True)
    active = models.BooleanField(default=True)
    SECTIONS = (
        ('about', 'About'),
        ('community', 'Community'),
        ('research', 'Research'),
        ('resources', 'Resources'),
        ('cities', 'Cities'),
        ('whatwedo', 'What We Do'),
        ('newsevents', 'News and Events'),
    )
    section = models.CharField(max_length=20, choices=SECTIONS, default='about')
    site = models.ForeignKey(Site, on_delete=models.CASCADE, default=settings.SITE_ID)
    objects = models.Manager()
    on_site = CurrentSiteManager()
    date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["title"]

class ArticleForm(ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'introduction', 'content', 'image', 'active']

class SimpleArticleForm(ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'image', 'date', 'head', 'includes_form', 'slug', 'active','content']

class Event(models.Model):
    article = models.OneToOneField(
        Article,
        on_delete=models.CASCADE,
        related_name='event',
        primary_key=True,
    )
    EVENT_TYPE = (
        ('conference', 'Conference'),
        ('hackathon', 'Hackathon'),
        ('workshop', 'Workshop'),
        ('seminar', 'Seminar'),
        ('other', 'Other'),
    )
    start = models.DateField(null=True, blank=True)
    end = models.DateField(null=True, blank=True)
    type = models.CharField(max_length=20, choices=EVENT_TYPE)
    estimated_date = models.CharField(max_length=60, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    url = models.CharField(max_length=255, null=True, blank=True)
    def __str__(self):
        return self.article.title

class EventForm(ModelForm):
    class Meta:
        model = Event
        exclude = ['article']

class VideoCollection(models.Model):
    title = models.CharField(max_length=255)
    description = HTMLField('description', null=True, blank=True)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, default=settings.SITE_ID)
    position = models.PositiveSmallIntegerField(default=1)
    objects = models.Manager()
    on_site = CurrentSiteManager()
    show_in_list = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["position"]

class VideoCollectionForm(ModelForm):
    class Meta:
        model = VideoCollection
        exclude = ['id', 'site']


class Video(models.Model):
    title = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    description = models.TextField()
    author = models.CharField(max_length=255)
    date = models.DateField(null=True)
    people = models.ManyToManyField(People, blank=True)
    VIDEOSITES = (
        ('youtube', 'YouTube'),
        ('vimeo', 'Vimeo'),
        ('wikimedia', 'Wikimedia Commons'),
        ('other', 'Other website'),
    )

    website = models.CharField(max_length=20, choices=VIDEOSITES)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, default=settings.SITE_ID)
    objects = models.Manager()
    on_site = CurrentSiteManager()
    primary_space = models.ForeignKey(ReferenceSpace, on_delete=models.CASCADE, null=True, blank=True)
    collections = models.ManyToManyField(VideoCollection, blank=True)
    thumbnail = models.ImageField(null=True, blank=True, upload_to='video_thumbnails')
    license = models.ForeignKey(License, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title


class VideoForm(ModelForm):
    class Meta:
        model = Video
        exclude = ['id', 'site']
        labels = {
            'primary_space': 'Reference space (optional)'
        }

class VideoUploadForm(ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'website', 'url', 'primary_space', 'description', 'author', 'date', 'thumbnail', 'license']
        labels = {
            'primary_space': 'Reference space',
            'url': 'Video URL'
        }
        
class Tag(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    parent_tag = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
        limit_choices_to={'hidden': False}, related_name='children'
    )
    hidden = models.BooleanField(db_index=True, default=False)
    gps = models.CharField(max_length=255, null=True, blank=True)
    PARENTS = (
 	(1,	'Publication Types'),
 	(2,	'Metabolism Studies'),
 	(3,	'Countries'),
 	(4,	'Cities'),
 	(5,	'Scales'),
 	(6,	'Flows'),
 	(7,	'Time Horizon'),
 	(9,	'Methodologies'),
 	(10,	'Other'),
    )
    parent = models.CharField(max_length=2, choices=PARENTS, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]

class TagForm(ModelForm):
    class Meta:
        model = Tag
        exclude = ['id', 'gps', 'parent', 'hidden']

class Reference(models.Model):
    title = models.CharField(max_length=255)
    LANGUAGES = (
        ('EN', 'English'),
        ('ES', 'Spanish'),
        ('CH', 'Chinese'),
        ('FR', 'French'),
        ('GE', 'German'),
        ('NL', 'Dutch'),
        ('OT', 'Other'),
    )
    language = models.CharField(max_length=2, choices=LANGUAGES)
    title_original_language = models.CharField(max_length=255, blank=True, null=True)
    authorlist = models.TextField()
    type = models.ForeignKey(ReferenceType, on_delete=models.CASCADE)
    journal = models.ForeignKey(Journal, on_delete=models.CASCADE, null=True, blank=True, help_text="If the journal does not appear in the list, please leave empty and add the name in the comments")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True)
    year = models.PositiveSmallIntegerField()
    abstract = models.TextField(null=True, blank=True)
    abstract_original_language = models.TextField(null=True, blank=True)
    date_added = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    file = models.FileField(null=True, blank=True, upload_to='references')
    open_access = models.NullBooleanField(null=True, blank=True)
    url = models.CharField(max_length=255, null=True, blank=True)
    doi = models.CharField(max_length=255, null=True, blank=True)
    isbn = models.CharField(max_length=255, null=True, blank=True)
    comments = models.TextField(null=True, blank=True)
    STATUS = (
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('deleted', 'Deleted'),
    )
    status = models.CharField(max_length=8, choices=STATUS, db_index=True)
    authors = models.ManyToManyField(People, through='ReferenceAuthors')
    organizations = models.ManyToManyField(Organization, through='ReferenceOrganization')
    tags = models.ManyToManyField(Tag, blank=True, limit_choices_to={'hidden': False})
    processes = models.ManyToManyField('staf.Process', blank=True, limit_choices_to={'slug__isnull': False})
    materials = models.ManyToManyField('staf.Material', blank=True)
    spaces = models.ManyToManyField(ReferenceSpace, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-year", "title"]

    def source(self):
        "Return details of where this reference was published at/in"
        if self.journal:
            return self.journal.name
        elif self.event:
            return self.event.name
        else:
            return self.type.name

class ReferenceAuthors(models.Model):
    reference = models.ForeignKey(Reference, on_delete=models.CASCADE)
    people = models.ForeignKey(People, on_delete=models.CASCADE)
    class Meta:
        db_table = 'core_reference_authors'

class ReferenceForm(ModelForm):
    class Meta:
        model = Reference
        fields = ['language', 'title', 'title_original_language', 'authorlist', 'type', 'journal', 'year', 'abstract', 'abstract_original_language', 'open_access', 'doi', 'isbn', 'url', 'comments']
        labels = {
            'authorlist': 'Author(s)',
            'doi': 'DOI',
            'isbn': 'ISBN',
            'url': 'URL',
        }

class ReferenceFormAdmin(ModelForm):
    class Meta:
        model = Reference
        exclude = ['id', 'organizations', 'processes', 'date_added', 'event', 'authors', 'spaces', 'tags', 'materials']
        labels = {
            'authorlist': 'Author(s)',
            'doi': 'DOI',
            'isbn': 'ISBN',
            'url': 'URL',
        }

class ReferenceOrganization(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    reference = models.ForeignKey(Reference, on_delete=models.CASCADE)
    TYPES = (
        ('publisher', 'Publisher'),
        ('commissioner', 'Commissioner'),
        ('organization', 'Organization'),
    )
    type = models.CharField(max_length=20, choices=TYPES)
    def __str__(self):
        return self.organization.name + " - " + self.type + " - " + self.reference.title

class UserAction(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

class UserLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='log')
    space = models.ForeignKey('multiplicity.ReferenceSpace', on_delete=models.CASCADE, null=True, blank=True)
    reference = models.ForeignKey(Reference, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    action = models.ForeignKey(UserAction, on_delete=models.CASCADE)
    points = models.PositiveSmallIntegerField()
    model = models.CharField(max_length=255, null=True, blank=True)
    model_id = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    class Meta:
        ordering = ["-date"]

class Color(models.Model):
    name = models.CharField(max_length=20)
    css = models.CharField(max_length=20)
    def __str__(self):
        return self.name

class Project(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    institution = models.CharField(max_length=255, null=True, blank=True)
    organizations = models.ManyToManyField(Organization, through='ProjectOrganization', blank=True)
    researcher = models.CharField(max_length=255, null=True, blank=True)
    supervisor = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    description = HTMLField('description', null=True, blank=True)
    target_finish_date = models.CharField(max_length=255, null=True, blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    STATUS = (
        ('planned', 'Planned'),
        ('ongoing', 'In progress'),
        ('finished', 'Finished'),
        ('cancelled', 'Cancelled'),
    )
    status = models.CharField(max_length=20, choices=STATUS, default='ongoing')
    active = models.BooleanField(default=True)
    pending_review = models.BooleanField(default=True)
    TYPE = (
        ('theses', 'Theses'),
        ('projects', 'Projects'),
        ('applied', 'Applied research'),
    )
    type = models.CharField(max_length=20, choices=TYPE)
    THESISTYPE = (
        ('bachelor', 'Bachelor'),
        ('masters', 'Master'),
        ('phd', 'PhD'),
        ('other', 'Other'),
    )
    thesistype = models.CharField(max_length=20, choices=THESISTYPE, null=True, blank=True)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    objects = models.Manager()
    on_site = CurrentSiteManager()
    url = models.CharField(max_length=255, null=True, blank=True)
    references = models.ManyToManyField(Reference, blank=True, limit_choices_to={'status': 'active'})

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("core:project", args=[self.type, self.id])

    class Meta:
        ordering = ['name']

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        exclude = ['id', 'site',  'references']
        labels = {
            'name': 'Project title',
            'thesistype': 'Thesis type',
            'researcher': 'Researcher(s)',
            'supervisor': 'Supervisor(s) / Project leader(s)',
            'url': 'URL',
        }

class ProjectUserForm(ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'researcher', 'type', 'thesistype', 'institution', 'supervisor', 'email', 'description', 'target_finish_date', 'start_date', 'end_date', 'status', 'url']
        labels = {
            'name': 'Project title',
            'thesistype': 'Thesis type',
            'researcher': 'Researcher(s)',
            'supervisor': 'Supervisor(s) / Project leader(s)',
            'url': 'URL',
        }

class ProjectOrganization(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    TYPES = (
        ('funder', 'Funder'),
        ('commissioner', 'Commissioner'),
        ('organization', 'Organization'),
    )
    type = models.CharField(max_length=20, choices=TYPES)
    def __str__(self):
        return self.organization.name + " - " + self.type + " - " + self.project.name


class Timeline(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    link = models.CharField(max_length=255, null=True, blank=True)
    date = models.DateField()
    def __str__(self):
        return self.title

class DataViz(models.Model):
    title = models.CharField(max_length=255)
    image = StdImageField(upload_to='dataviz', variations={'thumb': (300, 300), 'large': (1024, 1024)})
    uploaded_by = models.ForeignKey(People, on_delete=models.CASCADE)
    space = models.ForeignKey('multiplicity.ReferenceSpace', on_delete=models.CASCADE, null=True, blank=True)
    reference = models.ForeignKey(Reference, on_delete=models.CASCADE, null=True, blank=True)
    process_group = models.ForeignKey('multiplicity.ProcessGroup', on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    description = HTMLField(null=True, blank=True)
    url = models.CharField(max_length=255, null=True, blank=True, help_text="URL of the source website/article -- ONLY enter if this is not linked to a publication")
    source = models.TextField(null=True, blank=True, help_text="Name of the source website/article -- ONLY enter if this is not linked to a publication")
    year = models.PositiveSmallIntegerField(null=True, blank=True, help_text="Year of the data being visualized -- ONLY enter if this is not linked to a publication")
    class Meta:
        ordering = ["-date"]
    def __str__(self):
        return self.title


class NewsletterSubscriber(models.Model):
    people = models.ForeignKey(People, on_delete=models.CASCADE)
    datasets = models.BooleanField()
    news = models.BooleanField()
    events = models.BooleanField()
    publications = models.BooleanField()
    dataviz = models.BooleanField()
    multimedia = models.BooleanField()
    projects = models.BooleanField()
    theses = models.BooleanField()
    reference_spaces = models.ManyToManyField(ReferenceSpace, blank=True)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, default=settings.SITE_ID)
