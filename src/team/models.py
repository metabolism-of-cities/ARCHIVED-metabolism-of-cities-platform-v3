from django.db import models

# So that we can set the user as a foreign key
from django.conf import settings

# So that we can set date = today
from datetime import datetime
from django.contrib.auth.models import User

from django.contrib.auth import get_user_model
User = get_user_model()

from core.models import Color

# To get the total of topics in a category
from django.db.models import Count
from django.forms import ModelForm
from tinymce import HTMLField

class Category(models.Model):
    name = models.CharField(max_length=255)
    google_drive = models.CharField(max_length=255, null=True, blank=True)
    icon = models.CharField(max_length=255, null=True, blank=True)
    category_description = models.TextField(null=True, blank=True);
    entry_exam = models.TextField(null=True, blank=True);
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True)
    slug = models.SlugField()
    GROUPS = (
        ('community', 'Community'),
        ('services', 'Services'),
        ('project', 'Project'),
        ('board', 'Administrative board'),
    )
    group = models.CharField(max_length=10, choices=GROUPS, default='community')
    members = models.ManyToManyField(User, through='TaskForceMember')
    def __str__(self):
        return self.name

class ProjectTaskforceForm(ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'google_drive']
        labels = { 'name': 'Internal (short) name' }

class ActiveManager(models.Manager):
    def get_queryset(self):
        return super(ActiveManager, self).get_queryset().filter(active=True)

class Topic(models.Model):
    name = models.CharField(max_length=255)
    categories = models.ManyToManyField(Category, related_name='topics')
    subscriptions = models.ManyToManyField(User, related_name='subscribed_to', through='TopicSubscription')
    last_message = models.ForeignKey('Message', on_delete=models.CASCADE, null=True, related_name='last_message')
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    objects = models.Manager() # The default manager.
    active_objects = ActiveManager() # Only show active topics
    def __str__(self):
        return self.name

    def last_read(self, request):
        read = MessageRead.objects.filter(topic_id=self.id, user_id=request.user.id)

        if read:
            return read[0]
        else:
            return read

class TopicForm(ModelForm):
    class Meta:
        model = Topic
        fields = ['name', 'categories', 'active']

class TopicSubscription(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    NOTIFICATIONS = (
        ('instantly', 'Instant notification'),
        ('daily', 'Daily digest'),
        ('weekly', 'Weekly digest'),
    )
    type = models.CharField(max_length=10, choices=NOTIFICATIONS, default='instantly')

class Message(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
    file = models.FileField(upload_to='uploads/', null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["date"]

class MessageRead(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.PROTECT)
    message = models.ForeignKey(Message, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)

class TaskForceQuerySet(models.QuerySet):
    def leader(self):
        return self.filter(role='leader', end__isnull=True)
    def member(self):
        return self.filter(role='member', end__isnull=True)
    def active(self):
        return self.filter(end__isnull=True).exclude(role='reader')

class TaskForceMember(models.Model):
    taskforce = models.ForeignKey(Category, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    NOTIFICATIONS = (
        ('instantly', 'Instant notification'),
        ('daily', 'Daily digest'),
        ('weekly', 'Weekly digest'),
        ('none', 'No subscription'),
    )
    default_subscription = models.CharField(max_length=10, choices=NOTIFICATIONS, default='instantly')
    ROLES = (
        ('leader', 'Leader'),
        ('member', 'Member'),
        ('reader', 'Reader'),
    )
    role = models.CharField(max_length=10, choices=ROLES, default='member')
    start = models.DateTimeField(auto_now_add=True)
    end = models.DateField(null=True, blank=True)
    notify_of_new_topics = models.BooleanField()
    objects = TaskForceQuerySet.as_manager()
    def __str__(self):
        return '%s (%s)' % (self.user.first_name, self.taskforce.name)

class TaskForceMemberForm(ModelForm):
    class Meta:
        model = TaskForceMember
        fields = ['taskforce', 'default_subscription', 'role', 'notify_of_new_topics']


class Service(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(db_index=True, max_length=255, unique=True)
    description = HTMLField('Description')
    price_range = models.CharField(max_length=255, null=True, blank=True)
    available_members = models.ManyToManyField(User, blank=True)
    possible_partners = HTMLField('Possible partners', blank=True, null=True)
    public = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class Project(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    funders = models.CharField(max_length=255, null=True, blank=True)
    partners = models.CharField(max_length=255, null=True, blank=True)
    our_budget = models.CharField(max_length=255, null=True, blank=True)
    total_budget = models.CharField(max_length=255, null=True, blank=True)
    description = HTMLField('description', null=True, blank=True)
    budget_breakdown = HTMLField('Budget breakdown', null=True, blank=True)
    logos = models.ImageField(null=True, blank=True, upload_to='projectlogos')
    image = models.ImageField(null=True, blank=True, upload_to='projects')
    taskforce = models.ForeignKey(Category, on_delete=models.CASCADE)
    type = models.ForeignKey(Service, on_delete=models.CASCADE,blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    public = models.BooleanField(default=True)
    STATUS = (
        ('deciding', 'Not yet internally approved'),
        ('no_go', 'Internal decision not to proceed'),
        ('drafing', 'Internally approved; proposal is being drafted'),
        ('submitted', 'Submitted; in review'),
        ('declined', 'Declined'),
        ('approved', 'Approved; not yet started'),
        ('work', 'Approved; in progress'),
        ('completed', 'Approved; project completed'),
    )
    status = models.CharField(max_length=20, choices=STATUS, default='not_submitted')

    def __str__(self):
        return self.name

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'funders', 'partners', 'our_budget', 'total_budget', 'description', 'budget_breakdown', 'type', 'start_date', 'end_date', 'public', 'status']
        labels = { 'name': 'Official project name' }

class TaskForceUnit(models.Model):
    taskforce = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name

class TicketQuerySet(models.QuerySet):
    def completed(self):
        return self.filter(status='completed')
    def pending(self):
        return self.exclude(status='completed').exclude(status='removed')

class TaskForceTicket(models.Model):
    taskforce = models.ForeignKey(Category, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, limit_choices_to={'is_staff': True})
    title = models.CharField(max_length=255)
    description = HTMLField('description', null=True, blank=True)
    STATUS = (
        ('unassigned', 'Unassigned'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('shelved', 'Shelved'),
        ('completed', 'Completed'),
        ('removed', 'Removed'),
    )
    LEVELS = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    )
    urgency = models.CharField(max_length=6, choices=LEVELS, default='medium')
    importance = models.CharField(max_length=6, choices=LEVELS, default='medium')
    complexity = models.CharField(max_length=6, choices=LEVELS, default='medium')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS, default='unassigned')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, null=True, blank=True)
    unit = models.ForeignKey(TaskForceUnit, on_delete=models.CASCADE, null=True, blank=True)
    deadline = models.DateField(null=True, blank=True)
    good_entry_task = models.BooleanField(default=False)
    objects = TicketQuerySet.as_manager()

class TaskForceTicketForm(ModelForm):
    class Meta:
        model = TaskForceTicket
        fields = ['title', 'description', 'assigned_to', 'status', 'importance', 'urgency', 'complexity', 'unit', 'deadline', 'good_entry_task']

class TicketLog(models.Model):
    ticket = models.ForeignKey(TaskForceTicket, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = HTMLField('description', null=True, blank=True)

# Always show the first name instead of username
# https://stackoverflow.com/questions/34214320/django-customize-the-user-models-return-field
def get_first_name(self):
    return self.first_name

User.add_to_class("__str__", get_first_name)
