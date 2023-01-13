from django.urls import reverse
from django.http import HttpResponse
from ..forms import *
from ..models import *
from django.forms import formset_factory
from django.shortcuts import get_object_or_404, render, redirect
from django.apps import apps

# Create your views here.
def addDepartment(request):
    if request.method == "POST":
        departmentform = DepartmentForm(request.POST, request.FILES)
        formatform = FormatForm(request.POST, request.FILES)
        if departmentform.is_valid() and formatform.is_valid:
            newdepartment=departmentform.save(commit=False)
            #newdepartment.user=1
            new_format = formatform.save(commit=False)
            new_format.department=newdepartment
            newdepartment.user=request.user
            newdepartment.save()
            new_format.save()
            return HttpResponse(status=204, headers={'HX-Trigger':'departmentChange'})
    else:
        departmentform=DepartmentForm()
        formatform=FormatForm()
    context={
        "departmentform": departmentform,
        "formatform": formatform
    }
    return render(request, 'forms/departmentForm.html',context)

def addTeacher(request, department, id=0):
    if request.method=="POST":
        Teacher.objects.filter(pk=0).delete()
        teacher, created=Teacher.objects.get_or_create(id=request.POST['id'], user=request.user, department_id=department)
        Teacher.objects.filter(pk=0).delete()
        form = TeacherForm(request.POST, instance=teacher)
        if(form.is_valid()):
            print(teacher)
            newTeacher=form.cleaned_data
            newTeacher["user"]=request.user
            newTeacher["department"]=Department.objects.get(id=department)
            teacher.save()
            #Teacher.objects.delete(id=0)
            if(not created):
                return HttpResponse(status=204, headers={'HX-Trigger':'teacherDetailChange', 'Department':department})
            return HttpResponse(status=204, headers={'HX-Trigger':'teacherChange', 'Department':department})
            
    else:
        if(id!=0):
            teacher=get_object_or_404(Teacher, pk=id)
            form=TeacherForm(instance=teacher)
        else:     
            form = TeacherForm(initial={"id":0})
    context={'form':form}
    context['Operation']="Add or Edit Teacher"
    return render(request, 'forms/modalForm.html', context)

def setAvailability(request, teacherid):
    context={}
    context['teacher']=Teacher.objects.get(id=teacherid)
    ft=context['teacher'].department.format
    periods=Period.objects.values_list().filter(department=context['teacher'].department)
    period1=periods[1]
    extra=ft.numPeriods*5
    formsets=[]

    availabilityFormSet = formset_factory(AvailabilityForm, extra=extra)
    if request.method=='POST':
        for w in range(ft.numWeeks):
            formset1 = availabilityFormSet(request.POST, prefix="week-"+str(w))
            if formset1.is_valid():
                i=0
                Availability.objects.filter(teacher=teacherid).filter(week=w+1).delete()
                for f in formset1:
                    cd = f.cleaned_data
                    checked = cd.get('checked')
                    if(checked):
                        newperiod=Availability()
                        newperiod.period=cd.get('period')
                        newperiod.week=cd.get('week')
                        newperiod.teacher=Teacher.objects.get(id=teacherid)
                        newperiod.save()
                    i=i+1
                valid=True
            else:
                valid=False
            formsets.append(formset1)
        if valid==True:
            return redirect(reverse('departments'))
    else:
        for w in range(ft.numWeeks):
            formsets.append(availabilityFormSet(prefix="week-"+str(w)))
        #formset2 = availabilityFormSet(prefix="week2")
    
    currentQuery=Availability.objects.filter(teacher=teacherid)
    current = []
    for c in currentQuery:
        current.append(str(c.week)+"-"+c.period)

    #hours=Teacher.objects.values_list('totalHours', flat=True).get(id=teacherid)
    #context['hours']=hours
    context['current']=current
    context['periods']=periods
    #context['formset1']=formset1
    context['formsets']=formsets
    context['weeks']=ft.numWeeks
    context['periodpw']=ft.numPeriods*5
    #context['formset2']=formset2
    return render(request, 'forms/availabilityForm.html', context)


def addModule(request, year):
    department=Year.objects.get(id=year).department
    if request.method=='POST':
        form=ModuleGroupForm(request.POST, request.FILES)
        if form.is_valid():
            group=form.save(commit=False)
            group.year_id=year
            group.department=department
            group.user=request.user
            group.save()
            return HttpResponse(status=204, headers={'HX-Trigger':'moduleChange'})
    form=ModuleGroupForm()
    context={}
    context['form']=form
    context['Operation']="Add Modules"
    return render (request, "forms/modalForm.html", context)

def addYear(request, departmentId):
    
    if request.method=='POST':
        form=YearForm(request.POST, request.FILES)
        if form.is_valid():
            year=form.save(commit=False)
            year.department_id=departmentId
            year.save()
            return HttpResponse(status=204, headers={'HX-Trigger':'yearChange'})
    else:
        form=YearForm()
    context={}
    context['form']=form
    context['departmentId']=departmentId
    context['Operation']="Add Year"
    return render(request, "forms/modalForm.html", context)

def assignTeacher(request, departmentId, moduleId):
    choices=[]
    teachers=Teacher.objects.filter(department_id=departmentId)
    for teacher in teachers:
        choices.append((teacher.id, teacher.name))
    if request.method=='POST':
        form=AssignTeacherForm(choices, request.POST, request.FILES)
        if form.is_valid():
            test=form.cleaned_data
            mod= Module.objects.get(id=moduleId)
            id=form.cleaned_data['teacher']
            mod.teacher_id=int(id)
            mod.save()
            return HttpResponse(status=204, headers={'HX-Trigger':'moduleDetailsChange'})
    form=AssignTeacherForm(choices)
    context={'form':form}
    context['Operation']="Assign Teacher"
    return render(request, 'forms/modalForm.html', context)

def assignPeriod(request, department, group, groupNum):
    weeks=[]
    periods=[]
    format = Format.objects.get(department_id=department)
    for i in range(1, format.numPeriods+1):
        periods.append((i,i))
    for i in range(1, format.numWeeks+1):
        weeks.append((i,i))
    if request.method=='POST':
        form=AssignPeriodForm(weeks,periods,request.POST,request.FILES)
        if form.is_valid():
            modules=Module.objects.filter(group_id=group, groupNum=groupNum)
            for mod in modules:
                per=form.cleaned_data['day']+"-"+str(form.cleaned_data['period'])
                mod.period=Period.objects.get(department_id=department, week=form.cleaned_data['week'], name=per)
                mod.save()
            return HttpResponse(status=204, headers={'HX-Trigger':'moduleDetailsChange'})
    form=AssignPeriodForm(weeks,periods)
    context={'form':form}
    context['Operation']="Assign/Edit Period"
    return render(request, 'forms/modalForm.html', context)

def deleteObject(reqest, type, id):
    Type = apps.get_model(app_label='timetable', model_name=type)
    try:
        obj = Type.objects.get(id=id).delete()
    except Type.DoesNotExist:
        obj=None
    trigger = type[0].lower()+type[1:]+"Change"
    events='{\"'+trigger+'\": "Deleted", "objectDeleted": "ObjectDeleted"}'
    return HttpResponse(status=204, headers={"HX-Trigger": events})


    


