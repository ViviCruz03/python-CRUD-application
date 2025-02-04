from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
#Biblioteca de django que permite crear una cookie para la sesión del usuario
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import TareaForm
from .models import Tarea
from django.utils import timezone

# Create your views here.

def home(request):
    return render(request, 'home.html', {
    })

def signup(request):

    if request.method == 'GET':
        #print('Enviando formulario')
        return render(request, 'signup.html', {
            'form': UserCreationForm
        })
    else:
        if request.POST['password1'] == request.POST['password2']:
            # Registrar usuario
            try:
                user = user.objects.create_user(
                    request.POST['username'], password=request.POST['password1'])
                user.save()
                #Creación de la cookie
                login(request, user)
                return redirect('tareas')
            except IntegrityError:
                return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    "error": 'El usuario ya existe'
                })
        return render(request, 'signup.html', {
            'form': UserCreationForm,
            "error": 'Las contraseñas no coinciden'
        })

def tareas(request):
    tareas = Tarea.objects.filter(user=request.user, datecompleted__isnull=True)
    return render(request, 'tareas.html',{'tareas':tareas})

def tareas_completadas(request):
    tareas = Tarea.objects.filter(user=request.user, datecompleted__isnull=False).order_by ('-datecompleted')
    return render(request, 'tareas.html',{'tareas':tareas})

def create_task(request):
    if request.method =='GET':
        return render(request, 'crear_tarea.html',{'form': TareaForm })
    else:
        try:
            form = TareaForm(request.POST)
            nueva_tarea = form.save(commit=False) #Evita que Django guarde la tarea inmediatamente
            nueva_tarea.user = request.user #Asigna el usuario autenticado.
            nueva_tarea.save() #Guarda la tarea en la base de datos con el usuario asignado.
            return redirect('tareas')
        except ValueError:
            return render(request, 'crear_tarea.html',{
                "form":TareaForm, 
                "error": "Error al crear la tarea"
            })

def tarea_detalle(request, tarea_id):
    if request.method == 'GET':
        # Obtiene la tarea o lanza un error 404 si no existe
        tarea=get_object_or_404(Tarea, pk=tarea_id, user=request.user)
        form= TareaForm(instance=tarea)
        return render(request, 'detalles_tarea.html', {'tarea': tarea, 'form': form})    
    else:
        try:
            tarea= get_object_or_404(Tarea, pk=tarea_id, user=request.user)
            form = TareaForm(request.POST, instance=tarea)
            form.save()
            return redirect('tareas')
        except ValueError:
            return render (request, 'detales_tarea.html', {'tarea':tarea, 'form': form, 'error':"Error al actualizar la tarea"})

def signout(request):
    logout(request)
    return redirect('home')

def signin(request):
    if request.method == 'GET':
        return render(request, 'ingresar.html',{
        'form': AuthenticationForm
        })
    else:
        user=authenticate (
            request, username=request.POST['username'], password=request.POST
            ['password'])
        if user is None:
            return render(request, 'ingresar.html', {
                'form': AuthenticationForm,
                'error': 'El nombre o la contraseña son incorrectos'
        })
        else:
            login(request, user)
            return redirect('tareas')

def completar_tarea(request, tarea_id):
    tarea=get_object_or_404(Tarea, pk=tarea_id, user=request.user)
    if request.method =='POST':
        tarea.datecompleted =timezone.now()
        tarea.save()
        return redirect(tareas)


def eliminar_tarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, pk=tarea_id, user=request.user)
    if request.method == 'POST':
        tarea.delete()
        return redirect('tareas')