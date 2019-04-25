from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Journal, Organization, Publisher, Reference, ReferenceForm, ReferenceFormAdmin, People, Article, PeopleForm, Video, VideoForm, ReferenceOrganization, Project, UserAction, UserLog, SimpleArticleForm, ProjectForm, ProjectUserForm, EventForm, ReferenceType, Tag, Event, TagForm, OrganizationForm, VideoCollection, VideoCollectionForm, PeopleNote, PeopleAffiliation, ReferenceAuthors
from team.models import Category, TaskForceMember, TaskForceTicket, TaskForceUnit
from multiplicity.models import ReferenceSpace
from staf.models import Data, Process, Material
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.sites.models import Site
from django.http import Http404, HttpResponseRedirect

# These are used so that we can send mail
from django.core.mail import send_mail
from django.template.loader import render_to_string

from django.conf import settings

from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt

from collections import defaultdict

def videos(request, collection=False, all=False):
    editlink = False
    if not collection and not all:
        if request.site.id == 1:
            collection = 4
        else:
            collection = 6

    if collection:
        collection = get_object_or_404(VideoCollection, pk=collection)
        editlink = reverse("core:admin_videocollection", args=[collection.id])
    id = 87
    if request.site.id == 2:
        id = 150
    collections = VideoCollection.on_site.all().exclude(pk=7)
    if all:
        list = Video.on_site.all().exclude(collections__id=7).order_by('title')
    else:
        list = Video.on_site.filter(collections=collection).order_by('title')
    addlink = "/admin/videos/create"
    context = { "section": "resources", "collection": collection, "addlink": addlink,
    "collections": collections, "list": list, "editlink": editlink, 'all': all }
    return render(request, "core/videos.html", context)

def video(request, id):
    info = get_object_or_404(Video, pk=id)
    editlink = ""+str(id) + "/change/"
    editlink = reverse("core:admin_video", args=[id])

    context = { "section": "resources", "page": "video", "info": info, "editlink": editlink }
    return render(request, "core/video.html", context)

def search(request):
    context = { "section": "resources", "page": ""  }
    return render(request, "core/search.html", context)

def home(request):
    context = { "section": "home", "page": ""  }
    return render(request, "core/home.html", context)

def index(request):
    if request.site.id == 1:
        main_filter = 11 # This is urban systems
        context = { "section": "home", "page": ""  }
        return render(request, "core/home.html", context)
    else:
        main_filter = 219
    publications = False
    events = False
    projects = False
    if request.site.id == 1:
        news = Article.objects.filter(parent=61).order_by("-created_at")[:5]
        events = Article.objects.filter(parent=59).order_by("-created_at")[:5]
    else:
        news = Article.objects.filter(parent=142).order_by("-created_at")[:5]
        #publications = Reference.objects.exclude(type=10).order_by("-id")[:5]
        publications = Reference.objects.filter(status="active", tags__id=main_filter).order_by("-id").exclude(type=10)
        projects = Project.on_site.order_by("-id")[:5]
    context = { "news": news, "events": events, "publications": publications, "projects": projects }
    if request.site.id == 1:
        return render(request, "core/index.html", context)
    else:
        return render(request, "core/index.moi.html", context)

def empty(request):
    context = { "section": "about", "page": "about"}
    return render(request, "core/empty.html", context)

def section_home(request, slug):
    if slug == "about":
        pages = [36, 37, 39, 40, 43, 45, 46]
    elif slug == "resources":
        pages = [68, 125, 65, 88, 87, 75, 111, 77]
    elif slug == "community":
        pages = [50, 57, 49, 59, 61]
    else:
        from django.http import Http404
        raise Http404("Page does not exist (section home)")
    list = Article.on_site.filter(id__in=pages)
    context = { "section": slug, "list": list}
    return render(request, "core/section.html", context)

def literature(request):
    context = { "section": "literature", "page": "home"}
    return render(request, "core/literature.html", context)

def team(request):
    page = Article.objects.get(pk=39)
    list = People.objects.exclude(member_since__isnull=True).order_by("member_since")
    context = { "section": "about", "list": list, "page": page }
    return render(request, "core/team.html", context)

def taskforces(request):
    list = Category.objects.filter(group="community", position__isnull=False).order_by("position")
    page = Article.objects.get(pk=40)
    context = { "section": "about", "page": "taskforces", "list": list, "page": page}
    return render(request, "core/taskforces.html", context)

def taskforce(request, slug):
    info = get_object_or_404(Category, slug=slug)
    tickets = TaskForceTicket.objects.filter(taskforce=info).exclude(status="removed").order_by("title")
    units = TaskForceUnit.objects.filter(taskforce=info).order_by("name")
    taskforces = Category.objects.filter(group="community", position__isnull=False).order_by("position")
    context = { "section": "about", "page": "taskforces", "info": info, "tickets": tickets, "units": units, "sidenav": True, "taskforces": taskforces }
    return render(request, "core/taskforce.html", context)

def notfound(request):
    return render(request, "404.html")

@csrf_exempt
def page(request, slug):
    page = get_object_or_404(Article, slug=slug, site=request.site, active=True)
    content = page.content
    context = { "section": page.section, "page": "news", "page": page, "content": content }
    return render(request, "core/page.html", context)

@csrf_exempt
def contact(request):

    name = request.POST["name"]
    email = request.POST["email"]
    message = request.POST["message"]
    organization = request.POST["organization"]
    context = {
        "name": name,
        "email": email,
        "organization": organization,
        "message": message
    }

    message = render_to_string("core/mail/contactform.txt", context)

    send_mail(
        "Contact form Metabolism of Cities (" + name + ")",
        message,
        settings.SITE_EMAIL,
        [settings.SITE_EMAIL],
    )
    messages.success(request, "Thanks, we have received your message!")
    return redirect("core:contact")


def sectionpage(request, id=None, slug=None):
    if id:
        info = get_object_or_404(Article, pk=id)
    elif slug:
        info = get_object_or_404(Article, slug=slug)
    editlink = "/admin/core/article/"+str(info.id) + "/change/"
    list = Article.objects.filter(active=True, parent=info.parent).order_by("created_at")
    context = { "section": "markcities", "page": info.slug, "info": info, "editlink": editlink, "list": list, "datatables": True}
    return render(request, "core/article.section.html", context)

def article(request, id):
    info = get_object_or_404(Article, pk=id)
    event = False
    if not info.active and not request.user.is_authenticated:
        raise Http404("Page was not found")
    if hasattr(info, "event"):
        event = info.event
    editlink = "/admin/articles/"+str(id)
    section = info.section
    if info.parent:
        section = info.parent.section
    list = Article.objects.filter(active=True, parent=info.parent).order_by("-created_at")[:8]
    context = { "section": section, "page": "news", "info": info, "editlink": editlink, "list": list, "event": event}
    return render(request, "core/article.html", context)

def articles(request, parent):
    order = "-created_at"
    if parent == "events":
        match = { 1: 59, 2: 143 }
        parent = match[request.site.id]
        years = [2020, 2019, 2018]
        order = "event__start"
    elif parent == "news":
        match = { 1: 61, 2: 142 }
        parent = match[request.site.id]
        years = [2019, 2018, 2017]
        order = "-date"
    elif parent == "blog":
        match = { 1: 60, 2: 142 }
        parent = match[request.site.id]
        years = [2017, 2016]
        order = "-date"
    list = Article.objects.filter(active=True, parent__id=parent, site=request.site).order_by(order)
    page = Article.objects.get(pk=parent)
    section = page.section
    addlink = reverse("core:admin_article_parent", args=[parent])
    context = { "section": section, "page": page, "list": list, "addlink": addlink, "years": years }
    return render(request, "core/news.html", context)

def news_and_events(request):
    match = { 1: 59, 2: 143 }
    events = match[request.site.id]
    match = { 1: 61, 2: 142 }
    news = match[request.site.id]
    news_list = Article.objects.filter(active=True, parent__id=news, site=request.site).order_by("-created_at")
    events_list = Event.objects.filter(article__active=True, article__site=request.site).order_by("start")
    page = Article.objects.get(pk=news)
    section = page.section
    add_news_link = reverse("core:admin_article_parent", args=[news])
    add_events_link = reverse("core:admin_article_parent", args=[events])
    context = { "section": section, "page": page, "news_list": news_list, "events_list": events_list, "add_news_link": add_news_link, "add_events_link": add_events_link }
    return render(request, "core/news.events.html", context)

def people(request):
    list = People.objects.all()
    page = get_object_or_404(Article, pk=49)
    context = { "section": "community", "page": "people", "list": list, "page": page}
    return render(request, "core/people.html", context)

def peopledetails(request, id):
    from django.db.models import Sum
    info = get_object_or_404(People, pk=id)
    list = Reference.objects.filter(authors__id=id)
    videos = info.video_set.all()
    references = Reference.objects.filter(status="active", authors=info)
    if info.user:
        points = UserLog.objects.filter(user=info.user).aggregate(total=Sum("points"))
        log = info.user.log
        if log:
            log = log.all()[:10]
    else:
        points = False
        log = False
    context = { "section": "community", "page": "people", "info": info, "list": list, "videos": videos, "references": references, "points": points, "log": log }
    return render(request, "core/people.details.html", context)

def userdetails(request, id):
    # For each user we have one record in the people table
    # However, this record is not created by default
    # Here we check if it exists. If not, we"ll create a new one
    # Our final goal is to redirect to the appropriate people page
    people = get_object_or_404(People, user=id)
    if not people:
        info = get_object_or_404(User, pk=id)
        if info.is_active:
            people = People.objects.create(
                name = info.first_name + str(" ") + info.last_name,
                email = user.email,
                user = user,
            )

    if not people:
        raise Http404("No user found")
    else:
        return redirect(reverse("core:peopledetails", args=[people.id]))

def journals(request):
    list = Journal.objects.order_by("name").annotate(num_references=Count("reference"))
    datatables = True
    page = get_object_or_404(Article, pk=111)
    context = { "page": page, "list": list, "datatables": datatables}
    return render(request, "core/journals.html", context)

def journal(request, id):
    info = get_object_or_404(Journal, pk=id)
    references = Reference.objects.filter(journal_id=id).order_by("-year")
    context = { "section": "literature", "page": "journals", "info": info, "references": references}
    return render(request, "core/journal.html", context)

def organizations(request, type):
    if type == "universities":
        page_id = 48

    page = get_object_or_404(Article, pk=page_id)
    list = Organization.objects.filter(type=type, parent__isnull=True).order_by("name")
    context = { "section": "community", "page": "organizations", "list": list, "page": page}
    return render(request, "core/organizations.html", context)

def organization(request, id):
    info = get_object_or_404(Organization, pk=id)
    list = Reference.objects.filter(Q(organizations__id=id) | Q(organizations__parent__id=id)).order_by("-year")
    divisions = Organization.objects.filter(parent=info)
    editlink = "/admin/core/organization/"+str(id) + "/change/"
    context = { "section": "community", "page": "organizations", "info": info, "list": list, "editlink": editlink, "divisions": divisions}
    return render(request, "core/organization.html", context)

def events(request):
    list = Event.objects.all
    context = { "section": "literature", "page": "organizations", "list": list}
    return render(request, "core/events.html", context)

def event(request, id):
    info = get_object_or_404(Event, pk=id)
    list = Reference.objects.filter(event_id=id).order_by("-year")
    context = { "section": "literature", "page": "events", "info": info, "list": list}
    return render(request, "core/event.html", context)

def publishers(request):
    list = Publisher.objects.order_by("name")
    context = { "section": "literature", "page": "publishers", "list": list}
    return render(request, "core/publishers.html", context)

def publisher(request, id):
    info = get_object_or_404(Publisher, pk=id)
    list = Reference.objects.filter(publisher_id=id).order_by("-year")
    context = { "section": "literature", "page": "publishers", "info": info, "list": list}
    return render(request, "core/publisher.html", context)

def reference(request, id):
    info = get_object_or_404(Reference, pk=id)
    if request.site.id == 1:
        main_filter = 11 # This is urban systems
    else:
        main_filter = 219
    related = Reference.objects.filter(status="active", tags__id=main_filter).order_by("-id")[:5]
    authors = info.authors.all()
    data = Data.objects.filter(dataset__references=info)
    editlink = reverse("core:admin_reference", args=[info.id])
    context = { "section": "literature", "page": "publications", "info": info, "related": related, "authors": authors, "editlink": editlink, "data": data, "datatables": True }
    return render(request, "core/reference.html", context)

@login_required
def referenceform(request, id=False, dataset=False):
    new_record = False
    if request.site.id == 1:
        main_filter = 11 # This is urban systems
    else:
        main_filter = 219

    if id:
        info = get_object_or_404(Reference, pk=id)
        if request.user.is_staff:
            form = ReferenceFormAdmin(instance=info)
        else:
            form = ReferenceForm(instance=info)
    else:
        info = False
        if request.user.is_staff:
            form = ReferenceFormAdmin(initial={"language": "EN", "status": "active", "tags": main_filter})
        else:
            form = ReferenceForm()
    if request.method == "POST":
        if not id:
            new_record = True
            if request.user.is_staff:
                form = ReferenceFormAdmin(request.POST, request.FILES)
            else:
                form = ReferenceForm(request.POST)
        else:
            if request.user.is_staff:
                form = ReferenceFormAdmin(request.POST, request.FILES, instance=info)
            else:
                form = ReferenceForm(request.POST, instance=info)
        if form.is_valid():
            info = form.save()
            if new_record:
                create_record = get_object_or_404(UserAction, pk=1)
                log = UserLog(user=request.user, action=create_record, reference=info, points=5)

            messages.success(request, "Information was saved.")
            return redirect("core:reference", id=info.id)
        else:
            messages.error(request, "We could not save your form, please correct the errors")

    context = { "section": "resources", "page": "publications", "info": info, "form": form, "dataset": dataset }
    return render(request, "core/reference.form.html", context)

@staff_member_required
def referenceform_authors(request, id, delete=False):

    info = get_object_or_404(Reference, pk=id)

    if delete:
        ReferenceAuthors.objects.get(pk=delete).delete()
        messages.success(request, "Author was deleted.")

    if request.method == "POST" and "author" in request.POST:
        ReferenceAuthors.objects.create(
            people = get_object_or_404(People, pk=request.POST["author"]),
            reference = info
        )
        messages.success(request, "Author was added.")
        
    context = { 
        "section": "resources", 
        "page": "publications", 
        "info": get_object_or_404(Reference, pk=id), 
        "list": People.objects.filter(status="active"),
        "authors": ReferenceAuthors.objects.filter(reference=info).order_by("id"),
    }
    return render(request, "core/reference.form.authors.html", context)


@staff_member_required
def referenceform_tags(request, id):
    info = get_object_or_404(Reference, pk=id)
    if request.method == "POST":
        info.tags.clear()
        selected = request.POST.getlist("tags")
        for tag in selected:
            info.tags.add(Tag.objects.get(pk=tag))
        messages.success(request, "Information was saved.")
        return redirect("core:editreference_multiplicity", id=info.id)
    context = { 
        "navbar": "backend", 
        "tags": Tag.objects.filter(hidden=False, parent_tag__isnull=False), 
        "info": info, 
        "parent_tags": Tag.objects.filter(parent_tag__isnull=True, hidden=False), 
        "select2": True,
    }
    return render(request, "core/admin/reference.tags.html", context)


@staff_member_required
def referenceform_multiplicity(request, id):

    info = get_object_or_404(Reference, pk=id)

    if request.method == "POST":
        info.processes.clear()
        selected = request.POST.getlist("processes")
        for process in selected:
            info.processes.add(Process.objects.get(pk=process))

        info.materials.clear()
        selected = request.POST.getlist("materials")
        for materials in selected:
            info.materials.add(Material.objects.get(pk=materials))

        info.spaces.clear()
        selected = request.POST.getlist("spaces")
        for spaces in selected:
            info.spaces.add(ReferenceSpace.objects.get(pk=spaces))

        messages.success(request, "Information was saved.")

    context = {
        "section": "resources", 
        "page": "publications", 
        "info": info, 
        "processes": Process.objects.filter(slug__isnull=False).order_by("id"),
        "select2": True,
        "materials": Material.objects.filter(parent__isnull=True).order_by('code'),
    }
    return render(request, "core/admin/reference.form.multiplicity.html", context)



def references(request, type=False, tag=False):
    if request.site.id == 1:
        main_filter = 11 # This is urban systems
    else:
        main_filter = 219 # Island system
    if type:
        type = get_object_or_404(ReferenceType, pk=type)
        list = Reference.objects.filter(status="active", type=type, tags__id=main_filter).order_by("-year")
        title = type.name + "s"
    else:
        if tag:
            list = Reference.objects.filter(status="active", tags__id=main_filter).filter(tags__id=tag).order_by("-year")
            tag = get_object_or_404(Tag, pk=tag, hidden=False)
            title = tag.name + " | Publications"
        else:
            list = Reference.objects.filter(status="active", tags__id=main_filter).order_by("-year")
            title = "Publications"
    maintags = Tag.objects.filter(parent_tag__isnull=True, hidden=False)
    addlink = reverse("core:newreference")

    cities_list = Reference.objects.filter(status="active", tags__id=main_filter, spaces__type__id=3)
    cities = defaultdict(dict)
    cities_references = {}

    # TODO
    # We can improve this a lot
    for details in cities_list:
        for sub in details.spaces.all():
            if sub.type.id == 3:
                cities[sub.id] = sub
                reference = details
                if sub.id in cities_references and details not in cities_references[sub.id]:
                    cities_references[sub.id].append(details)
                else:
                    cities_references[sub.id] = []
                    cities_references[sub.id].append(details)

    cities = dict(cities)
    context = { 
        "section": "resources",
        "list": list, 
        "addlink": addlink, 
        "title": title, 
        "select2": True, 
        "tag": tag, 
        "maintags": maintags, 
        "page": get_object_or_404(Article, pk=75),
        "methodologies": Tag.objects.filter(parent_tag__id=318, hidden=False),
        "cities": cities,
        "cities_references": cities_references,
    }
    return render(request, "core/references.list.html", context)

def references_old(request, type=False, tag=False):
    title = "Publications"
    list = None
    cities = None
    reference_types = False
    selected_keywords = []
    entered_keywords = []

    if "terms" in request.GET:
        list = Reference.objects.filter(status="active")
        terms = request.GET.getlist("terms")

        for term in terms:
            try:
                int(term)
                list = list.filter(tags__id=term)
                selected_keywords.append(int(term))
                
            except ValueError:
                list = list.filter(abstract__icontains=term)
                entered_keywords.append(term)

    maintags = Tag.objects.filter(parent_tag__isnull=True, hidden=False)
    tags = Tag.objects.filter(hidden=False)

    addlink = reverse("core:newreference")

    if list:
        reference_types = list.values("type__name").order_by("type__name").distinct()
    else:
        cities = Tag.objects.filter(parent=4, hidden=False).order_by("name")

    context = { 
        "section": "resources", "page": "publications", "references": list, "addlink": addlink, 
        "title": title, "select2": True, "maintags": maintags, "tags": tags,
        "selected_keywords": selected_keywords, "entered_keywords": entered_keywords,
        "reference_types": reference_types, "cities": cities, "datatables": True
    }
    return render(request, "core/references.html", context)


def updatejournals(request):
    list = Journal.objects.order_by("name")
    unis = [51, 57, 78, 88, 140, 6, 49, 45, 135, 139, 53, 35, 83, 117, 90, 105, 27, 26, 18, 25, 3, 24, 62, 19]
    events = [134, 86, 32, 122, 87, 63, 54, 55, 29, 42, 56]
    publishers = [22, 30, 82, 94, 38, 97, 130]
    for info in list:
        if info.id in publishers:
            publisher = Publisher(name=info.name)
            publisher.save()
            info.delete()

        if info.id in events:

            if info.id == 55:
                event = Event.objects.get(name="REAL CORP - International Conference on Urban Planning and Regional Development in the Information Society ")
            else:
                event = Event(name=info.name, type="conference")
                event.save()
            info.delete()

        if info.id in unis:

            uni = Organization(name=info.name)
            uni.type = "universities"
            uni.save()

            if info.id == 51:
                uni.name = "University of Cape Town"
                division = Division(name="Department of Environmental & Geographical Science", organization=uni)
                division.save()
                uni.save()

            if info.id == 57:
                uni.delete()
                uni = Organization.objects.get(name="University of Cape Town")

            if info.id == 27:
                uni.delete()
                uni = Organization.objects.get(name="European Commission")

            if info.id == 78:
                uni.name = "Delft University of Technology"
                division = Division(name="Faculty of Architecture and the Built Environment", organization=uni)
                division.save()
                uni.save()

            if info.id == 140:
                uni.name = "Institute for Interdisciplinary Studies at Austrian Universities"
                division = Division(name="Department for Social Ecology", organization=uni)
                division.save()
                uni.save()

            if info.id == 6:
                uni.name = "Massachusetts Institute of Technology"
                division = Division(name="Department of Architecture", organization=uni)
                division.save()
                uni.save()

            if info.id == 49:
                uni.delete()
                uni = Organization.objects.get(name="Massachusetts Institute of Technology")
                division = Division(name="Department of Architecture", organization=uni)
                division.save()
                uni.save()

            if info.id == 45:
                uni.name = "Yale University"
                division = Division(name="Yale Center for Industrial Ecology", organization=uni)
                division.save()
                uni.save()

            if info.id == 135:
                uni.delete()
                uni = Organization.objects.get(name="Yale")
                division = Division(name="Yale School of Forestry & Environmental Studies", organization=uni)
                division.save()

            info.delete()
    context = { "section": "literature", "page": "journals", "list": list}
    return render(request, "core/empty.html", context)

# Now update papers with the previous journal to reflect the university
def updateorgs(request):

    list = Organization.objects.order_by("name")
    for info in list:
        if info.id == 45 and info.name != "Center for Industrial Ecology":
            info.name = "Center for Industrial Ecology"
            info.type = "universities"
            main = Organization(name="Yale University", type="universities", id=200)
            main.save()
            info.parent = main
            info.save()

        if info.id == 6 or info.id == 49:
            info.location = ReferenceSpace.objects.get(pk=94)
            info.save()

        if info.id == 19:
            info.location = ReferenceSpace.objects.get(pk=103)
            info.save()

        if info.id == 78 and info.name != "Faculty of Architecture and the Built Environment":
            info.name = "Faculty of Architecture and the Built Environment"
            info.type = "universities"
            main = Organization(name="Delft University of Technology", type="universities", id=201)
            main.save()
            info.parent = main
            info.save()

        if info.id == 35 and info.name != "Institute of Environmental Sciences (CML)":
            info.name = "Institute of Environmental Sciences (CML)"
            info.type = "universities"
            info.location = ReferenceSpace.objects.get(pk=78)
            main = Organization(name="Leiden University", type="universities", id=203)
            main.location = ReferenceSpace.objects.get(pk=78)
            main.save()
            info.parent = main
            info.save()

        if info.id == 140 and info.name != "Department for Social Ecology":
            info.name = "Department for Social Ecology"
            info.type = "universities"
            main = Organization(name="Institute for Interdisciplinary Studies at Austrian Universities", type="universities", id=202)
            main.save()
            info.parent = main
            info.save()

        if info.id == 6 and info.name != "Department of Architecture":
            info.name = "Department of Architecture"
            info.type = "universities"
            info.parent = Organization.objects.get(pk=49)
            info.save()

        if info.id == 51:
            info.parent = Organization.objects.get(pk=57)
            info.name = "Department of Environmental & Geographical Science"
            info.type = "universities"
            info.location = ReferenceSpace.objects.get(pk=2)
            info.save()

        if info.id == 57:
            info.location = ReferenceSpace.objects.get(pk=2)
            info.save()

        if info.id == 135:
            info.parent = Organization.objects.get(pk=200)
            info.name = "School of Forestry & Environmental Studies"
            info.type = "universities"
            info.save()

        if info.id == 24:
            info.name = "Sustainable Europe Research Institute."
            info.type = "universities"
            info.save()

        if info.id == 83:
            info.parent = Organization.objects.get(pk=105)
            info.name = "CORDIS"
            info.save()

        if info.id == 130:
            info.parent = Organization.objects.get(pk=200)
            info.save()

        unis = [19,26,35,49,57,88,148]

        if info.id in unis:
            info.type = "universities"
            info.save()

    Organization.objects.filter(type="academic").update(type="university")
    Organization.objects.filter(type="university").update(type="universities")
    seri = Organization.objects.filter(pk=24)
    if seri.count():
        newseri = Organization.objects.get(pk=25)
        newseri.type = "universities"
        newseri.save()
        ReferenceOrganization.objects.filter(organization=seri).update(organization=newseri)
        seri.delete()

    context = { "section": "literature", "page": "journals", "list": list}
    return render(request, "core/empty.html", context)

def projects(request, type, status=False):
    if status:
        list = Project.on_site.filter(type=type, status=status, active=True, pending_review=False)
    else:
        list = Project.on_site.filter(type=type, active=True, pending_review=False)
    if request.site.id == 1:
        if type == "projects":
            page = 50
        elif type == "theses":
            page = 57
    elif request.site.id == 2:
        if type == "projects":
            page = 149
        elif type == "theses":
            page = 148
    page = get_object_or_404(Article, pk=page)
    addlink = reverse("core:admin_project_create")
    context = { "section": "community", "list": list, "page": page, "addlink": addlink, "datatables": True }
    return render(request, "core/projects.html", context)

def project(request, type, id):
    info = get_object_or_404(Project, pk=id)
    editlink = reverse("core:admin_project", args=[info.id])
    references = info.references.all()
    context = { "section": "community", "list": list, "info": info, "editlink": editlink, "references": references}
    return render(request, "core/project.view.html", context)

def project_form(request, id=False):
    if request.site.id == 1:
        page = 50
    else:
        page = 50

    if id:
        info = get_object_or_404(Project, pk=id)
        form = ProjectUserForm(instance=info)
    else:
        info = False
        form = ProjectUserForm()
    if request.method == "POST":
        if not id:
            new_record = True
            form = ProjectUserForm(request.POST)
        else:
            form = ProjectUserForm(request.POST, instance=info)
        if form.is_valid():
            info = form.save(commit=False)
            info.site = request.site
            info.save()

            if new_record:
                create_record = get_object_or_404(UserAction, pk=1)
                if request.user.is_authenticated:
                    log = UserLog(user=request.user, action=create_record, model="Research", points=5, description=info.name)
                info.pending_review = True
                info.save()

                # Must send mail to admins!
                context = {
                    "info": info,
                }
                msg_plain = render_to_string("core/mail/newproject.txt", context)
                send_mail(
                    "New project added: " + info.name,
                    msg_plain,
                    settings.SITE_EMAIL,
                    [settings.SITE_EMAIL],
                )

            else:
                edit_record = get_object_or_404(UserAction, pk=2)
                log = UserLog(user=request.user, action=edit_record, model="Research", points=1, description=info.name)

            messages.success(request, "We have received your submitted. We will review your project and activate it shortly if it is relevant to the website. Thanks!")
            return redirect("core:project", id=info.id, type=info.type)
        else:
            messages.error(request, "We could not save your form, please correct the errors")

    context = { "section": "community", "page": "research", "info": info, "form": form }
    return render(request, "core/project.form.html", context)


def reference_search_ajax(request, active_only=False):
    list = []
    if "term" in request.GET:
        if active_only:
            references = Reference.objects.filter(title__icontains=request.GET["term"],status="active").order_by("title")
        else:
            references = Reference.objects.filter(title__icontains=request.GET["term"]).order_by("title")
        for details in references:
            d = {}
            d["text"] = details.title + " (" + str(details.year) + ")"
            d["id"] = details.id
            list.append(d)
    return JsonResponse(list, safe=False)

def reference_list_ajax(request):
    list = Reference.objects.filter(tags=request.GET["id"],status="active")
    reference_types = list.values("type__name").order_by("type__name").distinct()
    list = list.order_by("title")
    context = { "references": list, "show_quantity": True, "reference_types": reference_types }
    return render(request, "core/includes/references.list.html", context)

def register(request, contributor=False, taskforce=False):

    if taskforce:
        taskforce = get_object_or_404(Category, slug=taskforce)

    if request.method == "POST":
        user = User.objects.filter(email=request.POST["email"])
        if user:
            user = user[0]
            people = get_object_or_404(People, user=user)
        else:
            if "password" not in request.POST:
                import uuid
                password = str(uuid.uuid4())
            else:
                password = request.POST["password"]
            user = User.objects.create_user(request.POST["email"], request.POST["email"], password)
            user.first_name = request.POST["first_name"]
            user.last_name = request.POST["last_name"]
            user.is_active = False
            user.save()
            people = People.objects.create(
                firstname = request.POST["first_name"],
                lastname = request.POST["last_name"],
                email = request.POST["email"],
                email_public = False,
                user = user,
                description = request.POST["profile"],
                status = "pending",
            )

        PeopleNote.objects.create(
            people = people,
            created_by = user,
            note = request.POST["contribution"],
        )

        current_site = Site.objects.get_current()
        scheme = request.scheme
        url = scheme + "://" + current_site.domain

        context = {
            "url": url + reverse("core:admin_people", args=[people.id]),
            "profile": request.POST["profile"],
            "contribution": request.POST["contribution"],
            "user": user,
            "site": current_site.name,
            "taskforce": taskforce,
        }

        if contributor:
            subject = "Data contributor signup"
        elif taskforce:
            subject = taskforce.name + " task force signup"
        else:
            subject = "New team member signup"

        msg_html = render_to_string("team/mail/newaccount.html", context)
        msg_plain = render_to_string("team/mail/newaccount.txt", context)

        send_mail(
            subject + " - " + people.firstname + " " + people.lastname,
            msg_plain,
            settings.SITE_EMAIL,
            [settings.SITE_EMAIL],
            html_message=msg_html,
        )

        if user.is_active:
            login(request, user)
            messages.success(request, "Welcome " + request.POST["first_name"] + "! You are now a registered user.")
        else:
            messages.success(request, "Thanks " + request.POST["first_name"] + "! We have received your submission and we will reach out soon to follow up on this.")
        if taskforce:
            return redirect(reverse("core:taskforce", args=[taskforce.slug]))
        else:
            return redirect("/about/join")
    context = { "taskforce": taskforce, "contributor": contributor }
    if contributor or taskforce or True:
        return render(request, "registration/contributor.html", context)
    else:
        return render(request, "registration/register.html")

def tag_ajax(request):
    if request.GET.get("parent"):
        tags = Tag.objects.filter(parent_tag=request.GET["parent"]).order_by("name")
    else:
        tags = Tag.objects.filter(parent_tag__isnull=True).order_by("name")
    list = []
    for details in tags:
        d = {}
        d["title"] = details.name
        d["lazy"] = True
        d["key"] = details.id
        list.append(d)
    return JsonResponse(list, safe=False)

def tag_ajax_folder(request):
    if request.GET.get("id"):
        tags = Tag.objects.filter(parent_tag=request.GET["id"], hidden=False).order_by("name")
        tag = get_object_or_404(Tag, pk=request.GET["id"])
    else:
        tags = Tag.objects.filter(parent_tag__isnull=True, hidden=False).order_by("name")
        tag = None
    context = { "list": tags, "tag": tag }
    return render(request, "core/includes/tags.folder.html", context)

def set_theme(request, theme):
    response = redirect(request.GET["next"])
    response.set_cookie("theme", theme, 60*60*25*365)
    return response

# Admin section

@staff_member_required
def admin_people_list(request):
    list = People.objects.all()
    context = { "navbar": "backend", "list": list, "datatables": True }
    return render(request, "core/admin/people.list.html", context)

@staff_member_required
def admin_member_list(request):
    list = People.on_site.filter(user__isnull=False)
    context = { "navbar": "backend", "list": list, "datatables": True, "volunteers": True }
    return render(request, "core/admin/people.list.html", context)

@staff_member_required
def admin_people(request, id=False):
    if id:
        info = get_object_or_404(People, pk=id)
        form = PeopleForm(instance=info)
    else:
        info = False
        form = PeopleForm()
    list = People.objects.filter(status="active")
    if request.method == "POST":
        if "merge" in request.POST:
            error = False
            old = info
            new = get_object_or_404(People, pk=request.POST["merge"])
            PeopleNote.objects.filter(people=old).update(people=new)
            PeopleAffiliation.objects.filter(people=old).update(people=new)

            # We will reassign the existing publications.
            ReferenceAuthor = Reference.authors.through
            try:
                ReferenceAuthor.objects.filter(people=old).update(people=new)
            except:
                messages.error(request, "Could not reassign publications because some publications are already assigned to the new person -- please check and retry")
                error = True

            # Same with articles
            ArticleAuthor = Article.authors.through
            try:
                ArticleAuthor.objects.filter(people=old).update(people=new)
            except:
                messages.error(request, "Could not reassign article because some articles are already assigned to the new person -- please check and retry")
                error = True

            # Videos
            VideoPeople = Video.people.through
            try:
                VideoPeople.objects.filter(people=old).update(people=new)
            except:
                messages.error(request, "Could not reassign videos because some videos are already assigned to the new person -- please check and retry")
                error = True

            if not error:
                old.delete()
                messages.success(request, "Records have been merged and old record was deleted.")
                return redirect("core:admin_people_list")

        else:
            if not id:
                form = PeopleForm(request.POST, request.FILES)
            else:
                form = PeopleForm(request.POST, request.FILES, instance=info)
            if form.is_valid():
                info = form.save()
                messages.success(request, "Information was saved.")
                return redirect(reverse("core:admin_people", args=[info.id]))
            else:
                messages.error(request, "We could not save your form, please correct the errors")
    context = { "navbar": "backend", "form": form, "info": info, "list": list, "select2": True }
    return render(request, "core/admin/people.html", context)

@staff_member_required
def admin_project(request, id=False):
    if id:
        info = get_object_or_404(Project, pk=id)
        form = ProjectForm(instance=info)
    else:
        info = False
        form = ProjectForm()
    if request.method == "POST":
        if not id:
            form = ProjectForm(request.POST)
        else:
            form = ProjectForm(request.POST, instance=info)
        if form.is_valid():
            info = form.save(commit=False)
            info.site = request.site
            info.save()

            info.references.clear()
            selected = request.POST.getlist("references")
            for reference in selected:
                info.references.add(Reference.objects.get(pk=reference))

            messages.success(request, "Information was saved.")
            return redirect(reverse("core:project", args=[info.id]))
        else:
            messages.error(request, "We could not save your form, please correct the errors")
    context = { "navbar": "backend", "form": form, "info": info, "tinymce": True, "select2": True }
    return render(request, "core/admin/project.html", context)

@staff_member_required
def admin_project_list(request, status="published"):
    if status == "published":
        list = Project.on_site.filter(active=True, pending_review=False)
    elif status == "deleted":
        list = Project.on_site.filter(active=False, pending_review=False)
    elif status == "pending":
        list = Project.on_site.filter(pending_review=True)

    context = { "navbar": "backend", "list": list, "datatables": True, "tab": status }
    return render(request, "core/admin/project.list.html", context)

@staff_member_required
def admin_tag_list(request):
    list = Tag.objects.filter(parent_tag__isnull=True, hidden=False)
    context = { "navbar": "backend", "list": list, "datatables": True }
    return render(request, "core/admin/tag.list.html", context)

@staff_member_required
def admin_tag(request, id=False, parent=False):
    if id:
        info = get_object_or_404(Tag, pk=id)
        form = TagForm(instance=info)
    else:
        info = False
        if parent:
            form = TagForm(initial={"parent_tag": parent})
        else:
            form = TagForm()

    if request.method == "POST":
        if not id:
            form = TagForm(request.POST, request.FILES)
        else:
            form = TagForm(request.POST, request.FILES, instance=info)
        if form.is_valid():
            info = form.save(commit=False)
            if not id:
                info.site = request.site
            info.save()
            messages.success(request, "Information was saved.")
            return redirect(reverse("core:admin_tag_list"))
        else:
            messages.error(request, "We could not save your form, please correct the errors")
    context = { "navbar": "backend", "form": form, "info": info, "select2": True }
    return render(request, "core/admin/tag.html", context)


@staff_member_required
def admin_video_list(request):
    list = Video.on_site.all()
    context = { "navbar": "backend", "list": list, "datatables": True }
    return render(request, "core/admin/videos.list.html", context)

@staff_member_required
def admin_video(request, id=False):
    if id:
        info = get_object_or_404(Video, pk=id)
        form = VideoForm(instance=info)
    else:
        info = False
        form = VideoForm()
    if request.method == "POST":
        if not id:
            form = VideoForm(request.POST, request.FILES)
        else:
            form = VideoForm(request.POST, request.FILES, instance=info)
        if form.is_valid():
            info = form.save(commit=False)
            if not id:
                info.site = request.site
            info.save()
            form.save_m2m()
            messages.success(request, "Information was saved.")
            return redirect(reverse("core:video", args=[info.id]))
        else:
            messages.error(request, "We could not save your form, please correct the errors")
    context = { "navbar": "backend", "form": form, "info": info, "select2": True }
    return render(request, "core/admin/video.html", context)


@staff_member_required
def admin_videocollections(request):
    list = VideoCollection.on_site.all()
    context = { "navbar": "backend", "list": list, "datatables": True }
    return render(request, "core/admin/videocollections.html", context)

@staff_member_required
def admin_videocollection(request, id=False):
    if id:
        info = get_object_or_404(VideoCollection, pk=id)
        form = VideoCollectionForm(instance=info)
    else:
        info = False
        form = VideoCollectionForm()
    if request.method == "POST":
        if not id:
            form = VideoCollectionForm(request.POST)
        else:
            form = VideoCollectionForm(request.POST, instance=info)
        if form.is_valid():
            info = form.save(commit=False)
            if not id:
                info.site = request.site
            info.save()
            messages.success(request, "Information was saved.")
            return redirect(reverse("core:admin_videocollections"))
        else:
            messages.error(request, "We could not save your form, please correct the errors")
    context = { "navbar": "backend", "form": form, "info": info }
    return render(request, "core/admin/videocollection.html", context)


@staff_member_required
def admin_organization_list(request):
    list = Organization.on_site.all()
    context = { "navbar": "backend", "list": list, "datatables": True }
    return render(request, "core/admin/organizations.list.html", context)

@staff_member_required
def admin_organization(request, id=False, slug=False):
    space = False
    if slug:
        space = get_object_or_404(ReferenceSpace, slug=slug)
    if id:
        info = get_object_or_404(Organization, pk=id)
        form = OrganizationForm(instance=info)
    else:
        info = False
        form = OrganizationForm()
    if request.method == "POST":
        if not id:
            form = OrganizationForm(request.POST, request.FILES)
        else:
            form = OrganizationForm(request.POST, request.FILES, instance=info)
        if form.is_valid():
            info = form.save()
            if id:
                info.processes.clear()

            selected = request.POST.getlist("process")
            for process in selected:
                info.processes.add(Process.objects.get(pk=process))

            messages.success(request, "Information was saved.")
            return redirect(reverse("core:admin_organization", args=[info.id]))
        else:
            messages.error(request, "We could not save your form, please correct the errors")
    processes = Process.objects.filter(slug__isnull=False).order_by("id")
    context = { "navbar": "backend", "form": form, "info": info, "select2": True, "space": space, "processes": processes }
    return render(request, "core/admin/organization.html", context)


@staff_member_required
def admin_article(request, id=False, type=False, parent=False):
    eventform = False
    if parent:
        id = False
        parent = get_object_or_404(Article, pk=parent)
        if parent.title == "Events":
            type = "event"
    if id:
        info = get_object_or_404(Article, pk=id)
        form = SimpleArticleForm(instance=info)
        if hasattr(info, "event"):
            eventform = EventForm(instance=info.event)
            type = "event"
    else:
        info = False
        form = SimpleArticleForm()
        if type == "event":
            eventform = EventForm()
    if request.method == "POST":
        if not id:
            form = SimpleArticleForm(request.POST)
            if type == "event":
                eventform = EventForm(request.POST)
        else:
            form = SimpleArticleForm(request.POST, instance=info)
            if type == "event":
                eventform = EventForm(request.POST, instance=info.event)
        if (form.is_valid() and eventform and eventform.is_valid()) or (form.is_valid() and not eventform):
            info = form.save(commit=False)
            if parent:
                info.parent = parent
            info.site = request.site
            info.save()

            if type == "event":
                event = eventform.save(commit=False)
                event.article = info
                event.save()

            saved = True
            messages.success(request, "Information was saved.")
            redirect = request.POST.get("redirect", "/")
            return HttpResponseRedirect(redirect)
        else:
            messages.warning(request, "We could not save your form, please correct the errors")

    context = { "navbar": "backend", "form": form, "info": info, "eventform": eventform, "parent": parent, "tinymce": True}
    return render(request, "core/admin/article.html", context)

@staff_member_required
def admin_references(request):
    list = Reference.objects.all()
    context = { "navbar": "backend", "list": list, "datatables": True }
    return render(request, "core/admin/references.list.html", context)

