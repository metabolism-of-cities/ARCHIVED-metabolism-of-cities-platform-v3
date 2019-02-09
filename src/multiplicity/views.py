from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from .models import Topic, DatasetType, ReferenceSpace, ReferenceSpaceType, Feature, ReferenceSpaceCSV, ReferenceSpaceLocation, ReferenceSpaceFeature, ReferenceSpaceForm, ReferenceSpaceLocationForm, DQI, DQIRating, Information, GraphType, DatasetType, DatasetTypeForm, DatasetTypeStructure, InformationForm, PhotoForm, Photo, ProcessGroup, ReferencePhoto, ReferencePhotoForm, MTU

from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.template.defaultfilters import slugify
from core.models import UserAction, UserLog, ReferenceForm, Reference, ReferenceType, Organization, Video, VideoUploadForm
from staf.models import CSV, Material, Data, Unit, TimePeriod, DatasetForm, Material, Dataset, Process
from django.db.models import Count
from django.contrib import messages

# To serialize into json
from django.core import serializers

# For file uploads
import uuid
import csv
import codecs

from django.conf import settings
from collections import defaultdict
import datetime
from dateutil.parser import parse

# Getting min and max values
from django.db.models import Max
from django.db.models import Min

# To create json objects
import json

# To search annotate
from django.db.models import Q

# To use factory forms
from django.forms import modelform_factory

# To get a representative image for a set of reference spaces
from django.db.models import OuterRef, Subquery

def index(request):
    list = ReferenceSpace.objects.filter(type__id=3)
    context = { 'section': 'cites', 'menu': 'dashboard', 'list': list, 'datatables': True, 'topics': topics }
    return render(request, 'multiplicity/city.html', context)

def space_list(request, city, type):
    info = get_object_or_404(ReferenceSpace, slug=city)
    type = get_object_or_404(ReferenceSpaceType, slug=type)
    list = ReferenceSpace.objects.filter(city=info, type=type)
    features = Feature.objects.filter(type=type.id, show_in_table=True).filter(Q(exclusively_for__isnull=True) | Q(exclusively_for=info))
    features_list = ReferenceSpaceFeature.objects.filter(space__type=type, feature__show_in_table=True)
    feature = defaultdict(dict)
    for details in features_list:
        feature[details.space.id][details.feature.id] = details.value
    topic = type.topic
    tab = type.slug
    data_out = {}
    single = False
    for details in list:
        data = Data.objects.filter(origin_space=details.id)
        if data:
            data_out[details.name] = data
            # This single is just to have a single dataset to loop over. Not efficient at all. 
            # TODO fix this whole way of querying the database for all data
            single = data

    data_in = Data.objects.filter(destination_space__type=type)
    topics = Topic.objects.exclude(position=0).filter(parent__isnull=True)
    context = { 'section': 'cities', 'menu': 'infrastructure', 'info': info, 'type': type, 'list': list, 'datatables': True, 'tab': tab, 'page': type.topic.slug, 'topic':topic, 'features': features,
    'feature': feature, 'data_in': data_in, 'data_out': data_out, 'charts': True, 'single': single, 'topics': topics}
    return render(request, 'multiplicity/space.list.html', context)

def space(request, city, type, space):
    info = get_object_or_404(ReferenceSpace, slug=city)
    type = get_object_or_404(ReferenceSpaceType, slug=type)
    space = get_object_or_404(ReferenceSpace, city=info, type=type, slug=space)
    log = UserLog.objects.filter(space=space)
    data_in = Data.objects.filter(destination_space=space)
    data_out = Data.objects.filter(origin_space=space)
    feature_list = ReferenceSpaceFeature.objects.filter(space=space)
    photos = space.photos.filter(deleted=False)
    videos = Video.objects.filter(primary_space=space)
    gallery = False
    if photos:
        gallery = True
    features = {}
    for details in feature_list:
        features[details.feature.name] = details.value
    topic = type.topic
    tab = type.slug
    photouploadlink = '/cities/'+info.slug+'/photo?space='+str(space.id)
    videouploadlink = '/cities/'+info.slug+'/upload/video?space='+str(space.id)
    editlink = '/admin/multiplicity/referencespace/'+str(space.id)+'/change/'
    topics = Topic.objects.exclude(position=0).filter(parent__isnull=True)
    if space.mtu:
        menu = 'resources'
        page = 'maps'
    else:
        menu = 'infrastructure'
        page = 'unsure'
    context = { 'section': 'cities', 'menu': menu, 'page': page, 'info': info, 
    'type': type, 'space': space, 'tab': tab, 'log': log, 'features': features, 'topic': topic,
    'data_in': data_in, 'data_out': data_out, 'datatables': True, 'charts': True, 'topics': topics, 
    'feature_list': feature_list, 'editlink': editlink, 'photos': photos,
    'gallery': gallery, 'videos': videos, 'photouploadlink': photouploadlink,
    'videouploadlink': videouploadlink, 
    }
    return render(request, 'multiplicity/space.html', context)

def map(request, city, type='boundaries', id=False):
    topics = Topic.objects.exclude(position=0).filter(parent__isnull=True)
    info = get_object_or_404(ReferenceSpace, slug=city)
    if id:
        boundary = get_object_or_404(ReferenceSpaceLocation, pk=id)
    else:
        boundary = info.location
    list = ReferenceSpaceLocation.objects.filter(space=info)
    editlink = reverse('multiplicity:upload_systemboundary', args=[info.slug, boundary.id])
    addlink = reverse('multiplicity:upload_systemboundary', args=[info.slug])
    if type == 'boundaries':
        tab = 'boundaries'
    context = { 
        'section': 'cities', 'menu':  'resources', 'page': 'maps', 'info': info, 
        'topics': topics, 'boundary': boundary, 'tab': tab, 'list': list,
        'editlink': editlink, 'addlink': addlink
    }
    return render(request, 'multiplicity/space.map.html', context)

def mtu_map(request, city, type=False):
    info = get_object_or_404(ReferenceSpace, slug=city)
    mtu_list = MTU.objects.filter(space=info)
    
    if type:
        type = get_object_or_404(ReferenceSpaceType, slug=type)
    elif mtu_list:
        type = mtu_list[0].type
    else:
        type = False

    if mtu_list:
        datatables = True
        map = True
    else:
        datatables = False
        map = False
    list = ReferenceSpace.objects.filter(city=info, type=type)
    tab = 'mtu'
    context = { 
        'section': 'cities', 'menu':  'resources', 'info': info, 
        'tab': tab, 'list': list, 'page': 'maps', 'datatables': datatables, 
        'mtu_list': mtu_list, 'type': type, 'map': map, 
    }
    return render(request, 'multiplicity/mtu.map.html', context)

def sector(request, city, sector):
    info = get_object_or_404(ReferenceSpace, slug=city)
    sector = get_object_or_404(ProcessGroup, slug=sector)
    information = Information.objects.filter(process__in=sector.processes.all(), space=info).order_by('position')
    references = Reference.objects.filter(processes__in=sector.processes.all(), tags=info.tag).order_by('title')
    organizations = Organization.objects.filter(processes__in=sector.processes.all(), reference_spaces=info).order_by('name')
    datasets = Dataset.objects.filter(primary_space=info, process__in=sector.processes.all(), deleted=False)
    addlink = reverse('multiplicity:information_form', args=[info.slug])
    photos = Photo.objects.filter(primary_space=info, process__in=sector.processes.all(), deleted=False)
    map = False
    infrastructure = False

    last_space = ReferenceSpace.objects.filter(type=OuterRef('pk')).order_by('-id')
    space_photo = Photo.objects.filter(secondary_space__type=OuterRef('pk')).order_by('id')
    types = ReferenceSpaceType.objects.filter(process__in=sector.processes.all()).annotate(total=Count('referencespace', filter=Q(referencespace__city=info)))
    types = types.annotate(image=Subquery(space_photo.values('image')[:1]))

    #Photo.objects.filter(primary_space=OuterRef('referencespace', secondary_space__isnull=True, process__isnull=True, deleted=False)

# newest = Comment.objects.filter(post=OuterRef('pk')).order_by('-created_at')
# Post.objects.annotate(newest_commenter_email=Subquery(newest.values('email')[:1]))
    print(types)

    spaces_list = {}
    for type in types:
        get_list = ReferenceSpace.objects.filter(city=info, type=type)
        if get_list:
            spaces_list[type.id] = get_list
            # We should build in a check to see if the spaces really have coordinates available; if not map = false
            map = True
            infrastructure = True

    features_list = ReferenceSpaceFeature.objects.filter(space__type__process__in=sector.processes.all(), feature__show_in_table=True)
    feature = defaultdict(dict)
    for details in features_list:
        feature[details.space.id][details.feature.id] = details.value

    context = { 'section': 'cities', 'menu':  'sectors', 'sector': sector, 'info': info, 'information': information, 'datasets': datasets, 
    'map': map, 'addlink': addlink, 'types': types, 'gallery': True, 'spaces_list': spaces_list, 'datatables': True, 'feature': feature, 
    'infrastructure': infrastructure, 'photos': photos, 'references': references, 'organizations': organizations, 
    }
    return render(request, 'multiplicity/sector.html', context)

def overview(request, city, slug):
    groups = ProcessGroup.objects.order_by('name')
    flow = get_object_or_404(DatasetTypeStructure, slug=slug)
    list = DatasetType.objects.filter(category__parent=flow)
    types = DatasetTypeStructure.objects.filter(parent=flow)
    if not types:
        types = DatasetTypeStructure.objects.filter(pk=flow.id)
    info = get_object_or_404(ReferenceSpace, slug=city)

    if flow.parent and flow.parent.name == "Material Flows":
      menu = 'material-flows'
    elif flow.parent and flow.parent.parent and flow.parent.parent.name == "Material Flows":
      menu = 'material-flows'
      slug = flow.parent.slug
    else:
      menu = 'material-stocks'

    page = slug
    context = { 'section': 'cities', 'menu':  menu, 'page': slug, 'info': info,
    'list': list, 'types': types, 'flow': flow, 'slug': slug,
    'editlink': reverse('multiplicity:admin_datasettypes'),
    'groups': groups
    }
    return render(request, 'multiplicity/overview.html', context)

def overview(request, city, slug):
    groups = ProcessGroup.objects.order_by('name')
    flow = get_object_or_404(DatasetTypeStructure, slug=slug)
    list = DatasetType.objects.filter(category__parent=flow)
    types = DatasetTypeStructure.objects.filter(parent=flow)
    if not types:
        types = DatasetTypeStructure.objects.filter(pk=flow.id)
    info = get_object_or_404(ReferenceSpace, slug=city)

    if flow.parent and flow.parent.name == "Material Flows":
      menu = 'material-flows'
    elif flow.parent and flow.parent.parent and flow.parent.parent.name == "Material Flows":
      menu = 'material-flows'
      slug = flow.parent.slug
    else:
      menu = 'material-stocks'

    page = slug
    context = { 'section': 'cities', 'menu':  menu, 'page': slug, 'info': info,
    'list': list, 'types': types, 'flow': flow, 'slug': slug,
    'editlink': reverse('multiplicity:admin_datasettypes'),
    'groups': groups
    }
    return render(request, 'multiplicity/overview.html', context)

def flow(request, city, type, slug=False):
    info = get_object_or_404(ReferenceSpace, slug=city)
    type = get_object_or_404(DatasetType, slug=type)
    list = Dataset.objects.filter(type=type)
    if type.category.slug == 'internal': 
      page = 'internal'
    else:
      page = 'external'
    editlink = reverse('multiplicity:admin_datasettype', args=[type.id])
    addlink = reverse('multiplicity:information_form', args=[info.slug])
    information = Information.objects.filter(space=info, dataset_types=type)
    photos = Photo.objects.filter(primary_space=info, topic=type.topic, deleted__isnull=False)
    context = { 'section': 'cities', 'menu':  'material-flows', 'page': page, 'info': info,
        'list': list, 'flow': flow, 'slug': slug, 'type': type, 'editlink': editlink,
        'addlink': addlink, 'information': information, 'photos': photos,
        'gallery': True,
    }
    return render(request, 'multiplicity/flow.html', context)

def photos(request, city, type='photo'):
    info = get_object_or_404(ReferenceSpace, slug=city)
    photos = Photo.objects.filter(primary_space=info, deleted=False, type=type)
    topics = Topic.objects.exclude(position=0).filter(parent__isnull=True)
    addlink = reverse('multiplicity:photo_form', args=[info.slug])
    if type == 'photo':
        page = 'photos'
        tab = False
        title = 'Photos'
    else:
        page = 'maps'
        tab = 'other'
        title = 'Other maps'

    context = { 'section': 'cities', 'menu':  'resources', 'page': page, 'info': info, 'photos': photos, 
    'topics': topics, 'addlink': addlink, 'gallery': True, 'tab': tab, 'title': title }
    return render(request, 'multiplicity/resources.photos.html', context)

def videos(request, city):
    info = get_object_or_404(ReferenceSpace, slug=city)
    list = Video.objects.filter(primary_space=info)
    addlink = reverse('multiplicity:photo_form', args=[info.slug])

    context = { 'section': 'cities', 'menu':  'resources', 'page': 'videos', 'info': info, 'list': list,
    'addlink': addlink, }
    return render(request, 'multiplicity/resources.videos.html', context)

def resources(request, city, slug):
    info = get_object_or_404(ReferenceSpace, slug=city)
    topics = Topic.objects.exclude(position=0).filter(parent__isnull=True)
    if slug == "reports":
        type = 27
    elif slug == "journal-articles":
        type = 16
    elif slug == "theses":
        type = 29
    elif slug == "presentations":
        type = 25
    elif slug == "podcasts":
        type = 24
    type = get_object_or_404(ReferenceType, pk=type)
    references = Reference.objects.filter(status='active', tags=info.tag, type=type).order_by('-year')
    addlink = reverse('multiplicity:photo_form', args=[info.slug])

    context = { 'section': 'cities', 'menu':  'resources', 'page': type.name, 'info': info, 'references': references, 'topics': topics, 'addlink': addlink, 'type': type, 'slug': slug}
    return render(request, 'multiplicity/resources.list.html', context)

def datasets(request, city):
    info = get_object_or_404(ReferenceSpace, slug=city)
    datasets = Dataset.objects.filter(primary_space=info, deleted=False)
    topics = Topic.objects.exclude(position=0).filter(parent__isnull=True)
    context = { 'section': 'cities', 'menu':  'resources', 'page': 'datasets', 'info': info, 'datasets': datasets, 'topics': topics }
    return render(request, 'multiplicity/datasets.html', context)

def datasets_overview(request, city, topic, type='flows'):
    info = get_object_or_404(ReferenceSpace, slug=city)
    topic = Topic.objects.get(slug=topic)
    datasets = Dataset.objects.filter(primary_space=info, deleted=False, topics=topic, type__type=type)
    context = { 'section': 'cities', 'menu':  type, 'page': topic.slug, 'info': info, 'datasets': datasets, 'topic': topic}
    return render(request, 'multiplicity/datasets.html', context)

def dataset(request, city, id, slug=False):
    info = get_object_or_404(ReferenceSpace, slug=city)
    dataset = get_object_or_404(Dataset, pk=id)
    csv_files = CSV.objects.filter(dataset=id)
    scoring = range(1,6)
    topics = Topic.objects.exclude(position=0).filter(parent__isnull=True)
    editlink = '/admin/staf/dataset/' + str(id) + '/change/'
    topic = None
    unit = get_object_or_404(Unit, pk=1)
    graphs = GraphType.objects.exclude(pk__in=[7,8,10])
    materials = Data.objects.filter(dataset=dataset).values('material_name').order_by('material_name').distinct()
    timeframes = Data.objects.select_related('timeframe').filter(dataset=dataset).distinct('timeframe__start').order_by('timeframe__start').count()
    all_materials = materials.count()
    materials_hidden = False
    if all_materials > 5:
        materials_hidden = all_materials-5
    materials = materials[:5]
    dates = Data.objects.filter(dataset=dataset).aggregate(start=Min('timeframe__start'), end=Max('timeframe__end'))

    #for datapoint in dataset.data_set.all():
    #datapoint.material in topic.materials.all() or datapoint.material.parent in topic.materials.all():
    deletelink = '/cities/' + info.slug + '/datasets/' + str(dataset.id) + '/delete'
    context = { 'section': 'cities', 'menu':  'resources', 'page': 'datasets', 'info': info, 'dataset': dataset, 'csv_files': csv_files, 'datatables': True, 'scoring': scoring, 'topics': topics, 'editlink': editlink, 'topic': topic, 'deletelink': deletelink, 'graphs': graphs, 'dates': dates, 'materials': materials, 'materials_hidden': materials_hidden, 'timeframes': timeframes, }
    return render(request, 'multiplicity/dataset.html', context)

def datatable(request, dataset=False, material=False):
    dataset = get_object_or_404(Dataset, pk=dataset)
    data = Data.objects.filter(dataset=dataset)
    context = { 'data': data, 'dataset': dataset }
    return render(request, 'multiplicity/includes/datatable.html', context)

def graph(request, city, dataset, id):
    info = get_object_or_404(ReferenceSpace, slug=city)
    dataset = get_object_or_404(Dataset, pk=dataset)
    timeframes = Data.objects.select_related('timeframe').filter(dataset=dataset).distinct('timeframe__start').order_by('timeframe__start')
    data = Data.objects.filter(dataset=dataset).order_by('timeframe__start')
    data_groups = Data.objects.select_related('material').filter(dataset=dataset).distinct('material__name').order_by('material__name')
    data_subgroups = Data.objects.filter(dataset=dataset).distinct('material_name').order_by('material_name')
    unit = False

    space = dataset.primary_space

    t1 = []
    t2 = []
    t3 = []
    for row in timeframes:
        t1.append({'label':row.timeframe.name})
        t2.append({'date':row.timeframe.start.strftime("%Y-%m-%d")})
        t3.append({'date':row.timeframe.start.strftime("%Y, %m, %d")})
    t1 = json.dumps(t1)
    t2 = json.dumps(t2)
    t3 = json.dumps(t3)

    groups = []
    for row in data_groups:
        groups.append({'label': row.material.name})
    groups = json.dumps(groups)

    subgroups = []
    for row in data_subgroups:
        subgroups.append({'label': row.material_name, 'group': row.material.name})
    subgroups = json.dumps(subgroups)

    datapoints = []
    spaces = []
    for row in data:
        unit = False
        if row.unit:
            unit = row.unit.symbol
        this_space = False
        if row.origin_space and row.origin_space.city == space:
            this_space = row.origin_space.name
        elif row.destination_space and row.destination_space.city == space:
            this_space = row.destination_space.name
        elif row.destination_space and row.destination_space.city == space:
            this_space = row.destination_space.name
        elif row.destination_space == space or row.origin_space == space:
            this_space = space.name

        if this_space:
            if this_space not in spaces:
                spaces.append(this_space)

        datapoints.append({'material_name': row.material_name, 'material_group': row.material.name, 'date': row.timeframe.start.strftime("%Y-%m-%d"), 'date_label': row.timeframe.name, 'date_formatted':row.timeframe.start.strftime("%Y, %m, %d"), 'quantity': row.quantity, 'unit': unit, 'type': this_space})
    datapoints = json.dumps(datapoints)

    spaces = json.dumps(spaces)

    graph = get_object_or_404(GraphType, pk=id)
    context = {'graph': graph, 'dataset': dataset, 'info': info, 
    't1': t1, 
    't2': t2,
    't3': t3,
    'groups': groups,
    'subgroups': subgroups,
    'data': datapoints,
    'spaces': spaces,
    'info': info,
    'dataset': dataset,
    'unit': unit,
    }
    return render(request, 'multiplicity/graphs/' + graph.slug + '.html', context)

def topicmap(request, city, theme, topic):
    info = get_object_or_404(ReferenceSpace, slug=city)
    topic = get_object_or_404(Topic, slug=topic)
    spaces = ReferenceSpace.objects.filter(city=info, type__topic=topic)
    types = ReferenceSpaceType.objects.filter(topic=topic).annotate(total=Count('referencespace', filter=Q(city=info)))
    # TODO Surely we can do better than this? A single db query should be possible.
    count = {}
    for details in spaces:
        if details.type.id in count:
            count[details.type.id] += 1
        else:
            count[details.type.id] = 1
    context = { 'section': 'cities', 'menu': topic.theme.slug, 'page': topic.slug, 'info': info, 'topic': topic, 'spaces': spaces, 'types': types, 'count': count, 'tab': 'overview'}
    return render(request, 'multiplicity/topic.html', context)

# Download options

def download_location(request, city, id):
    info = get_object_or_404(ReferenceSpaceLocation, pk=id)
    response = HttpResponse(info.geojson, content_type="application/json")
    response['Content-Disposition'] = 'attachment; filename="' + info.name + '.json"'
    return response


def download_csv(request, city, id):
    file = get_object_or_404(CSV, pk=id)
    file_path = settings.MEDIA_ROOT + '/csv/' + file.name
    contents = open(file_path, 'r')
    date = str(file.created_at.year) + '-' + str(file.created_at.month) + '-' + str(file.created_at.day)
    response = HttpResponse(contents, content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="'+file.dataset.name+'-'+date+'.csv"'
    return response

@login_required
def upload_flow(request, city, type='flows'):
    info = get_object_or_404(ReferenceSpace, slug=city)
    types = False
    if type == 'flows':
        types = DatasetTypeStructure.objects.filter(pk__in=[8,9,10,11,6])
    list = DatasetType.objects.filter(type=type, active=True)
    addlink = '/admin/multiplicity/datasettype/add/'
    context = { 'section': 'cities', 'menu': 'upload', 'info': info, 'list': list, 'types': types, 'addlink': addlink, 'type': type}
    return render(request, 'multiplicity/upload/index.flow.html', context)

@login_required
def upload_infrastructure(request, city):
    info = get_object_or_404(ReferenceSpace, slug=city)
    list = ReferenceSpaceType.objects.filter(user_accessible=True).order_by('name')
    context = { 'section': 'cities', 'menu': 'upload', 'info': info, 'list': list, 'datatables': True }
    return render(request, 'multiplicity/upload/index.infrastructure.html', context)

@login_required
def upload_infrastructure_file(request, city, type):
    info = get_object_or_404(ReferenceSpace, slug=city)
    type = get_object_or_404(ReferenceSpaceType, slug=type)
    features = Feature.objects.filter(type=type.id).filter(Q(exclusively_for__isnull=True) | Q(exclusively_for=info))
    previous = ReferenceSpaceCSV.objects.filter(user=request.user, type=type, space=info)
    if request.method == 'POST':
        if 'data' in request.POST:
            input = request.POST['data']
            filename = str(uuid.uuid4())
            file = 'Data entry on ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            path = settings.MEDIA_ROOT + '/csv-referencespace/' + filename
            in_txt = csv.reader(input.split('\n'), delimiter = '\t')
            out_csv = csv.writer(open(path, 'w', newline=''))
            out_csv.writerows(in_txt)
        else:
            file = request.FILES['file']
            filename = str(uuid.uuid4())
            path = settings.MEDIA_ROOT + '/csv-referencespace/' + filename

            with open(path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

        csv_file = ReferenceSpaceCSV(name=filename, original_name=file, imported=False, user=request.user, type=type, space=info)
        csv_file.save()
        return redirect('multiplicity:upload_infrastructure_review', id=csv_file.id, type=type.slug, city=info.slug)

    topics = Topic.objects.exclude(position=0).filter(parent__isnull=True)
    context = { 'section': 'cities', 'menu': 'upload', 'info': info, 'features': features, 'type': type, 'previous': previous, 'topics': topics }
    return render(request, 'multiplicity/upload/infrastructure.file.html', context)

@login_required
def upload_flow_file(request, city, id):
    info = get_object_or_404(ReferenceSpace, slug=city)
    dataset = get_object_or_404(DatasetType, pk=id)
    type = dataset.type
    if request.user.is_staff:
        previous = CSV.objects.filter(datasettype=dataset, space=info)
    else:
        previous = CSV.objects.filter(user=request.user, datasettype=dataset, space=info)
    if request.method == 'POST':
        if 'data' in request.POST:
            input = request.POST['data']
            filename = str(uuid.uuid4())
            file = 'Data entry on ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            path = settings.MEDIA_ROOT + '/csv/' + filename
            in_txt = csv.reader(input.split('\n'), delimiter = '\t')
            out_csv = csv.writer(open(path, 'w', newline=''))
            out_csv.writerows(in_txt)
        else:
            file = request.FILES['file']
            filename = str(uuid.uuid4())
            path = settings.MEDIA_ROOT + '/csv/' + filename

            with open(path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

        csv_file = CSV(name=filename, original_name=file, imported=False, user=request.user, datasettype=dataset, space=info)
        csv_file.save()
        return redirect('multiplicity:upload_flow_review', id=csv_file.id, type=dataset.id, city=info.slug)

    topics = Topic.objects.exclude(position=0).filter(parent__isnull=True)
    editlink = '/admin/multiplicity/datasettype/' + str(id) +'/change/'
    context = { 'section': 'cities', 'menu': 'upload', 'info': info, 'type': type, 'previous': previous, 'dataset': dataset, 'editlink': editlink, 'topics': topics }
    return render(request, 'multiplicity/upload/flow.file.html', context)

@login_required
def upload_flow_file_sample(request, city, id):
    most_recent_file = CSV.objects.filter(dataset__type__id=id, imported=True).order_by('-id')
    if most_recent_file:
        most_recent_file = most_recent_file[0]
        file = settings.MEDIA_ROOT + '/csv/' + most_recent_file.name
        contents = open(file, 'r')
    else:
        info = get_object_or_404(DatasetType, id=id)
        if info.type == "stocks":
            contents = "Date"
        else:
            contents = "Timeframe name,From (date),To(date"
        contents = contents + ",Material name,Material code,Quantity,Unit"
        if info.flows == "destination_only" or info.flows == "origin_only":
            contents = contents + ",Location"
        else:
            contents = contents + ",Origin,Destination"
        contents = contents + ",Comments"

    response = HttpResponse(contents, content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="sample.csv"'
    return response

@login_required
def upload_infrastructure_file_sample(request, city, type):
    from django.http import FileResponse
    most_recent_file = ReferenceSpaceCSV.objects.filter(type__slug=type, imported=True).order_by('-id')
    if most_recent_file:
        most_recent_file = most_recent_file[0]
        file = settings.MEDIA_ROOT + '/csv-referencespace/' + most_recent_file.name
        contents = open(file, 'r')
    else:
        type = get_object_or_404(ReferenceSpaceType, slug=type)
        # If the file has not yet been uploaded before, then we need to create our own
        # sample file
        info = get_object_or_404(ReferenceSpace, slug=city)
        features = Feature.objects.filter(type=type.id).filter(Q(exclusively_for__isnull=True) | Q(exclusively_for=info))
        contents = "Name,Latitude,Longitude,Description,Website URL"
        for details in features:
            contents = contents + "," + details.name
    response = HttpResponse(contents, content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="sample.csv"'
    return response


@login_required
def upload_infrastructure_review(request, city, type, id):
    info = get_object_or_404(ReferenceSpace, slug=city)
    type = get_object_or_404(ReferenceSpaceType, slug=type)
    if request.user.is_staff:
        csv_file = ReferenceSpaceCSV.objects.get(pk=id)
    else:
        csv_file = ReferenceSpaceCSV.objects.get(pk=id, user=request.user)
    data = []
    datatables = True
    error = False
    feature_list = {}

    path = settings.MEDIA_ROOT + '/csv-referencespace/' + csv_file.name
    features = Feature.objects.filter(type=type.id).filter(Q(exclusively_for__isnull=True) | Q(exclusively_for=info))
    # By default there are 5 rows, so we start the count at 4 for additional rows
    start = 4
    column_count = start+1
    if features:
        column_count = column_count+features.count()

    try:
        f = codecs.open(path, encoding='utf-8', errors='strict')
        reader = csv.reader(f)

        if not error:
            for row in reader:

                if len(row) != column_count:
                    error = "File format invalid. The number of columns in the files is not correct. We expect " + str(column_count) + "  columns but the file had " + str(len(row))
                elif not error:

                    existing = False
                    if row[0].strip() != "Name" and row[0]:
                        check = ReferenceSpace.objects.filter(city=info, type=type, name=row[0].strip())
                        if check:
                            existing = True

                        if features:
                            count = start
                            feature_list = {}
                            for details in features:
                                count = count + 1
                                feature_list[details.name] = row[count]

                        data.append({'name': row[0], 'existing': existing, 'lat': row[1], 'lng': row[2], 'url': row[4], 'description': row[3],'features': feature_list});

    except UnicodeDecodeError:
        error = "File is not saved as UTF-8. Please save in UTF-8 format, or use our template files."

    menu = 'infrastructure'
    topics = Topic.objects.exclude(position=0).filter(parent__isnull=True)
    context = { 'section': 'cities', 'menu': 'upload', 'data': data, 'file': csv_file, 'datatables': datatables, 'info': info, 'type': type, 'features': features, 'topics': topics, 'error': error }
    return render(request, 'multiplicity/upload/infrastructure.review.html', context)


@login_required
def upload_flow_review(request, city, type, id):
    info = get_object_or_404(ReferenceSpace, slug=city)
    if request.user.is_staff:
        csv_file = CSV.objects.get(pk=id)
    else:
        csv_file = CSV.objects.get(pk=id, user=request.user)
    dataset = get_object_or_404(DatasetType, pk=type)

    data = []
    datatables = True
    feature_list = {}

    path = settings.MEDIA_ROOT + '/csv/' + csv_file.name
    # By default there are 5 rows, so we start the count at 4 for additional rows
    start = 4

    referencespacelist = {}
    materiallist = {}
    show_origin = False
    show_destination = False
    show_location = False
    error = False
    warning = False

    if dataset.type == "stocks":
        column_count = 7
        column_origin = False
        column_destination = 5
        show_location = True
        if dataset.name == "Population":
            column_count = 5
            column_destination = 3
    elif dataset.flows == 'origin_and_destination':
        column_count = 10
        column_origin = 7
        column_destination = 8
    elif dataset.flows == 'origin_only':
        column_count = 9
        column_origin = 7
        column_destination = False
        show_location = True
    else:
        column_count = 9
        column_origin = False
        column_destination = 7
        show_location = True
    column_comments = column_count-1

    try:
        f = codecs.open(path, encoding='utf-8', errors='strict')
        reader = csv.reader(f)
        for row in reader:

            existing = False

            if len(row) != column_count and len(row) > 0:
                error = "File format invalid. The number of columns in the files is not correct. We expect " + str(column_count) + "  columns but the file had " + str(len(row))
            elif not error and len(row) > 0:
                if row[0].strip() != "Timeframe" and row[0] and row[0].strip() != "Timeframe name" and row[0].strip() != "Date" :

                    if dataset.name == "Population":
                        material = "People"
                        if row[1].strip():
                            material = row[1]
                        material_code = "MF1.5.1"
                        date = row[0]
                        qty = row[2]
                        unit = "unit"
                    elif dataset.type == "stocks":
                        material = row[1].strip()
                        material_code = row[2].strip()
                        date = row[0]
                        qty = row[3]
                        unit = row[4]
                    else:
                        timeframe = row[0]
                        material = row[3].strip()
                        material_code = row[4].strip()
                        start_date = row[1]
                        end_date = row[2]
                        qty = row[5]
                        unit = row[6]
                    if not material and not material_code:
                        error = "Every row must have a material name or material code"
                    material_info = False

                    # We create a dictionary that holds all the query results for each of the names.
                    # Otherwise we'll keep running the same queries if the names repeat
                    # So before we run a query, we check if the query has already been done 

                    if material_code in materiallist:
                        material_info = materiallist[material_code]
                    elif material in materiallist:
                        material_info = materiallist[material]
                    else:
                        if material_code:
                            material_info = Material.objects.filter(code=material_code)
                            if material_info:
                                material_info = material_info[0]
                                materiallist[material_code] = material_info
                            else:
                                error = "We could not find one or more of the materials listed (code: " + material_code + "). Please provide a material code to ensure that we can locate this material."
                        else:
                            material_info = Material.objects.filter(name=material)
                            if material_info:
                                material_info = material_info[0]
                                materiallist[material] = material_info
                            else:
                                error = "We could not find one or more of the materials listed (" + material + "). Please provide a material code to ensure that we can locate this material."

                    destination = False
                    destination_info = False
                    if column_destination:
                        destination = row[column_destination].strip()
                        if destination:
                            show_destination = True

                            # We create a dictionary that holds all the query results for each of the names.
                            # Otherwise we'll keep running the same queries if the names repeat
                            # So before we run a query, we check if the query has already been done 

                            if destination in referencespacelist:
                                destination_info = referencespacelist[destination]
                            elif destination == info.name:
                                destination_info = info
                            else:
                                destination_info = ReferenceSpace.objects.filter(city=info,name=destination)
                                if not destination_info:
                                    destination_info = ReferenceSpace.objects.filter(name=destination)
                                if destination_info:
                                    # We only want a single result, so slice this
                                    destination_info = destination_info[0]
                                else:
                                    warning = "We could not find the place(s) marked in red. Make sure the place(s) exist in the system first."
                                referencespacelist[destination] = destination_info

                    origin = False
                    origin_info = False
                    if column_origin:
                        # We'll do the exact same thing with origin as we did with destination
                        origin = row[column_origin].strip()
                        if origin:
                            show_origin = True
                            if origin in referencespacelist:
                                origin_info = referencespacelist[origin]
                            elif origin == info.name:
                                origin_info = info
                            else:
                                origin_info = ReferenceSpace.objects.filter(city=info,name=origin)
                                if not origin_info:
                                    origin_info = ReferenceSpace.objects.filter(name=origin)
                                if origin_info:
                                    origin_info = origin_info[0]
                                else:
                                    warning = "We could not find the place(s) marked in red. Make sure the place(s) exist in the system first."
                                referencespacelist[origin] = origin_info
                    if dataset.type == "stocks":

                        try:
                            start = parse(date)
                            end = False
                            timeframe = start
                        except ValueError:
                            error = "Date not valid: " + str(date)
                            end = "Unknown date"
                            timeframe = date

                    else:
                        try:
                            start = parse(start_date)
                        except ValueError:
                            error = "Date not valid: " + str(start_date)
                            end = "Unknown date"

                        try:
                            end = parse(end_date)
                        except ValueError:
                            error = "Date not valid: " + str(end_date)
                            end = "Unknown date"

                    try:
                        quantity = float(qty.replace(',',''))
                    except ValueError:
                        quantity = None

                    data.append({'timeframe': timeframe, 'from': start, 'to': end, 'material': material, 'material_info': material_info, 'quantity': quantity,
                    'unit': unit, 'origin': origin, 'origin_info': origin_info, 'destination': destination, 'destination_info': destination_info, 'comments': row[column_comments]})

    except UnicodeDecodeError:
        error = "File is not saved as UTF-8. Please save in UTF-8 format, or use our template files."

    topics = Topic.objects.exclude(position=0).filter(parent__isnull=True)

    context = { 'section': 'cities', 'menu': 'upload', 'data': data, 'file': csv_file, 'datatables': datatables, 'info': info, 
    'dataset': dataset, 'show_origin': show_origin, 'show_destination': show_destination, 'error': error, 'show_location': show_location, 'topics': topics, 'warning': warning,
    'type': dataset.type }
    return render(request, 'multiplicity/upload/flow.review.html', context)

@login_required
def upload_infrastructure_meta(request, city, type, id):
    info = get_object_or_404(ReferenceSpace, slug=city)
    type = get_object_or_404(ReferenceSpaceType, slug=type)
    csv_file = ReferenceSpaceCSV.objects.get(pk=id)
    #csv_file = ReferenceSpaceCSV.objects.get(pk=id, user=request.user)
    features = Feature.objects.filter(type=type.id).filter(Q(exclusively_for__isnull=True) | Q(exclusively_for=info))

    # By default there are 5 rows, so we start the count at 4 for additional rows
    start = 4

    if request.method == 'POST':
        path = settings.MEDIA_ROOT + '/csv-referencespace/' + csv_file.name
        with open(path) as f:
            reader = csv.reader(f)
            for row in reader:
                existing = False
                if row[0] != "Name".strip() and row[0]:
                    check = ReferenceSpace.objects.filter(city=info, type=type, name=row[0].strip())
                    if check:
                        existing = True
                    else:
                        record = ReferenceSpace(
                            name = row[0].strip(),
                            type = type,
                            city = info,
                            country = info.country,
                            url = row[4],
                            description = row[3],
                            csv = csv_file,
                        )
                        record.save()

                        if row[1] and row[2]:
                            location = ReferenceSpaceLocation(
                                space = record,
                                lat = row[1],
                                lng = row[2],
                            )
                            location.save()
                            record.location = location
                            record.save()

                        if features:
                            count = start
                            for details in features:
                                count = count + 1
                                if row[count]:
                                    feature = ReferenceSpaceFeature(space=record, feature=details, value=row[count])
                                    feature.save()

                        create_record = get_object_or_404(UserAction, pk=1)
                        log = UserLog(user=request.user, action=create_record, space=record, points=10)
                        log.save()

        csv_file.imported = True
        csv_file.how_obtained = request.POST['how_obtained']
        csv_file.gaps = request.POST['gaps']
        csv_file.source = request.POST['source']
        csv_file.save()

        return redirect('multiplicity:space_list', type=type.slug, city=info.slug)

    topics = Topic.objects.exclude(position=0).filter(parent__isnull=True)
    context = { 'section': 'cities', 'menu': 'upload', 'file': csv_file, 'info': info, 'type': type, 'topics': topics }
    return render(request, 'multiplicity/upload/infrastructure.meta.html', context)

@login_required
def upload_flow_meta(request, city, type, id):
    info = get_object_or_404(ReferenceSpace, slug=city)
    if request.user.is_staff:
        csv_file = CSV.objects.get(pk=id)
    else:
        csv_file = CSV.objects.get(pk=id, user=request.user)
    dataset = get_object_or_404(DatasetType, pk=type)
    error = False

    if dataset.type == "stocks":
        column_count = 7
        column_origin = False
        column_destination = 5
        show_location = True
        if dataset.name == "Population":
            column_count = 5
            column_destination = 3
    elif dataset.flows == 'origin_and_destination':
        column_count = 10
        column_origin = 7
        column_destination = 8
    elif dataset.flows == 'origin_only':
        column_count = 9
        column_origin = 7
        column_destination = False
    else:
        column_count = 9
        column_origin = False
        column_destination = 7
    column_comments = column_count-1

    if request.method == 'POST':

        if 'reference_id' in request.POST:
            reference = get_object_or_404(Reference, pk=request.POST['reference_id'])
        else:
            referenceform = ReferenceForm(request.POST)
            if referenceform.is_valid():
                reference = referenceform.save(commit=False)
                reference.status = 'pending'
                reference.save()
                create_record = get_object_or_404(UserAction, pk=1)
                log = UserLog(user=request.user, action=create_record, reference=reference, points=5)

            else:
                error = True

        if not error:

            try:
                reliability = int(request.POST['quality_1'])
                reliability = DQIRating.objects.get(indicator_id=1, score=reliability)
            except ValueError:
                reliability = None

            try:
                completeness = int(request.POST['quality_2'])
                completeness = DQIRating.objects.get(indicator_id=2, score=completeness)
            except ValueError:
                completeness = None

            try:
                geographical_correlation = int(request.POST['quality_4'])
                geographical_correlation = DQIRating.objects.get(indicator_id=3, score=geographical_correlation)
            except ValueError:
                geographical_correlation = None

            try:
                access = int(request.POST['quality_3'])
                access = DQIRating.objects.get(indicator_id=4, score=access)
            except ValueError:
                access = None

            newdataset = Dataset(
                name = request.POST['name'],
                primary_space = info,
                reliability = reliability,
                completeness = completeness, 
                geographical_correlation = geographical_correlation,
                access = access,
                notes = request.POST['notes'],
                replication = request.POST['instructions'],
            )
            newdataset.save()
            csv_file.dataset = newdataset
            csv_file.save()

            newdataset.references.add(reference)
            
            if dataset.name == "Population":
                # Population figures must be linked directly to population topic
                topic = Topic.objects.get(pk=17)
                newdataset.topics.add(topic)

            messages.success(request, 'Information was saved.')

            path = settings.MEDIA_ROOT + '/csv/' + csv_file.name

            materiallist = {}
            timeframelist = {}
            unitlist = {}
            referencespacelist = {}

            with open(path) as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) > 0 and row[0].strip() != "Timeframe" and row[0] and row[0].strip() != "Timeframe name" and row[0].strip() != "Date":

                        if dataset.name == "Population":
                            material = "People"
                            if row[1].strip():
                                material = row[1]
                            material_code = "MF1.5.1"
                            date = row[0]
                            timeframe = row[0]
                            qty = row[2]
                            unit = "unit"
                        elif dataset.type == "stocks":
                            material = row[1].strip()
                            material_code = row[2].strip()
                            date = row[0]
                            timeframe = row[0]
                            qty = row[3]
                            unit = row[4].strip()
                        else:
                            timeframe = row[0]
                            material = row[3].strip()
                            material_code = row[4].strip()
                            start_date = row[1]
                            end_date = row[2]
                            qty = row[5]
                            unit = row[6].strip()

                        if material_code in materiallist:
                            material_info = materiallist[material_code]
                        elif material in materiallist:
                            material_info = materiallist[material]
                        else:
                            if material_code:
                                material_info = Material.objects.filter(code=material_code)
                                material_info = material_info[0]
                                materiallist[material_code] = material_info
                            else:
                                material_info = Material.objects.filter(name=material)
                                material_info = material_info[0]
                                materiallist[material] = material_info

                        if unit:
                            if unit in unitlist:
                                unit_info = unitlist[unit]
                            else:
                                unit_info = Unit.objects.filter(symbol=unit)
                                if unit_info:
                                    unit_info = unit_info[0]
                                else:
                                    unit_info = Unit(
                                        name = unit,
                                        symbol = unit,
                                    )
                                    unit_info.save()
                                unitlist[unit] = unit_info
                        else:
                            unit_info = None

                        if dataset.type == "stocks":
                            if timeframe in timeframelist:
                                timeframe_info = timeframelist[timeframe]
                            else:
                                timeframe_info = TimePeriod.objects.filter(start=parse(date), end__isnull=True)
                                if timeframe_info:
                                    timeframe_info = timeframe_info[0]
                                    timeframelist[timeframe] = timeframe_info
                                else:
                                    timeframe_info = TimePeriod(
                                        start=parse(date),
                                        name=parse(date).strftime('%b %d, %Y'),
                                    )
                                    timeframe_info.save()
                                    timeframelist[timeframe] = timeframe_info

                        else:
                            if timeframe in timeframelist:
                                timeframe_info = timeframelist[timeframe]
                            else:
                                timeframe_info = TimePeriod.objects.filter(start=parse(row[1]), end=parse(row[2]))
                                if timeframe_info:
                                    timeframe_info = timeframe_info[0]
                                    timeframelist[timeframe] = timeframe_info
                                else:
                                    timeframe_info = TimePeriod(
                                        start=parse(row[1]),
                                        end=parse(row[2]),
                                        name=row[0],
                                    )
                                    timeframe_info.save()
                                    timeframelist[timeframe] = timeframe_info

                        destination_info = None
                        if column_destination:
                            destination = row[column_destination].strip()
                            destination_info = None
                            if destination:

                                # We create a dictionary that holds all the query results for each of the names.
                                # Otherwise we'll keep running the same queries if the names repeat
                                # So before we run a query, we check if the query has already been done 

                                if destination in referencespacelist:
                                    destination_info = referencespacelist[destination]
                                else:
                                    destination_info = ReferenceSpace.objects.filter(name=destination)
                                    if destination_info:
                                        # We only want a single result, so slice this
                                        destination_info = destination_info[0]
                                    else:
                                        destination_info = ReferenceSpace(
                                            name = destination,
                                            type = dataset.destination_reference_type,
                                            city = info,
                                            country = info.country,
                                        )
                                        destination_info.save()

                                        create_record = get_object_or_404(UserAction, pk=1)
                                        log = UserLog(user=request.user, action=create_record, space=origin_info, points=0)
                                        log.save()
                                    referencespacelist[destination] = destination_info

                        origin_info = None
                        if column_origin:
                            # We'll do the exact same thing with origin as we did with destination
                            origin = row[column_origin].strip()
                            origin_info = None
                            if origin:
                                if origin in referencespacelist:
                                    origin_info = referencespacelist[origin]
                                else:
                                    origin_info = ReferenceSpace.objects.filter(name=origin)
                                    if origin_info:
                                        origin_info = origin_info[0]
                                    else:
                                        origin_info = ReferenceSpace(
                                            name = origin,
                                            type = dataset.origin_reference_type,
                                            city = info,
                                            country = info.country,
                                        )
                                        origin_info.save()

                                        create_record = get_object_or_404(UserAction, pk=1)
                                        log = UserLog(user=request.user, action=create_record, space=origin_info, points=0)
                                        log.save()

                                    referencespacelist[origin] = origin_info

                        try:
                            quantity = float(qty.replace(',',''))
                        except ValueError:
                            quantity = None

                        try:
                            comments = row[column_comments]
                        except ValueError:
                            comments = None
                        data = Data(
                            quantity = quantity,
                            unit = unit_info,
                            material = material_info,
                            material_name = material,
                            dataset = newdataset,
                            origin_space = origin_info,
                            destination_space = destination_info,
                            timeframe = timeframe_info,
                            origin = dataset.origin_process,
                            destination = dataset.destination_process,
                            csv = csv_file,
                            comments = comments,
                        )

                        data.save()

            csv_file.imported = True
            csv_file.save()

            # Temporary redirect for video
            # return redirect('http://localhost:8000/cities/cape-town/resources/water/water-treatment-works/faure')

            return redirect('multiplicity:dataset', id=newdataset.id, city=info.slug)

        else:
            messages.warning(request, 'We could not save your form, please correct the errors')

    datasetform = DatasetForm(request.POST or None, instance=info)
    referenceform = ReferenceForm(initial={'type': 16, 'language': 'EN'})
    dqi = DQI.objects.all
    topics = Topic.objects.exclude(position=0).filter(parent__isnull=True)
    context = { 'section': 'cities', 'menu': 'upload', 'file': csv_file, 'info': info, 'type': dataset.type, 'dataset': dataset, 'datasetform': datasetform, 'referenceform': referenceform, 'dqi': dqi, 'topics': topics }
    return render(request, 'multiplicity/upload/flow.meta.html', context)


@login_required
def upload_systemboundaries(request, city):
    info = get_object_or_404(ReferenceSpace, slug=city)
    locations = ReferenceSpaceLocation.objects.filter(space=info).order_by('name')
    context = { 'section': 'cities', 'menu': 'upload', 'info': info, 'locations': locations }
    return render(request, 'multiplicity/upload/systemboundaries.html', context)


@login_required
def upload_systemboundary(request, city, location=False):
    if location:
            location = ReferenceSpaceLocation.objects.get(pk=location)

    info = get_object_or_404(ReferenceSpace, slug=city)

    Form = modelform_factory(ReferenceSpaceLocation, 
        fields=('name', 'source', 'timeframe', 'description', 'geojson'),
        labels={"lat": "Latitude", "lng": "Longitude"}
    )
    if request.method == 'POST':
        if location:
            form = Form(request.POST, request.FILES, instance=location)
        else:
            form = Form(request.POST, request.FILES)
        if form.is_valid():
            boundary = form.save(commit=False)
            boundary.space = info
            boundary.save()
            messages.success(request, 'The boundaries have been saved.')
            return redirect(reverse('multiplicity:map', args=[info.slug, boundary.id]))
        else:
            messages.warning(request, 'We could not save your form, please correct the errors')

    else:
        if location:
            form = Form(instance=location)
        else:
            form = Form()

    locations = ReferenceSpaceLocation.objects.filter(space=info).order_by('name')
    context = { 'section': 'cities', 'menu': 'upload', 'info': info, 'locations': locations, 'form': form }
    return render(request, 'multiplicity/upload/systemboundary.html', context)

@login_required
def upload_mtu(request, city):
    info = get_object_or_404(ReferenceSpace, slug=city)
    if 'file' in request.FILES:
        file = request.FILES['file']
        filename = str(uuid.uuid4())
        path = settings.MEDIA_ROOT + '/json/' + filename

        with open(path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        return redirect(reverse('multiplicity:upload_mtu_review', args=[info.slug, filename]))

    context = { 'section': 'cities', 'menu': 'upload', 'info': info }
    return render(request, 'multiplicity/upload/mtu.html', context)

@login_required
def upload_mtu_review(request, city, filename):
    info = get_object_or_404(ReferenceSpace, slug=city)

    path = settings.MEDIA_ROOT + '/json/' + filename

    try:
        with open(path) as json_data:
            data = json.load(json_data)
    except:
        import os
        try:
            os.remove(path)
            error = "Your geojson file is invalid. Please verify that this is a correct geojson file. You can try validating it on <a href='http://http://geojson.io/'>geojson.io</a>"
        except:
            error = "Invalid link; use the form below to load your geojson file."
        messages.error(request, error)
        return redirect(reverse("multiplicity:upload_mtu", args=[info.slug]))

    if data:
        error = False

        if request.method == 'POST':
            create_record = get_object_or_404(UserAction, pk=1)
            import_data = get_object_or_404(UserAction, pk=6)

            log = UserLog.objects.create(user=request.user, action=import_data, space=info, points=10, model="MTU geojson", description="File: " + filename)

            type = ReferenceSpaceType.objects.filter(name=request.POST['mtu_name'])
            if type:
                type = type[0]
            else:
                type = ReferenceSpaceType.objects.filter(slug=slugify(request.POST['mtu_name']))
                if type:
                    type = type[0]
                else:
                    type = ReferenceSpaceType.objects.create(name=request.POST['mtu_name'], slug=slugify(request.POST['mtu_name']), type='SOC', marker_color=None, user_accessible=False)

            mtu = MTU.objects.create(type=type, space=info, timeframe=request.POST['timeframe'], source=request.POST['source'], file=filename, description=request.POST['details'])

        for record in data['features']:
            properties = record['properties']
            geometry = record['geometry']

            if request.method == 'POST':
                name = properties[request.POST['name']]
                area = None
                if 'area' in request.POST:
                    area = float(properties[request.POST['area']])/float(request.POST['unit'])

                space = ReferenceSpace.objects.create(name=name, type=type, city=info, country=info.country, slug=slugify(name), mtu=mtu)
                location = ReferenceSpaceLocation.objects.create(space=space, area=area, timeframe=request.POST['timeframe'], source=request.POST['source'], geojson=geometry)
                space.location = location
                space.save()

                log = UserLog.objects.create(user=request.user, action=create_record, space=space, points=0)

        if request.method == 'POST':
            return redirect(reverse('multiplicity:map_mtu', args=[info.slug, type.slug]))


        if 'crs' in data and 'properties' in data['crs'] and 'name' in data['crs']['properties']:
            projection = data['crs']['properties']['name']
        else:
            # If the projection is not set we must alert the user
            projection = "unknown"

    context = { 
        'section': 'cities', 'menu': 'upload', 'info': info, 'properties': properties, 'geometry': geometry,
        'filename': filename, 'map': True, 'projection': projection, 'error': error
    }
    return render(request, 'multiplicity/upload/mtu.review.html', context)


@login_required
def reference_form(request, city, type):
    info = get_object_or_404(ReferenceSpace, slug=city)
    if 'file' in request.FILES:
        file = request.FILES['file']
        filename = str(uuid.uuid4())
        path = settings.MEDIA_ROOT + '/json/' + filename

        with open(path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        return redirect(reverse('multiplicity:upload_mtu_review', args=[info.slug, filename]))

    context = { 'section': 'cities', 'menu': 'upload', 'info': info }
    return render(request, 'multiplicity/upload/mtu.html', context)

def infrastructure_list(request, topic, city):
    info = get_object_or_404(ReferenceSpace, slug=city)
    topic = get_object_or_404(Topic, slug=topic)
    spaces = ReferenceSpace.objects.filter(city=info, type__topic=topic)
    types = ReferenceSpaceType.objects.filter(topic=topic).annotate(total=Count('referencespace'))
    # TODO Surely we can do better than this? A single db query should be possible.
    topics = Topic.objects.exclude(position=0).filter(parent__isnull=True)
    count = {}
    for details in spaces:
        if details.type.id in count:
            count[details.type.id] += 1
        else:
            count[details.type.id] = 1
    context = { 'section': 'cities', 'menu': 'infrastructure', 'page': topic.slug, 'info': info, 'topic': topic, 'spaces': spaces, 'types': types, 'count': count, 'tab': 'overview', 'topics': topics}
    return render(request, 'multiplicity/topic.html', context)

def detail(request, slug):
    topics = Topic.objects.exclude(position=0).filter(parent__isnull=True)
    topic = Topic.objects.get(pk=2)
    info = get_object_or_404(ReferenceSpace, slug=slug)
    types = ReferenceSpaceType.objects.annotate(total=Count('referencespace', filter=Q(referencespace__city=info))).filter(total__gte=1).exclude(pk=8)
    references = Reference.objects.filter(status='active', tags=info.tag).order_by('-id')[:5]
    datasets_stocks = Dataset.objects.filter(primary_space=info, type__type='stocks').order_by('-id')[:5]
    datasets_flows = Dataset.objects.filter(primary_space=info, type__type='flows').order_by('-id')[:5]

    editlink = reverse("multiplicity:admin_referencespace", args=[info.type.slug, info.id])

    context = {
        'section': 'cities', 
        'info' : info,
        'menu' : 'dashboard',
        'topics': topics,
        'types': types, 
        'topic': topic,
        'editlink': editlink,
        'references': references,
        'datasets_flows': datasets_flows,
        'datasets_stocks': datasets_stocks,
    }
    return render(request, 'multiplicity/index.html', context)

def research(request, city):
    info = get_object_or_404(ReferenceSpace, slug=city)
    context = {
        'section': 'cities', 
        'info' : info,
        'menu' : 'research',
        'page' : 'overview',
    }
    return render(request, 'multiplicity/research.html', context)

def datasetlist(request):
    list = DatasetType.objects.all()
    context = { 'section': 'cities', 'menu': 'dashboard', 'list': list}
    return render(request, 'multiplicity/contribute.dataset.list.html', context)

def upload(request, city):
    topics = Topic.objects.exclude(position=0).filter(parent__isnull=True)
    info = get_object_or_404(ReferenceSpace, slug=city)
    context = { 'section': 'cities', 'menu': 'upload', 'page': 'upload', 'info': info, 'list': list, 'topics': topics}
    return render(request, 'multiplicity/upload/index.html', context)

def topic(request, city, topic, main=False, tab=False):
    topics = Topic.objects.exclude(position=0).filter(parent__isnull=True)
    topic = get_object_or_404(Topic, slug=topic)
    #datasets = Dataset.objects.filter(data__material__in=topic.materials.all())
    info = get_object_or_404(ReferenceSpace, slug=city)
    information = Information.objects.filter(topic=topic, space=info)
    if information:
        information = information[0]
    datasets = Dataset.objects.filter(topics=topic, primary_space=info)

    context = { 'section': 'cities', 'menu': 'profile', 'info': info, 'page': topic.slug, 'topic': topic, 'datasets': datasets, 'information': information }
    return render(request, 'multiplicity/topic.html', context)

def materials(request, catalog=False):
    if catalog == "hs":
        list = Material.objects.filter(catalog_id=1).order_by('id')
        title = "Harmonized system"
    elif catalog == "elements":
        list = Material.objects.filter(catalog_id=3).order_by('id')
        title = "Elements"
    elif catalog == "em":
        list = Material.objects.filter(catalog_id=2).order_by('id')
        title = "Engineering materials"
    else:
        list = Material.objects.filter(catalog_id=4).exclude(id=970921).order_by('id')
        title = "Eurostat catalog"
    context = { 'section': 'cites', 'menu': 'dashboard', 'list': list, 'datatables': True, 'title': title, 'type': catalog }
    return render(request, 'multiplicity/materials.html', context)

@login_required
def information_form(request, city, id=False, topic=False):

    info = get_object_or_404(ReferenceSpace, slug=city)
    processes = Process.objects.filter(slug__isnull=False).order_by('id')
    references = Reference.objects.filter(status='active')

    if topic:
        topic = Topic.objects.get(pk=topic)
        information = Information.objects.filter(topic=topic, space=info)
        if information:
            id = information[0].id

    if id:
        information = get_object_or_404(Information, pk=id)
        form = InformationForm(instance=information)
        if information.topic:
            topic = information.topic
    else:
        information = False
        form = InformationForm()
    saved = False

    if request.method == 'POST':
        if not id:
            form = InformationForm(request.POST, request.FILES)
        else:
            form = InformationForm(request.POST, request.FILES, instance=information)
        if form.is_valid():
            if not topic and request.POST['process']:
                process = Process.objects.get(pk=request.POST['process'])
            else:
                process = None
            if id:
                information = form.save()
                information.process = process
                information.save()
            else:
                information = form.save(commit=False)
                information.process = process
                information.space = info
                information.user = request.user
                if topic:
                    information.topic = topic
                information.save()

                form.save_m2m()

            information.references.clear()

            selected = request.POST.getlist('references')
            for reference in selected:
                information.references.add(Reference.objects.get(pk=reference))

            saved = True
            messages.success(request, 'Information was saved.')
            return redirect(reverse('multiplicity:information_form', args=[info.slug, information.id]))
        else:
            messages.warning(request, 'We could not save your form, please correct the errors')

    context = { 'section': 'cities', 'info': info, 'form': form, 'type': type, 'tinymce': True, 'processes': processes, 'information': information,
    'references': references, 'select2': True, 'topic': topic
    }
    return render(request, 'multiplicity/form.information.html', context)

@login_required
def photo_form(request, city, id=False, map=False):
    info = get_object_or_404(ReferenceSpace, slug=city)
    processes = Process.objects.filter(slug__isnull=False).order_by('id')
    if id:
        photo = get_object_or_404(Photo, pk=id)
        form = PhotoForm(instance=photo)
    else:
        photo = False
        form = PhotoForm()
    saved = False
    if request.method == 'POST':
        if not id:
            form = PhotoForm(request.POST, request.FILES)
        else:
            form = PhotoForm(request.POST, request.FILES, instance=photo)
        if form.is_valid():
            if request.POST['process']:
                process = Process.objects.get(pk=request.POST['process'])
            else:
                process = None
            photo = form.save(commit=False)
            photo.primary_space = info
            photo.uploaded_by = request.user
            photo.process = process
            if map:
                photo.type = 'map'
            else:
                photo.type = 'photo'
            photo.save()
            saved = True
            messages.success(request, 'Image was saved.')
            if not id:
                record_type = get_object_or_404(UserAction, pk=1)
                points = 3
            else:
                record_type = get_object_or_404(UserAction, pk=2)
                points = 0
            log = UserLog.objects.create(user=request.user, action=record_type, space=photo.primary_space, points=points, model="Photo", model_id=photo.id)

            if map:
                return redirect(reverse('multiplicity:map_other', args=[info.slug]))
            else:
                return redirect(reverse('multiplicity:photos', args=[info.slug]))
        else:
            messages.warning(request, 'We could not save your form, please correct the errors')

    if map:
        title = 'Map'
    else:
        title = 'Photo'

    context = { 'section': 'cities', 'info': info, 'form': form, 'type': type, 'processes': processes, 'photo': photo, 'select2': True,
    'map': map, 'menu': 'upload', 'title': title }
    return render(request, 'multiplicity/form.photo.html', context)


@login_required
def upload_video(request, city, id=False, space=False):
    info = get_object_or_404(ReferenceSpace, slug=city)
    processes = Process.objects.filter(slug__isnull=False).order_by('id')
    if id:
        video = get_object_or_404(Video, pk=id)
        form = VideoUploadForm(instance=video)
    else:
        video = False
        form = VideoUploadForm()
    saved = False
    if request.method == 'POST':
        if not id:
            form = VideoUploadForm(request.POST, request.FILES)
        else:
            form = VideoUploadForm(request.POST, request.FILES, instance=video)
        if form.is_valid():
            if request.POST['process']:
                process = Process.objects.get(pk=request.POST['process'])
            else:
                process = None
            video = form.save(commit=False)
            if request.POST['primary_space']:
                video.primary_space = get_object_or_404(ReferenceSpace, pk=request.POST['primary_space'])
            video.process = process
            url = video.url
            video.url = url.rsplit('/', 1)[-1]
            video.save()
            saved = True
            messages.success(request, 'Video was saved.')
            if not id:
                record_type = get_object_or_404(UserAction, pk=1)
                points = 3
            else:
                record_type = get_object_or_404(UserAction, pk=2)
                points = 0
            log = UserLog.objects.create(user=request.user, action=record_type, space=video.primary_space, points=points, model="Video", model_id=video.id)

            if video.primary_space:
                return redirect_space(request, video.primary_space.id)
            else:
                return redirect_space(request, info.id)
        else:
            messages.warning(request, 'We could not save your form, please correct the errors')

    context = { 
        'section': 'cities', 'info': info, 'form': form, 
        'type': type, 'processes': processes, 'video': video, 'select2': True,
        'menu': 'upload' 
    }
    return render(request, 'multiplicity/upload/video.html', context)


# Admin

def redirect_space(request, id):
    info = get_object_or_404(ReferenceSpace, pk=id)
    if info.city:
        link = reverse('multiplicity:space', kwargs={
            'city': info.city.slug,
            'type': info.type.slug,
            'space': info.slug,
            })
    else:
        link = reverse('multiplicity:city', kwargs={'slug': info.slug})
    return redirect(link)

@staff_member_required
def admin_referencespaces(request, type):
    type = ReferenceSpaceType.objects.get(slug=type)
    list = ReferenceSpace.objects.filter(type=type)
    context = { 'navbar': 'backend', 'list': list, 'datatables': True, 'type': type }
    return render(request, 'multiplicity/admin/referencespaces.html', context)

@staff_member_required
def admin_referencespace(request, type, id=False):
    type = ReferenceSpaceType.objects.get(slug=type)
    if id:
        info = get_object_or_404(ReferenceSpace, pk=id)
        form = ReferenceSpaceForm(instance=info)
    else:
        info = False
        form = ReferenceSpaceForm()
    saved = False
    if request.method == 'POST':
        if not id:
            form = ReferenceSpaceForm(request.POST, request.FILES)
        else:
            form = ReferenceSpaceForm(request.POST, request.FILES, instance=info)
        if form.is_valid():
            info = form.save()
            saved = True
            messages.success(request, 'Information was saved.')
            return redirect(reverse('multiplicity:admin_referencespace', args=[info.type.slug, info.id]))
        else:
            messages.warning(request, 'We could not save your form, please correct the errors')

    context = { 'navbar': 'backend', 'info': info, 'form': form, 'type': type }
    return render(request, 'multiplicity/admin/referencespace.html', context)

@staff_member_required
def admin_locations(request):
    list = ReferenceSpaceLocation.objects.filter(type__id=3)
    context = { 'navbar': 'backend', 'list': list, 'datatables': True }
    return render(request, 'multiplicity/admin/locations.html', context)

@staff_member_required
def admin_location(request, id=False, referencespace=False, type=False):
    if type:
        type = ReferenceSpaceType.objects.get(slug=type)
    if referencespace:
        referencespace = get_object_or_404(ReferenceSpace, pk=referencespace)
        type = referencespace.type
    if id:
        info = get_object_or_404(ReferenceSpaceLocation, pk=id)
        form = ReferenceSpaceLocationForm(instance=info)
        type = info.space.type
    else:
        info = False
        form = ReferenceSpaceLocationForm()
    saved = False
    if request.method == 'POST':
        if not id:
            form = ReferenceSpaceLocationForm(request.POST)
        else:
            form = ReferenceSpaceLocationForm(request.POST, instance=info)
        if form.is_valid():
            info = form.save(commit=False)
            saved = True
            messages.success(request, 'Information was saved.')
            if referencespace:
                info.space = referencespace
            info.save()
            if referencespace:
                referencespace.location = info
                referencespace.save()

            return redirect(reverse('multiplicity:admin_location', args=[info.id]))
        else:
            messages.warning(request, 'We could not save your form, please correct the errors')

    context = { 'navbar': 'backend', 'info': info, 'form': form, 'referencespace': referencespace, 'type': type }
    return render(request, 'multiplicity/admin/location.html', context)


@staff_member_required
def admin_data_overview(request, city):
    info = get_object_or_404(ReferenceSpace, slug=city)
    datasets = Dataset.objects.filter(primary_space=info, deleted=False)
    csv = CSV.objects.filter(space=info)
    space_csv = ReferenceSpaceCSV.objects.filter(space=info)
    spaces = ReferenceSpace.objects.filter(city=info)
    photos = Photo.objects.filter(primary_space=info)
    information = Information.objects.filter(space=info)
    context = { 'navbar': 'backend', 'info': info, 'datasets': datasets, 'csv': csv, 'space_csv': space_csv, 'datatables': True, 
    'information': information, 'spaces': spaces, 'photos': photos }
    return render(request, 'multiplicity/admin/overview.data.html', context)

@staff_member_required
def delete_dataset(request, city, id):
    info = get_object_or_404(ReferenceSpace, slug=city)
    dataset = get_object_or_404(Dataset, pk=id)
    dataset.deleted = True
    dataset.save()
    messages.success(request, 'Dataset was deleted')
    return redirect('multiplicity:admin_data_overview', city=city)

@staff_member_required
def admin_datasettypes(request):
    list = DatasetType.objects.filter(active=True)
    context = { 'navbar': 'backend', 'list': list, 'datatables': True }
    return render(request, 'multiplicity/admin/datasettypes.html', context)

@staff_member_required
def admin_datasettype(request, id=False):
    if id:
        info = get_object_or_404(DatasetType, pk=id)
        form = DatasetTypeForm(instance=info)
    else:
        info = False
        form = DatasetTypeForm()
    saved = False
    if request.method == 'POST':
        if not id:
            form = DatasetTypeForm(request.POST, request.FILES)
        else:
            form = DatasetTypeForm(request.POST, request.FILES, instance=info)
        if form.is_valid():
            info = form.save()
            saved = True
            messages.success(request, 'Information was saved.')
            return redirect(reverse('multiplicity:admin_datasettypes'))
        else:
            messages.warning(request, 'We could not save your form, please correct the errors')

    context = { 'navbar': 'backend', 'info': info, 'form': form, 'type': type }
    return render(request, 'multiplicity/admin/datasettype.html', context)

@staff_member_required
def admin_referencephoto(request, id=False):
    if id:
        info = get_object_or_404(ReferencePhoto, pk=id)
        form = ReferencePhotoForm(instance=info)
    else:
        info = False
        form = ReferencePhotoForm()
    saved = False
    if request.method == 'POST':
        if not id:
            form = ReferencePhotoForm(request.POST)
        else:
            form = ReferencePhotoForm(request.POST, instance=info)
        if form.is_valid():
            info = form.save()
            saved = True
            messages.success(request, 'Information was saved.')
            return redirect(reverse('multiplicity:admin_datasettypes'))
        else:
            messages.warning(request, 'We could not save your form, please correct the errors')

    context = { 'navbar': 'backend', 'info': info, 'form': form }
    return render(request, 'multiplicity/admin/referencephoto.html', context)

def temp_slide(request, city):
    info = get_object_or_404(ReferenceSpace, slug=city)
    context = { 'section': 'cites', 'menu': 'dashboard', 'info': info }
    return render(request, 'multiplicity/slide.html', context)


