from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from datetime import date
import datetime
from django.utils import timezone

from .models import Topic, Category, Message, MessageRead, TaskForceMember, TopicForm, TaskForceMemberForm, TaskForceTicketForm, TaskForceTicket, TicketLog, TopicSubscription, TaskForceUnit, Project, ProjectTaskforceForm, ProjectForm
from django.template.defaulttags import register

# These are used so that we can send mail
from django.core.mail import send_mail
from django.template.loader import render_to_string

# We use this to manage which site this is
from django.contrib.sites.models import Site

# Because we need to break lines in the mail message variable
from django.template.defaultfilters import linebreaksbr

# To use the Count function
from django.db.models import Count

# To add two lists with members
# https://stackoverflow.com/questions/431628/how-to-combine-2-or-more-querysets-in-a-django-view
from itertools import chain

from django.contrib.auth.models import User

from django.contrib import messages

# This is to look up a dictionary item, used for
# last message read issue:
# https://stackoverflow.com/questions/8000022/django-template-how-to-look-up-a-dictionary-value-with-a-variable
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@login_required
def export(request):
    list = TaskForceTicket.objects.exclude(taskforce__id=16)
    topics = Topic.objects.all()
    msg = Message.objects.all().order_by('id')
    context = { "list": list, "topics": topics, "msg": msg }
    return render(request, "core/export.html", context)

@login_required
def index(request):
    categories = Category.objects.order_by('name').exclude(group='project').annotate(topic_count=Count('topics'))

    # I really think we can do better than this, but I must figure out _how_
    read = MessageRead.objects.filter(user=request.user)
    unread_category = {}
    total_topics = {}
    for info in read:
        for category in info.topic.categories.all():
            total_topics[category.id] = total_topics.get(category.id, 0) + 1
        if info.topic.last_message.id > info.message.id:
            unread_category[category.id] = 1

    for info in categories:
        count = total_topics.get(info.id)
        if not count:
            if info.topic_count > 0:
                unread_category[info.id] = 1
        elif info.topic_count > count:
            unread_category[info.id] = 1

    context = { 'categories' : categories, 'mainnav': 'mainnav-lg', 'navbar': 'team', 'total_topics': total_topics, 'unread_category': unread_category}
    return render(request, 'team/message.html', context)

@login_required
def member(request):
    categories = Category.objects.order_by('name')
    context = { 'categories' : categories, 'navbar': 'team'}
    return render(request, 'team/profile.edit.html', context)

@login_required
def categoryconfig(request, id):
    info = TaskForceMember.objects.filter(taskforce__id=id, user=request.user)
    category = Category.objects.get(pk=id)
    if info:
        info = info.get()
    else:
        info = TaskForceMember(taskforce=category, user=request.user, notify_of_new_topics=True)
    form = TaskForceMemberForm(instance=info)

    saved = False
    if request.method == 'POST':
        form = TaskForceMemberForm(request.POST, instance=info)
        form.save()
        saved = True
        return redirect('/intranet/taskforce/' + str(category.id))

    context = { 'info': info, 'navbar': 'team', 'category': category, 'form': form }
    return render(request, 'team/category.config.html', context)

@login_required
def category(request, id, topic=False):
    category = Category.objects.get(pk=id)
    list = Topic.objects.filter(categories__id=id).order_by('-last_message_id')

    # I really think we can do better than this, but I must figure out _how_
    read = MessageRead.objects.filter(user=request.user)
    read_message = {}
    for info in read:
        read_message[info.topic.id] = info.message.id

    context = { 'list' : list, 'category': category, 'read_message': read_message, 'topic': topic, 'navbar': 'team' }
    return render(request, 'team/category.html', context)

@login_required
def topic(request, id):
    topic = Topic.objects.get(pk=id)
    list = Message.objects.filter(topic=id)
    categories = topic.categories.all()

    # Registering that this topic was read up and until the last message
    # Assuming that there are actually any messages posted...
    if list:
        read = MessageRead.objects.filter(topic=topic, user=request.user)
        message = list.reverse()[0]
        if read:
            read = read[0]
            read.message = message
        else:
            read = MessageRead(message=message, topic=topic, user=request.user)
        read.save()

    # TODO: I think we can do this much more efficiently
    # First we get all the people who have subscribed to this topic
    # Then we see who is part of the task force, of any of the task forces that this
    # topic is posted in. And then we make a unique list with all those names
    members = TopicSubscription.objects.filter(topic=topic)
    subscribed = False
    for member in members:
        if member.user == request.user:
            subscribed = True

    # TODO: this makes things very slow, for some reason?!
    # For now we'll leave the list unsorted
    #memberlist = sorted(memberlist, key=str.lower)

    ticket = topic.taskforceticket_set.all()
    if ticket:
        ticket = ticket[0]
    context = { 'list' : list, 'topic': topic, 'navbar': 'team', 'members': members, 'categories': categories, 'subscribed': subscribed, 'ticket': ticket }

    return render(request, 'team/chat.html', context)

@login_required
def saveconfig(request, id):
    category = Category.objects.get(pk=id)
    category.google_drive = request.POST['google_drive']
    category.category_description = request.POST['category_description']
    category.save()
    return redirect('/intranet')

@login_required
def subscribetopic(request, id, type):
    topic = Topic.objects.get(pk=id)
    current = TopicSubscription.objects.filter(topic=topic, user=request.user)
    if current:
        current = current.get()
        if type == "unsubscribe":
            current.delete()
        else:
            current.type = type
            current.save()
    else:
        new = TopicSubscription(topic=topic, user=request.user, type=type)
        new.save()
    return redirect('/intranet/topic/'+ str(topic.id) + '/view')

@login_required
def leavetaskforce(request, id):
    taskforce = TaskForceMember.objects.get(pk=id, user=request.user).delete()
    return redirect('/intranet/profile')

@login_required
def createtopic(request):
    topic = Topic(name=request.POST['topic'], author=request.user)
    topic.save()
    topic.categories.add(Category.objects.get(id=request.POST['category']))
    members = TaskForceMember.objects.filter(taskforce__in=topic.categories.all())
    TopicSubscription(topic=topic, user=request.user, type='instantly').save()
    for member in members:
        if member.user != request.user and member.default_subscription != 'none':
            TopicSubscription(topic=topic, user=member.user, type=member.default_subscription).save()
    return redirect('/intranet/topic/' + str(topic.id) + "/edit")

@login_required
def saveprofile(request):
    checked = request.POST.getlist('category')
    TaskForceMember.objects.filter(user=request.user).delete()
    for category in checked:
        taskforce = TaskForceMember(taskforce=Category.objects.get(pk=category), user=request.user, start=date.today(), group_leader = False)
        taskforce.save()
    return redirect('/intranet')

@login_required
def createmessage(request, id):
    message = Message(message=request.POST['message'], topic=Topic.objects.get(pk=id), author=request.user)
    message.save()
    topic = Topic.objects.get(pk=id)
    topic.last_message_id = message.id
    topic.save()
    read = MessageRead.objects.filter(topic=topic, user=request.user)
    if read:
        read = read[0]
        read.message = message
    else:
        read = MessageRead(message=message, topic=topic, user=request.user)
    read.save()

    total_messages = Message.objects.filter(topic=topic).count()

    current_site = Site.objects.get_current()
    scheme = request.scheme
    url = scheme + "://" + current_site.domain
    context = {
        'url': url + '/intranet/topic/'+str(topic.id)+'/view',
        'url_unsubscribe': url + '/intranet/topic/'+str(topic.id)+'/subscription/unsubscribe',
        'url_weekly': url + '/intranet/topic/'+str(topic.id)+'/subscription/weekly',
        'url_daily': url + '/intranet/topic/'+str(topic.id)+'/subscription/daily',
        'url_instantly': url + '/intranet/topic/'+str(topic.id)+'/subscription/instantly',
        'domain' : url,
        'topic': topic.name,
        'message': linebreaksbr(request.POST['message']),
        'message_plain': request.POST['message'],
        'user': request.user.username,
    }

    recipients = []
    # If the @all string is used, everybody in the relevant task force(s) will get an instant notification
    if "@all" in request.POST['message']: 
        members = TaskForceMember.objects.filter(user__is_staff=True, user__is_active=True, taskforce__in=topic.categories.all())
        for member in members:
            if member.user != request.user and member.user.email not in recipients:
                recipients.append(member.user.email)

    # For the first time this is posted, we must notify everyone who wants to be notified of new topics
    if total_messages == 1:
        members = TaskForceMember.objects.filter(user__is_staff=True, user__is_active=True, taskforce__in=topic.categories.all(), notify_of_new_topics=True)
        for member in members:
            if member.user != request.user and member.user.email not in recipients:
                recipients.append(member.user.email)

    # We use the @ sign to trigger an instant email, independently from the user settings
    if "@" in request.POST['message']:
        users = User.objects.filter(is_staff=True, is_active=True)
        for member in users:
            string = str("@") + str(member.first_name)
            if string in request.POST['message'] and member.email not in recipients:
                recipients.append(member.email)

    for member in TopicSubscription.objects.filter(topic=topic, type='instantly'):
        if member.user.email not in recipients:
            if member.user != request.user:
                recipients.append(member.user.email)

    if recipients:
        if total_messages == 1:
    
            for recipient in recipients:
                # If this is the first message, then we will notify everyone that a new topic 
                # has been posted, with a personalized message content
                setting = TopicSubscription.objects.filter(topic=topic, user__email=recipient)
                if setting.count():
                    setting = setting[0]
                    notification_setting = setting.get_type_display()
                else:
                    notification_setting = 'No notification'

                context['notification_setting'] = notification_setting

                msg_html = render_to_string('team/mail/newmessage.html', context)
                msg_plain = render_to_string('team/mail/newmessage.txt', context)

                recipientlist = [recipient]

                send_mail(
                    'New topic: ' + topic.name,
                    msg_plain,
                    'automail@metabolismofcities.org',
                    recipientlist,
                    html_message=msg_html,
                )
        else:
            msg_html = render_to_string('team/mail/newmessage.html', context)
            msg_plain = render_to_string('team/mail/newmessage.txt', context)

            send_mail(
                'Re: ' + topic.name,
                msg_plain,
                'automail@metabolismofcities.org',
                recipients,
                html_message=msg_html,
            )

    return redirect('/intranet/topic/' + str(message.topic.id) + "/view")

def register(request):
    if request.method == 'POST':
        check = User.objects.filter(email=request.POST['email'])
        if check.count:
            error = 'This user already exists. Please <a href="/login">log in</a> instead.'
        else:
            user = User.objects.create_user(request.POST['email'], request.POST['email'], request.POST['password'])
            user.first_name = request.POST['first_name']
            user.last_name = request.POST['last_name']
            user.save()
            return redirect('/accounts/login')
    return render(request, 'registration/register.html')

def login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect('/intranet/controlpanel/')
    else:
        return render(request, '/accounts/login')

@login_required
def opentopic(request, id):
    categories = Category.objects.order_by('name').exclude(group='project').annotate(topic_count=Count('topics'))
    topic = Topic.objects.get(pk=id)

    # I really think we can do better than this, but I must figure out _how_
    read = MessageRead.objects.filter(user=request.user)
    unread_category = {}
    total_topics = {}
    for info in read:
        for category in info.topic.categories.all():
            total_topics[category.id] = total_topics.get(category.id, 0) + 1
        if info.topic.last_message.id > info.message.id:
            unread_category[category.id] = 1

    for info in categories:
        count = total_topics.get(info.id)
        if not count:
            if info.topic_count > 0:
                unread_category[info.id] = 1
        elif info.topic_count > count:
            unread_category[info.id] = 1

    for info in topic.categories.all():
        # check if member
        category = info

    context = { 'categories' : categories, 'mainnav': 'mainnav-lg', 'navbar': 'team', 'total_topics': total_topics, 'unread_category': unread_category, 'topic': topic, 'category': category }
    return render(request, 'team/message.html', context)

@login_required
def opencategory(request, id):
    categories = Category.objects.order_by('name').exclude(group='project').annotate(topic_count=Count('topics'))

    # I really think we can do better than this, but I must figure out _how_
    read = MessageRead.objects.filter(user=request.user)
    unread_category = {}
    total_topics = {}
    for info in read:
        for category in info.topic.categories.all():
            total_topics[category.id] = total_topics.get(category.id, 0) + 1
        if info.topic.last_message.id > info.message.id:
            unread_category[category.id] = 1

    for info in categories:
        count = total_topics.get(info.id)
        if not count:
            if info.topic_count > 0:
                unread_category[info.id] = 1
        elif info.topic_count > count:
            unread_category[info.id] = 1

    category = Category.objects.get(pk=id)
    context = { 'categories' : categories, 'navbar': 'team', 'total_topics': total_topics, 'unread_category': unread_category, 'category': category, 'mainnav': 'mainnav-lg' }
    return render(request, 'team/message.html', context)

def taskforces(request):
    list = Category.objects.all()
    context = { 'list' : list, 'navbar': 'core', 'section': 'about', 'page': 'taskforces' }
    return render(request, 'team/taskforces.html', context)


@login_required
def edittopic(request, id):
    info = Topic.objects.get(pk=id)
    saved = False
    form = TopicForm(instance=info)
    if request.method == 'POST':
        form = TopicForm(request.POST, instance=info)
        form.save()
        saved = True
        return redirect('/intranet/topic/'+ str(info.id) + '/view')
    context = { 'navbar': 'team', 'info': info, 'form': form, 'saved': saved }
    return render(request, 'team/topic.edit.html', context)


@login_required
def search(request):
    # TO DO
    # We must add a filter later on that only filters for the topics that someone is registered for.
    if "keyword" in request.GET:
        keyword = request.GET['keyword']
        list = Message.objects.filter(message__search=keyword).order_by('-date')
    else:
        keyword = ''
        list = []
    context = { 'list' : list, 'navbar': 'team', 'section': 'about', 'page': 'search', 'keyword': keyword }

    return render(request, 'team/search.html', context)


@login_required
def controlpanel(request):
    community = Category.objects.filter(group='community')
    board = Category.objects.filter(group='board').all()
    services = Category.objects.filter(group='services').get()
    projects = Category.objects.filter(group='project').all()
    context = { 'navbar': 'backend', 'community': community, 'board': board, 'services': services, 'projects': projects }
    current_site = Site.objects.get_current()
    if current_site.id == 1:
        return render(request, 'team/controlpanel.html', context)
    else:
        return render(request, 'team/controlpanel.moi.html', context)

@login_required
def profile(request):
    taskforces = TaskForceMember.objects.filter(user=request.user)
    context = { 'navbar': 'backend', 'taskforces': taskforces }
    return render(request, 'team/profile.html', context)

@login_required
def projects(request):
    projects = Project.objects.all().order_by('-status')
    context = { 'navbar': 'backend', 'projects': projects}
    return render(request, 'team/projects.html', context)

@login_required
def project(request, id=False):
    if id:
        info = Project.objects.get(pk=id)
        form = ProjectForm(instance=info)
        taskforceform = ProjectTaskforceForm(instance=info.taskforce, prefix='taskforce')
    else:
        info = False
        form = ProjectForm()
        taskforceform = ProjectTaskforceForm(prefix='taskforce')
    saved = False
    if request.method == 'POST':
        if not id:
            taskforce = Category.objects.create(group='project')
            info = Project.objects.create(taskforce=taskforce)
        form = ProjectForm(request.POST, instance=info)
        taskforceform = ProjectTaskforceForm(request.POST, instance=info.taskforce, prefix='taskforce')
        if form.is_valid() and taskforceform.is_valid():
            form.save()
            taskforceform.save()
            saved = True
            messages.success(request, 'Information was saved.')
            return redirect('/intranet/taskforce/'+ str(info.taskforce.id))
        else:
            messages.warning(request, 'We could not save your form, please correct the errors')
    context = { 'navbar': 'backend', 'info': info, 'form': form, 'taskforceform': taskforceform }
    return render(request, 'team/project.html', context)

@login_required
def taskforce(request, id):
    info = Category.objects.get(pk=id)
    members = TaskForceMember.objects.filter(taskforce=info)
    tickets = TaskForceTicket.objects.filter(taskforce=info).exclude(status='completed').exclude(status='removed').order_by('title')
    units = TaskForceUnit.objects.filter(taskforce=info).order_by('name')
    projectinfo = False

    if info.group == 'project':
        projectinfo = Project.objects.get(taskforce=id)

    context = { 'navbar': 'backend', 'info': info, 'members': members, 'tickets': tickets, 'units': units, 'project': projectinfo }
    return render(request, 'team/taskforce.html', context)

@login_required
def ticketdetails(request, id):
    info = TaskForceTicket.objects.get(pk=id)
    log = info.ticketlog_set.all().order_by('created_at')
    users = User.objects.filter(is_staff=True)

    choices = TaskForceTicket.STATUS
    context = { 'navbar': 'backend', 'info': info, 'choices': choices, 'log': log, 'users': users }
    return render(request, 'team/ticket.view.html', context)

@login_required
def ticketstatus(request, id, status):
    info = TaskForceTicket.objects.get(pk=id)
    info.status = status
    info.save()

    log = TicketLog.objects.create(
        ticket = info,
        user = request.user,
        title = "Status changed to: " + str(info.get_status_display()),
    )
    log.save()
    return redirect('/intranet/tickets/'+str(info.id))

@login_required
def ticketperson(request, id, person):
    info = TaskForceTicket.objects.get(pk=id)
    info.assigned_to = User.objects.get(pk=person)
    if info.status == 'unassigned':
        info.status = 'assigned'
    info.save()

    log = TicketLog.objects.create(
        ticket = info,
        user = request.user,
        title = "Assigned to: " + str(info.assigned_to.first_name),
    )
    log.save()

    return redirect('/intranet/tickets/'+str(info.id))

@login_required
def ticketprogress(request, id):
    info = TaskForceTicket.objects.get(pk=id)
    if request.method == 'POST':
        log = TicketLog.objects.create(
            ticket = info,
            user = request.user,
            title = "Progress update",
            description = request.POST['progress'],
        )
        log.save()

    return redirect('/intranet/tickets/'+str(info.id))

@login_required
def ticketdiscussion(request, id):
    info = TaskForceTicket.objects.get(pk=id)
    topic = Topic(name=info.title, author=request.user)
    topic.save()
    info.topic = topic
    info.save()
    topic.categories.add(info.taskforce)
    members = TaskForceMember.objects.filter(taskforce__in=topic.categories.all())
    TopicSubscription(topic=topic, user=request.user, type='instantly').save()
    for member in members:
        if member.user != request.user and member.default_subscription != 'none':
            TopicSubscription(topic=topic, user=member.user, type=member.default_subscription).save()

    return redirect('/intranet/topic/' + str(topic.id) + "/edit")

@login_required
def ticket(request, id=False, category=False):
    if id:
        info = TaskForceTicket.objects.get(pk=id)
        category = info.taskforce
        edit = True
    else:
        category = Category.objects.get(pk=category)
        info = TaskForceTicket(taskforce=category)
        edit = False
    saved = False
    form = TaskForceTicketForm(instance=info)
    if request.method == 'POST':
        form = TaskForceTicketForm(request.POST, instance=info)
        form.save()
        saved = True
        if not id:
            log = TicketLog.objects.create(
                ticket = info,
                user = request.user,
                title = "Task was created"
            )
            log.save()
        return redirect('/intranet/tickets/'+ str(info.id))
    context = { 'navbar': 'backend', 'info': info, 'form': form, 'saved': saved, 'category': category, 'edit': edit }
    return render(request, 'team/ticket.html', context)

@login_required
def ticketreport(request):
    if request.GET.get('show') == "all" or request.GET.get('show') == "my_work":
        taskforces = Category.objects.all()
    elif request.GET.get('show') == "my_taskforces":
        taskforces = Category.objects.filter(members=request.user)

    if request.GET.get('user') == "all" or request.GET.get('user') is None:
        user = "all"
        if request.GET.get('tasks') == "all":
            log = TicketLog.objects.filter(ticket__taskforce__in=taskforces)
        elif request.GET.get('tasks') == "new":
            log = TicketLog.objects.filter(ticket__taskforce__in=taskforces, title='Task was created')
        elif request.GET.get('tasks') == "updates":
            log = TicketLog.objects.filter(ticket__taskforce__in=taskforces, title='Progress update')
        elif request.GET.get('tasks') == "completed":
            log = TicketLog.objects.filter(ticket__taskforce__in=taskforces, title='Status changed to: Completed')

    else:
        user = int(request.GET.get('user'))
        if request.GET.get('tasks') == "all":
            log = TicketLog.objects.filter(ticket__taskforce__in=taskforces, user=user)
        elif request.GET.get('tasks') == "new":
            log = TicketLog.objects.filter(ticket__taskforce__in=taskforces, title='Task was created', user=user)
        elif request.GET.get('tasks') == "updates":
            log = TicketLog.objects.filter(ticket__taskforce__in=taskforces, title='Progress update', user=user)
        elif request.GET.get('tasks') == "completed":
            log = TicketLog.objects.filter(ticket__taskforce__in=taskforces, title='Status changed to: Completed', user=user)

    users = User.objects.filter(is_staff=True, is_active=True)

    context = { 'navbar': 'backend', 'log': log, 'show': request.GET.get('show'), 'filter_task': request.GET.get('tasks'), 'users': users, 'user': user, 'datatables': True }
    return render(request, 'team/ticket.report.html', context)

@login_required
def ticketlist(request):
    if request.GET.get('show') == "all":
        taskforces = Category.objects.all()
    else:
        taskforces = Category.objects.filter(members=request.user)
    if request.GET.get('user') == "all":
        user = "all"
        if request.GET.get('status') == "all":
            list = TaskForceTicket.objects.filter(taskforce__in=taskforces)
        else:
            list = TaskForceTicket.objects.filter(taskforce__in=taskforces, status=request.GET.get('status'))
    else:
        user = int(request.GET.get('user'))
        if request.GET.get('status') == "all":
            list = TaskForceTicket.objects.filter(taskforce__in=taskforces, assigned_to=user)
        else:
            list = TaskForceTicket.objects.filter(taskforce__in=taskforces, assigned_to=user, status=request.GET.get('status'))
    status_list = TaskForceTicket.STATUS
    users = User.objects.filter(is_staff=True, is_active=True)
    context = { 'navbar': 'backend', 'list': list, 'show': request.GET.get('show'), 'filter_task': request.GET.get('tasks'), 'status_list': status_list, 'set_status': request.GET.get('status'), 'user': user, 'users': users, 'datatables': True }
    return render(request, 'team/ticket.list.html', context)

@login_required
def deletemessage(request, id):
    message = get_object_or_404(Message, pk=id)
    topic = message.topic
    if message.author == request.user:
        MessageRead.objects.filter(message=message).delete()
        message.delete()

    return redirect('/intranet/topic/' + str(message.topic.id) + '/view')

