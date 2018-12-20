from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

from .models import Material, Process, Unit, Dataset, DatasetForm, CSV, MaterialForm, ProcessForm, Data
from core.models import Reference
from multiplicity.models import ReferenceSpace, DatasetType, ProcessGroup
from django.contrib.auth.decorators import login_required

# For file uploads
import uuid
import csv
from django.conf import settings
from collections import defaultdict

from django.http import JsonResponse

@login_required
def index(request):
    context = { 'section': 'data', 'menu': 'index' }
    return render(request, 'staf/index.html', context)

@login_required
def search(request):
    data = Data.objects.all()
    context = { 'section': 'resources', 'menu': 'search', 'data': data, 'datatables': True }
    return render(request, 'staf/search.html', context)

@login_required
def processgroups(request):
    list = ProcessGroup.objects.order_by('name')
    context = { 'list': list, 'datatables': True }
    return render(request, 'staf/processgroup.list.html', context)

@login_required
def processgroup(request, id):
    info = ProcessGroup.objects.get(pk=id)
    context = { 'info': info }
    return render(request, 'staf/processgroup.html', context)

@login_required
def materiallist(request, id=False):
    if id:
        materials = Material.objects.filter(parent=id).order_by('code')
    else:
        materials = Material.objects.filter(parent__isnull=True).order_by('code')
    context = { 'section': 'data', 'menu': 'materials', 'materials': materials}
    return render(request, 'staf/material.list.html', context)

@login_required
def materialform(request, id=False):
    if id:
        info = Material.objects.get(id=id)
        form = MaterialForm(request.POST or None, instance=info)
        menu = 'materials'
        page = 'create'
    else:
        info = False
        form = MaterialForm(request.POST or None)
        menu = 'materials'
        page = 'create'
    if form.is_valid():
        info = form.save()

    context = { 'section': 'data', 'menu': menu,'form': form, 'info': info, 'page': page }
    return render(request, 'staf/materialform.html', context)

@login_required
def materialchild(request, id):
    parent = Material.objects.get(id=id)
    info = False
    form = MaterialForm(request.POST or None)
    menu = 'materials'
    page = 'create'
    success = False

    if form.is_valid():
        success = True
        info = form.save(commit=False)
        info.parent = parent
        info.save()

    context = { 'section': 'data', 'menu': menu,'form': form, 'info': info, 'page': page, 'parent': parent, 'success': success }
    return render(request, 'staf/materialform.html', context)

@login_required
def materiallistajax(request, id=False):
    if request.GET.get('parent'):
        materials = Material.objects.filter(parent=request.GET['parent']).order_by('code')
    else:
        materials = Material.objects.filter(parent__isnull=True).order_by('code')
    list = []
    for details in materials:
        d = {}
        if details.code:
            d['title'] = details.code + ' - ' + details.name
        else:
            d['title'] = details.name
        d['lazy'] = True
        d['key'] = details.id
        if details.is_separator:
            d['folder'] = True
        list.append(d)
    return JsonResponse(list, safe=False)

@login_required
def processlist(request, id=False):
    if id:
        processes = Process.objects.filter(parent=id).order_by('name')
    else:
        processes = Process.objects.filter(parent__isnull=True).order_by('name')
    context = { 'section': 'data', 'menu': 'processes', 'processes': processes}
    return render(request, 'staf/process.list.html', context)

@login_required
def processtable(request, id=False):
    processes = Process.objects.order_by('id')
    context = { 'section': 'data', 'menu': 'processes', 'processes': processes, 'datatables': True}
    return render(request, 'staf/process.table.html', context)

@login_required
def processform(request, id=False):
    if id:
        info = Process.objects.get(id=id)
        form = ProcessForm(request.POST or None, instance=info)
        menu = 'processes'
        page = 'create'
    else:
        info = False
        form = ProcessForm(request.POST or None)
        menu = 'processes'
        page = 'create'
    if form.is_valid():
        info = form.save()

    context = { 'section': 'data', 'menu': menu,'form': form, 'info': info, 'page': page }
    return render(request, 'staf/processform.html', context)

@login_required
def processchild(request, id):
    parent = Process.objects.get(id=id)
    info = False
    form = ProcessForm(initial={'parent': parent})
    menu = 'processes'
    page = 'create'
    success = False

    if form.is_valid():
        success = True
        info = form.save(commit=False)
        info.parent = parent
        info.save()

    context = { 'section': 'data', 'menu': menu,'form': form, 'info': info, 'page': page, 'parent': parent, 'success': success }
    return render(request, 'staf/processform.html', context)

@login_required
def processlistajax(request, id=False):
    if request.GET.get('parent'):
        processes = Process.objects.filter(parent=request.GET['parent']).order_by('name')
    else:
        processes = Process.objects.filter(parent__isnull=True).order_by('name')
    list = []
    for details in processes:
        d = {}
        d['title'] = details.name
        d['lazy'] = True
        d['key'] = details.id
        if details.is_separator:
            d['folder'] = True
        list.append(d)
    return JsonResponse(list, safe=False)

@login_required
def processlisting(request, id=False):
    if id:
        processes = Process.objects.filter(parent=id)
        ancestors = Process.objects.filter(tree_process__ancestors__contains=[id])
        ancestors = Process.objects.filter(pk__in=Process.objects.get(pk=id).tree_process.ancestors)
        home = False
        info = get_object_or_404(Process, pk=id)
        tree = {}
        margin = {}
    else:
        processes = Process.objects.filter(parent__isnull=True)
        ancestors = []
        home = True
        info = False
        tree = Process.objects.filter(tree_process__root=92)
        margin = {}
        for details in tree:
            if details.parent:
                if details.parent.id in margin:
                    margin[details.id] = margin[details.parent.id]+20
                else:
                    margin[details.id] = 10
    context = { 'section': 'data', 'menu': 'processes', 'processes': processes, 'ancestors': ancestors, 'home': home, 'info': info, 'tree': tree, 'margin': margin}
    return render(request, 'staf/process.browser.html', context)

@login_required
def processtree(request):
    tree = Process.objects.filter(tree_process__root=92)
    context = { 'section': 'tools', 'menu': 'staf', 'tree': tree}
    return render(request, 'staf/process.tree.html', context)

@login_required
def units(request):
    list = Unit.objects.all()
    context = { 'section': 'tools', 'menu': 'staf', 'list': list}
    return render(request, 'staf/unit.list.html', context)

@login_required
def unit(request, id):
    info = get_object_or_404(Unit, pk=id)
    context = { 'section': 'tools', 'menu': 'staf', 'info': info}
    return render(request, 'staf/unit.html', context)

@login_required
def datasets(request):
    list = Dataset.objects.all()
    context = { 'section': 'data', 'menu': 'datasets', 'list': list}
    return render(request, 'staf/datasets.html', context)
