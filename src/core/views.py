from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Journal, Organization, Publisher, Reference, ReferenceForm, ReferenceFormAdmin, People, Article, PeopleForm, Video, VideoForm, ReferenceOrganization, Project, UserAction, UserLog, SimpleArticleForm, ProjectForm, ProjectUserForm, EventForm, ReferenceType, Tag, Event, TagForm, OrganizationForm, VideoCollection, VideoCollectionForm, PeopleNote, ReferenceAuthors, DataViz, NewsletterSubscriber, Method
from team.models import Category, TaskForceMember, TaskForceTicket, TaskForceUnit
from multiplicity.models import ReferenceSpace, ReferenceSpaceCSV
from staf.models import Data, Process, Material, CSV
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
        list = Video.objects.filter(collections=collection).order_by('title')
    addlink = "/admin/videos/create"
    context = { "section": "resources", "collection": collection, "addlink": addlink,
    "collections": collections, "list": list, "editlink": editlink, 'all': all }
    return render(request, "core/videos.html", context)

def video(request, id):
    info = get_object_or_404(Video, pk=id)
    editlink = ""+str(id) + "/change/"
    editlink = reverse("core:admin_video", args=[id])
    download = False
    download_videos = [34,35,37,38,39,40,41,42,43]
    if id in download_videos:
        download = True

    context = { "section": "resources", "page": "video", "info": info, "editlink": editlink, "download": download }
    return render(request, "core/video.html", context)

def search(request):
    context = { "section": "resources", "page": ""  }
    return render(request, "core/search.html", context)

def home(request):
    context = { "section": "home", "page": ""  }
    return render(request, "core/home.html", context)

def glossary(request):
    list = Tag.objects.filter(include_in_glossary=True, description__isnull=False).order_by("name")
    context = { "section": "resources", "page": "glossary", "list": list  }
    return render(request, "core/glossary.html", context)

def index(request):
    if request.site.id == 1:
        main_filter = 11 # This is urban systems
        context = { "section": "home", "page": ""  }
    else:
        main_filter = 219
        context = { "section": "home", "page": ""  }
    return render(request, "core/home.html", context)
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
        pages = [68, 125, 65, 88, 87, 75, 111, 77, 201, 69]
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
    if request.site.id == 1:
        page = Article.objects.get(pk=39)
        list = People.objects.exclude(member_since__isnull=True).exclude(site__id=2).order_by("member_since")
    else:
        page = Article.objects.get(pk=192)
        ids = [1150,282,186,934,926,95,1165,927,1209,1169,1228,1307]
        list = People.objects.filter(pk__in=ids).order_by("-firstname")
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
    context = { 
        "section": "about", 
        "page": "taskforces", 
        "info": info, 
        "tickets": tickets, 
        "units": units, 
        "taskforces": taskforces,
    }
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
    site = Site.objects.get_current()
    context = {
        "name": name,
        "email": email,
        "organization": organization,
        "message": message
    }

    message = render_to_string("core/mail/contactform.txt", context)

    send_mail(
        "Contact form " + site.name + " (" + name + ")",
        message,
        settings.SITE_EMAIL,
        [settings.SITE_EMAIL],
    )
    messages.success(request, "Thanks, we have received your message!")
    return redirect("core:contact")


@csrf_exempt
def subscribe(request):
    check = People.objects.filter(email=request.POST["email"])
    if check:
        person = check[0]
    else:
        person = People.objects.create(
            firstname = request.POST["firstname"],
            lastname = request.POST["lastname"],
            affiliation = request.POST["organization"],
            email = request.POST["email"],
            email_public = False,
        )

    d = n = e = p = m = pr = t = False
    if "datasets" in request.POST and request.POST["datasets"]:
        d = True
    if "news" in request.POST and request.POST["news"]:
        n = True
    if "events" in request.POST and request.POST["events"]:
        e = True
    if "publications" in request.POST and request.POST["publications"]:
        p = True
    if "multimedia" in request.POST and request.POST["multimedia"]:
        m = True
    if "projects" in request.POST and request.POST["projects"]:
        pr = True
    if "theses" in request.POST and request.POST["theses"]:
        t = True

    NewsletterSubscriber.objects.create(
        people = person,
        datasets = d,
        news = n,
        events = e,
        publications = p,
        multimedia = m,
        projects = pr,
        theses = t,
        dataviz = False,
    )

    name = request.POST["firstname"] + " " + request.POST["lastname"]
    email = request.POST["email"]
    organization = request.POST["organization"]
    site = Site.objects.get_current()
    context = {
        "name": name,
        "email": email,
        "organization": organization,
    }

    message = render_to_string("core/mail/subscriber.txt", context)

    send_mail(
        "New subscriber " + site.name + " (" + name + ")",
        message,
        settings.SITE_EMAIL,
        [settings.SITE_EMAIL],
    )
    messages.success(request, "Thanks, you have signed up to our newsletter.")
    return redirect("core:subscribe")

def sectionpage(request, id=None, slug=None):
    if id:
        info = get_object_or_404(Article, pk=id)
    elif slug:
        info = Article.objects.filter(slug=slug)
        if info.count() > 1:
            info = info.filter(site=Site.objects.get_current())
            info = info[0]
        elif info.count() == 1:
            info = info[0]
        else:
            raise Http404("We could not find this page.")
    editlink = "/admin/core/article/"+str(info.id) + "/change/"
    list = Article.objects.filter(active=True, parent=info.parent).order_by("created_at")
    context = { 
        "section": "markcities", 
        "page": info.slug, 
        "info": info, 
        "editlink": editlink, 
        "list": list, 
        "datatables": True,
    }
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
    list = Article.objects.filter(active=True, parent=info.parent).order_by("-date", "-created_at")[:8]
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
    addlink = reverse("core:admin_article_parent", args=[parent]) + "?ref=" + request.path
    context = { "section": section, "page": page, "list": list, "addlink": addlink, "years": years }
    return render(request, "core/news.html", context)

def news_and_events(request):
    match = { 1: 59, 2: 143 }
    events = match[request.site.id]
    match = { 1: 61, 2: 142 }
    news = match[request.site.id]
    news_list = Article.objects.filter(active=True, parent__id=news, site=request.site).order_by("-date")
    events_list = Event.objects.filter(article__active=True, article__site=request.site).order_by("-start")
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

    if info.status != "active":
        if not request.user.is_staff:
            from django.http import Http404
            raise Http404("This record does not exist.")

    related = Reference.objects.filter(status="active", tags__id=main_filter).order_by("-id")[:5]
    authors = info.authors.all()
    data = Data.objects.filter(dataset__references=info)
    editlink = reverse("core:admin_reference", args=[info.id])
    context = { "section": "literature", "page": "publications", "info": info, "related": related, "authors": authors, "editlink": editlink, "data": data, "datatables": True }
    return render(request, "core/reference.html", context)

def referenceform(request, id=False, dataset=False):
    
    new_record = False
    if request.site.id == 1:
        main_filter = 11 # This is urban systems
    else:
        main_filter = 219

    if id and request.user.is_staff:
        info = get_object_or_404(Reference, pk=id)
        if request.user.is_staff:
            form = ReferenceFormAdmin(instance=info)
        else:
            form = ReferenceForm(instance=info)
    else:
        info = False
        if request.user.is_staff:
            initial={"language": "EN", "status": "active", "tags": main_filter}
        else:
            initial = {}
        if request.method == "POST" and "bibtex" in request.POST:
            bibtex = request.POST["bibtex"]
            lines = bibtex.splitlines()
            for line in lines:
                s = line.strip()
                if s and s[0] == "@":
                    type_id = None
                    value = s[s.find("@")+1:s.find("{")]
                    if value == "article":
                        type_id = 16
                    elif value == "report":
                        type_id = 27
                    elif value == "book":
                        type_id = 5
                    elif value == "thesis":
                        type_id = 29
                    if type_id:
                        initial["type"] = ReferenceType.objects.get(pk=type_id)
                location_equal = s.find("=")
                if location_equal:
                    label = s[0:location_equal]
                    label = label.strip()
                    value = s[s.find("{")+1:s.find("}")]
                    if label == "title":
                        initial["title"] = value
                    elif label == "author":
                        initial["authorlist"] = value
                    elif label == "journal":
                        find = Journal.objects.filter(name=value)
                        if find:
                            initial["journal"] = find[0]
                    elif label == "year":
                        initial["year"] = value
                    elif label == "abstract":
                        initial["abstract"] = value
                    elif label == "doi":
                        initial["doi"] = value
            messages.warning(request, "The form has been loaded with the BibTeX information, please review and complete the form below.")
        if request.user.is_staff:
            form = ReferenceFormAdmin(initial=initial)
        else:
            form = ReferenceForm(initial=initial)
    if request.method == "POST" and not "bibtex" in request.POST:
        title = request.POST["title"]
        title = title.strip()
        error = False
        if not id:
            new_record = True
            if request.user.is_staff:
                form = ReferenceFormAdmin(request.POST, request.FILES)
            else:
                form = ReferenceForm(request.POST)
            check = Reference.objects.filter(title=title)
            if check:
                messages.error(request, "This publication already exists in our library. If you can not yet locate it, it may still be under review. We can not add a duplicate publication. Please contact us if you have any questions")
                error = True
        else:
            if request.user.is_staff:
                form = ReferenceFormAdmin(request.POST, request.FILES, instance=info)
            else:
                form = ReferenceForm(request.POST, instance=info)
        
        if not error and form.is_valid():
            info = form.save()
            if new_record:
                create_record = get_object_or_404(UserAction, pk=1)
                if request.user.is_authenticated:
                    log = UserLog(user=request.user, action=create_record, reference=info, points=5)
                else:
                    info.status = "pending"
                    info.save()

                # Send mail to notify team that a new record was added.
                if request.user.is_authenticated:
                    name = request.user.username
                    email = request.user.email
                else:
                    name = request.POST["name"]
                    email = request.POST["email"]
                context = {
                    "name": name,
                    "email": email,
                    "title": title,
                    "link": reverse("core:editreference", args=[info.id]),
                    "domain": Site.objects.get_current().domain,
                }

                message = render_to_string("core/mail/referenceform.txt", context)

                send_mail(
                    "Publication added to Metabolism of Cities (" + title + ")",
                    message,
                    settings.SITE_EMAIL,
                    [settings.SITE_EMAIL],
                )

            if request.user.is_authenticated:
                if "cityloops" in request.POST:
                    info.cityloops = True
                    info.save()
                    return redirect(reverse("core:editreference_tags", args=[info.id]) + "?analyze=true")
                else:
                    messages.success(request, "Information was saved.")
                    return redirect("core:reference", id=info.id)
            else:
                messages.success(request, "Thanks, the record has been added! Our team will review this and notify you when it has been activated. Use the form below if you would like to add another record.")
                return redirect("core:newreference")

        else:
            messages.error(request, "We could not save your form, please correct the errors")

    context = { 
        "section": "resources", 
        "page": Article.objects.get(pk=213),
        "info": info, 
        "form": form, 
        "dataset": dataset,
    }
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
        if "cityloops_comments" in request.POST:
            info.cityloops_comments = request.POST["cityloops_comments"]
            info.save()
        if "spaces" in request.POST:
            info.spaces.clear()
            selected = request.POST.getlist("spaces")
            for spaces in selected:
                info.spaces.add(ReferenceSpace.objects.get(pk=spaces))
        else:
            return redirect("core:editreference_multiplicity", id=info.id)
    case_sensitive = ''
    case_insensitive = ''
    if "analyze" in request.GET:
        import PyPDF2
        tags = Tag.objects.filter(parent_tag__id=318)
        list = ["methodology", "methodologies"]
        for details in tags:
            name = details.name
            for char in "&,.!;:-/\\":
                name = name.replace(char,'').replace(" ", "")
            s = name
            location = s.find("(")
            if location > 0:
                name = s[0:location]
                abbreviation = s[s.find("(")+1:s.find(")")]
                list.append(abbreviation)
            list.append(name)
        file = info.file
        if file:

            pdfFileObj = open(file.path,'rb')
            pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
            num_pages = pdfReader.numPages
            count = 0
            text = ""#The while loop will read each page
            while count < num_pages:
                pageObj = pdfReader.getPage(count)
                count +=1
                text += pageObj.extractText()
            for char in "&,.!;:-/\\":
                text = text.replace(char,'')
            text = text.replace(" ", "")
            text = text.replace("\n", "").replace("\r", "").replace("ß", "fl")
            case_sensitive = ''
            case_insensitive = ''
            for method in list:
                location = text.find(method)
                if location > 0:
                    blurb = text[location-100:location+100] + "<br>"
                    case_sensitive += "<li>" + blurb.replace(method, '<span class="highlight">' + method + '</span>') + "</li>"
            lower = text.lower()
            for method in list:
                method = method.lower()
                location = lower.find(method)
                if location > 0:
                    blurb = text[location-100:location+100] + "<br>"
                    case_insensitive += "<li>" + blurb.replace(method, '<span class="highlight">' + method + '</span>') + "</li>"
    if request.site.id == 1:
        tags = Tag.objects.filter(parent_tag__isnull=False)
    else:
        tags = Tag.objects.filter(hidden=False, parent_tag__isnull=False)
    context = { 
        "navbar": "backend", 
        "tags": tags,
        "info": info, 
        "parent_tags": Tag.objects.filter(parent_tag__isnull=True, hidden=False), 
        "select2": True,
        "case_sensitive": case_sensitive,
        "case_insensitive": case_insensitive,
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



def references(request, type=False, tag=False, all=False):

    if "reshuffle" in request.GET:
        ids = [16, 5, 6, 19]
        list = ReferenceType.objects.filter(id__in=ids)
        list.update(group="academic")

        ids = [29]
        list = ReferenceType.objects.filter(id__in=ids)
        list.update(group="theses")

        ids = [27,11]
        list = ReferenceType.objects.filter(id__in=ids)
        list.update(group="reports")

        ids = [25,12,31,33,30, 24, 26, 2, 15]
        list = ReferenceType.objects.filter(id__in=ids)
        list.update(group="multimedia")

    if request.site.id == 1:
        main_filter = 11 # This is urban systems
        article_id = 75
        type_id = 3 # The ID of reference type = city
    else:
        main_filter = 219 # Island system
        article_id = 200
        type_id = 21 # The ID of reference type = island
    if type:
        type = get_object_or_404(ReferenceType, pk=type)
        list = Reference.objects.filter(status="active", type=type, tags__id=main_filter).order_by("-year")
        title = type.name + "s"
    else:
        if tag:
            list = Reference.objects.filter(status="active", tags__id=tag).order_by("-year")
            tag = get_object_or_404(Tag, pk=tag)
            if tag.hidden:
                tag = Tag.objects.filter(name=tag.name, hidden=False)
                if tag:
                    tag = tag[0]
                else:
                    return redirect("core:references")
            title = tag.name + " | Library"
        elif all:
            list = Reference.objects.filter(status="active").order_by("-year")
            title = "Entire library"
        else:
            list = Reference.objects.filter(status="active", tags__id=main_filter).order_by("-year")
            title = "Library"
    maintags = Tag.objects.filter(parent_tag__isnull=True, hidden=False)
    addlink = reverse("core:newreference")

    cities_list = Reference.objects.filter(status="active", tags__id=main_filter, spaces__type__id=type_id).prefetch_related('spaces')
    show = cities_list.all().query
    cities = defaultdict(dict)
    cities_references = {}

    if not tag:
        # TODO
        # We can improve this a lot
        for details in cities_list:
            for sub in details.spaces.all():
                if sub.type.id == type_id:
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
        "main_filter": Tag.objects.get(pk=main_filter),
        "title": title, 
        "select2": True, 
        "tag": tag, 
        "maintags": maintags, 
        "page": get_object_or_404(Article, pk=article_id),
        "methodologies": Tag.objects.filter(parent_tag__id=318, hidden=False),
        "cities": cities,
        "cities_references": cities_references,
        "all": all,
    }
    return render(request, "core/references.list.html", context)

def case_studies(request):
    list = Reference.objects.all()

    if request.site.id == 1:
        main_filter = 11 # This is urban systems
        article_id = 224
        type_id = 3 # The ID of reference type = city
    else:
        main_filter = 219 # Island system
        article_id = 200
        type_id = 21 # The ID of reference type = island
    list = Reference.objects.filter(status="active", tags__id=main_filter).filter(tags__id=1).order_by("-year").prefetch_related("tags").prefetch_related("spaces")

    context = { 
        "section": "resources",
        "list": list, 
        "title": "Case studies", 
        "page": get_object_or_404(Article, pk=article_id),
        "methodologies": Tag.objects.filter(parent_tag__id=318, hidden=False),
        "type_id": type_id,
        "datatables": True,
    }
    return render(request, "core/references.casestudies.html", context)

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
            form.save_m2m()

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

def datavisualizations(request):
    context = {
        "list": DataViz.objects.all(),
        "page": get_object_or_404(Article, pk=201),
    }
    return render(request, "core/dataviz.list.html", context)

def datavisualization(request, id):
    context = {
        "info": get_object_or_404(DataViz, pk=id),
    }
    return render(request, "core/dataviz.html", context)

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
        url = current_site.domain

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

def methodologies(request):
    list = Method.objects.all()
    context = {
        "list": list,
    }
    return render(request, "core/methodologies.html", context)
# Admin section

@staff_member_required
def admin_people_list(request):
    list = People.objects.all()
    context = { "navbar": "backend", "list": list, "datatables": True }
    return render(request, "core/admin/people.list.html", context)

@staff_member_required
def admin_member_list(request):
    list = People.on_site.filter(user__isnull=False)
    context = { 
        "navbar": "backend", 
        "list": list, 
        "datatables": True, 
        "volunteers": True,
    }
    return render(request, "core/admin/people.list.html", context)

@staff_member_required
def admin_member_profile(request, id):
    info = People.on_site.get(pk=id)
    csv = CSV.objects.filter(user=info.user)
    space_csv = ReferenceSpaceCSV.objects.filter(user=info.user)
    context = { 
        "navbar": "backend", 
        "info": info, 
        "datatables": True, 
        "volunteers": True,
        "log": UserLog.objects.filter(user=info.user),
        "csv": csv, 
        "space_csv": space_csv, 
    }
    return render(request, "core/admin/people.profile.html", context)

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
            form = ProjectForm(request.POST, request.FILES)
        else:
            form = ProjectForm(request.POST, request.FILES, instance=info)
        if form.is_valid():
            info = form.save(commit=False)
            info.site = request.site
            info.save()
            form.save_m2m()

            info.references.clear()
            selected = request.POST.getlist("references")
            for reference in selected:
                info.references.add(Reference.objects.get(pk=reference))

            messages.success(request, "Information was saved.")
            return redirect(info.get_absolute_url())
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
    elif status == "cityloops":
        list = Project.on_site.filter(Q(cityloops="pending")|Q(cityloops="yes"))
    context = { "navbar": "backend", "list": list, "datatables": True, "tab": status }
    return render(request, "core/admin/project.list.html", context)

@staff_member_required
def admin_tag_list(request, method=False):
    if "hidden" in request.GET:
        list = Tag.objects.filter(parent_tag__isnull=True)
    else:
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
def admin_method_list(request):
    list = Tag.objects.filter(parent_tag__id=318)
    context = { "navbar": "backend", "list": list, "datatables": True }
    return render(request, "core/admin/method.list.html", context)

@staff_member_required
def admin_method(request, id=False):

    from django.forms import modelform_factory
    ModelForm = modelform_factory(Method, exclude={})
    if id:
        info = get_object_or_404(Method, pk=id)
        form = ModelForm(request.POST or None, instance=info)
    else:
        form = ModelForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Information was saved.")
            return redirect(reverse("core:admin_method_list"))
        else:
            messages.error(request, "We could not save your form, please fill out all fields")

    context = { "navbar": "backend", "form": form, "form": form, "select2": True }
    return render(request, "core/admin/method.html", context)

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
    list = Organization.objects.all()
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
            form = SimpleArticleForm(request.POST, request.FILES)
            if type == "event":
                eventform = EventForm(request.POST)
        else:
            form = SimpleArticleForm(request.POST, request.FILES, instance=info)
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
    site = Site.objects.get_current()
    # Temporary
    # CityLoops
    # Take out national
    if "cityloops" in request.GET:
        list = list.filter(cityloops=True)
    elif "casestudies" in request.GET:
        list = list.exclude(tags__name="National").exclude(tags__name="Global").filter(tags__id=1)
    elif "zotero" in request.GET:
        list = list.filter(tags__id=705)
    elif "review" in request.GET:
        list = list.filter(tags__id=706)
    elif site.id == 1:
        list = list.exclude(tags__name="National").exclude(tags__name="Global")
    
    context = { 
        "navbar": "backend", 
        "list": list, 
        "datatables": True,
    }
    return render(request, "core/admin/references.list.html", context)

def findReference(title, doi=None):
    title = title.strip()
    # DOI is the most unique, so if present, use that
    if doi:
        list = Reference.objects.filter(doi=doi)
        if list.count() == 1:
            return list[0]
        elif list.count() > 1:
            list = list.filter(status="active")
            if list.count() == 1:
                return list[0]
    # Let's try the title instead
    list = Reference.objects.filter(title=title)
    if list.count() == 1:
        return list[0]
    elif list.count() > 1:
        list = list.filter(status="active")
        if list.count() == 1:
            return list[0]
    # Let's try the first 20 chars of the title (still unique enough but less chances of misspelling etc)
    list = Reference.objects.filter(title__icontains=title[0:20])
    if list.count() == 1:
        return list[0]
    elif list.count() > 1:
        list = list.filter(status="active")
        if list.count() == 1:
            return list[0]
    return False

def zotero_import(request):
    import requests
    from django.conf import settings
    url = "https://api.zotero.org/groups/2381279/items?limit=5"
    headers = {
        "Zotero-API-Version": "3",
        "Zotero-API-Key": settings.ZOTERO_API,
    }
    try:
        info = requests.get(url, headers=headers)
        if info.status_code == 200:
            results = info.json()
            print(results)
            count = 0
            total_results = info.headers["Total-Results"]
            link = info.headers["Link"]
            print(link)
            print("TOTAL: " + str(total_results))
            print("-----------------")
            for details in results:
                count += 1
                #print(details)
                data = details["data"]
                if "title" in data:
                    if data["itemType"] != "attachment":
                        print(data.get("title"))
                        print(data.get("itemType"))
                        print(data.get("abstractNote"))
                        print(data.get("publicationTitle"))
                        print(data.get("DOI"))
                        print(data.get("url"))
                        print(data.get("creators"))
                        print(data.get("tags"))
            print("TOTAL: " + str(count))
        else:
            print("Status code not 200!")
            print("Will not proceed")
            print(info.status_code)
    except Exception as e:
        print("Error!")
        print(e)
    return HttpResponse("All good")

# TEMPORARY IMPORT SCRIPTS FOR CITYLOOPS

def temp_import_projects(request):
    import datetime
    list = Project.objects.filter(cityloops="pending", status='ongoing', end_date__lte=datetime.date.today())
    for details in list:
        details.status = 'finished'
        details.save()
    return HttpResponse("All good")

    # Delete after Jan 1, 2020
    import codecs
    import csv
    from multiplicity.models import ReferenceSpaceType
    #path = settings.MEDIA_ROOT + "/projects.csv"
    f = codecs.open(path, encoding="utf-8", errors="strict")
    reader = csv.reader(f)
    count = 0
    for row in reader:
        count += 1
        if count > 3:
            funder = row[0]
            shortname = row[1]
            check = Project.objects.filter(Q(name=row[1])|Q(name=row[5]))
            try:
                budget = Decimal(row[23] * 1)
            except:
                budget = None
            site = Site.objects.get_current()
            if check:
                info = check[0]
            else:
                info = Project.objects.create(
                    name = row[1],
                    full_name = row[5],
                    email = row[9],
                    start_date = row[3],
                    end_date = row[4],
                    type = 'projects',
                    url = row[2],
                    site = site,
                )
            info.budget = budget
            info.cityloops = 'pending'
            info.output_tools = row[11]
            info.output_reports = row[12]
            info.output_articles = row[13]
            info.funding_program = row[0]
            info.methodologies = row[14]
            info.material_temp_notes = row[7]
            info.supervisor = row[8]
            if not info.description:
                info.description = row[25]
            info.internal_notes = 'Aim: \n' + row[6] + '\n\nData: \n' + row[15] + '\n\nComments:\n' + row[16] + '\n\nRelevance:\n' + row[17]
            info.save()

            city_type = ReferenceSpaceType.objects.get(pk=3)
            if row[19]:
                cities = row[19]
                all = cities.split(";")
                for details in all:
                    details = details.strip()
                    if details:
                        s = details.split(",")
                        country = s[1].strip()
                        if country == "UK":
                            country = "United Kingdom"
                        if country == "USA":
                            country = "United States of America"
                        city = s[0].strip()
                        search = ReferenceSpace.objects.filter(name=country)
                        if search.count() > 1:
                            print("More than one for " + country)
                        elif not search:
                            print("Did not find " + country)
                        country = search[0]
                        search = ReferenceSpace.objects.filter(name=city)
                        if search.count() > 1:
                            print("More than one for " + city)
                        elif not search:
                            print("Did not find " + city)
                            city = ReferenceSpace.objects.create(
                                name = city,
                                country = country,
                                type = city_type,
                                parent = country,
                            )
                        else:
                            city = search[0]
                        info.reference_spaces.add(city)
            info.save()
                            

    return HttpResponse("All good")

def temp_import_references(request):

    # Delete after Jan 1, 2020
    path = settings.MEDIA_ROOT + "/references.txt"
    contents = open(path, "r").read()
    lines = contents.splitlines()
    megastring = ""
    count = 0

    import re

    tag = Tag.objects.filter(name="UM review paper import")
    if tag:
        tag = tag[0]
    else:
        tag = Tag.objects.create(
            name = "UM review paper import",
            parent_tag = Tag.objects.get(name="Temporary tags"),
            hidden = True,
        )

    casestudytag = Tag.objects.get(pk=1)
    x = re.split("([0-9][0-9][0-9][0-9]\.)", megastring)
    total = 0
    list = []
    for details in x:
        getlength = len(details)
        details = details.strip()
        s = None
        if getlength > 50:
            start = details[0:40]
            search = Reference.objects.filter(title__icontains=start)
            if search.count() == 1:
                total += 1
                s = search[0]
            elif search.count() > 1:
                pass
            else:
                start = details[30:45]
                search = Reference.objects.filter(title__icontains=start)
                if search.count() == 1:
                    total += 1
                    s = search[0]
        if s:
            s.tags.add(tag)
            s.tags.add(casestudytag)
            print(s)
            list.append(s)

    print("TOTAL: " + str(total))
    #print(matches)
    context = { 
        "list": list,
    }
    return render(request, "core/temp.html", context)
