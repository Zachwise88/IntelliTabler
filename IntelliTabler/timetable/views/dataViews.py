from django.shortcuts import get_object_or_404, render, redirect
from ..models import Department, Teacher, Module, ModuleGroup
from django.contrib.auth.decorators import login_required
from django.apps import apps



def index(request):
    return render(request, "index.html")

@login_required
def departments(request):
    return render(request, "data/departments.html")

@login_required
def departmentChange(request):
    context={}
    departments=Department.objects.filter(user=request.user)
    context["entities"]=departments
    return render(request, "data/sideBarList.html", context)

@login_required
def teachers(request):
    return render(request, "data/teachers.html")

@login_required
def teacherChange(request):
    context={}
    teachers=Teacher.objects.filter(user=request.user)
    context["entities"]=teachers
    return render(request, "data/sideBarList.html", context)

@login_required
def viewObjects(request, type, id=0):
    context={}
    Type = apps.get_model(app_label='timetable', model_name=type)
    if id==0:
        id=request.GET.get('id', 0)
    if(id):
        objects=Type.objects.filter(user=request.user, department_id=id)
    else:
        objects=Type.objects.filter(user=request.user)
    context['type']= type
    context["entities"]=objects
    context["objectId"]=id
    return render(request, "data/sideBarList.html", context)

@login_required
def viewModules(request, type, departmentId, id=0):
    context={}
    Type = apps.get_model(app_label='timetable', model_name=type)
    if id==0:
        id=request.GET.get('id', 0)
    if(id):
        objects=Type.objects.filter(user=request.user, year=id)
    else:
        objects=Type.objects.filter(department_id=departmentId)
    context['type']= type
    context["entities"]=objects
    context["departmentId"]=departmentId
    context["yearId"]=id
    return render(request, "data/modulesList.html", context)

def modules(request, departmentId):
    context={}
    modules=ModuleGroup.objects.filter(department=departmentId)
    years=set()
    for mod in modules:
        years.add(mod.year)
        if(mod.year not in context):
            context[mod.year]=[]
        context[mod.year].append(mod)
    context["years"]=years
    context["departmentId"]=departmentId
    return render(request, "data/modules.html", context)



def getTeacher(request, id=0):
    if id==0:
        id=request.GET.get('id', 0)
    try: 
        teacher=Teacher.objects.get(id=id)
    except:
        teacher=None
    context={}
    context["teacher"]=teacher
    return render(request, "data/teacherInfo.html", context)

def getModules(request, id=0):
    if id==0:
        id=request.GET.get('id', 0)        
    moduleList=Module.objects.filter(group_id=id)
    context={}
    modules={}
    for mod in moduleList:
        if mod.groupNum not in modules:
            modules[mod.groupNum]=[]
        modules[mod.groupNum].append(mod)
    context["modules"]=modules
    return render(request, "data/modulesInfo.html", context)