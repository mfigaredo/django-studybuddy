from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from slugify import slugify
from django.contrib import messages
from django.db.models import Q, Count
# from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
# from django.contrib.auth.forms import UserCreationForm
from .forms import RoomForm, UserForm, MyUserCreationForm
from .models import Room, Topic, Message, User
import json

# Create your views here.

# rooms = [
#   {'id': 1, 'name': 'Lets learn Python!'},
#   {'id': 2, 'name': 'Design with me'},
#   {'id': 3, 'name': 'Frontend developers'},
# ]

# def test(request):
#   # current_page = request.META['wsgi.url_scheme'] +'://' +request.META['HTTP_HOST'] + request.META['PATH_INFO']
#   # referer = request.META.get('HTTP_REFERER', None)
#   # return HttpResponse(current_page + ' - ' + referer)
#   # return HttpResponse('<h2>Hello, World!</h2>')
#   context = {'myvar': 123, }
#   return render(request, 'base/test.html', context)


def loginPage(request):

  page = 'login'
  if request.user.is_authenticated:
    return redirect('home')

  if request.method == 'POST':
    email = request.POST.get('email').lower()
    password = request.POST.get('password')

    try:
      user = User.objects.get(email=email)
    except:
      messages.error(request, 'User does not exist')

    user = authenticate(request, email=email, password=password)

    if user is not None:
      login(request, user)
      return redirect('home')
    else:
      messages.error(request, 'Email or password does not exist')

  context = {'page': page}
  return render(request, 'base/login_register.html', context)

def logoutUser(request):
  if request.method == 'POST':
    logout(request)
  return redirect('home')

def registerPage(request):
  page = 'register'
  form = MyUserCreationForm()

  if request.method == 'POST':
    form = MyUserCreationForm(request.POST)
    if form.is_valid():
      user = form.save(commit=False)
      user.username = user.username.lower()
      user.save()
      login(request, user)
      return redirect('home')
    else:
      messages.error(request, 'An error occurred during registration')

  context = {'page': page, 'form': form}
  return render(request, 'base/login_register.html', context)

def home(request):
  
  
  topic = request.GET.get('topic','')
  # rooms = Room.objects.filter(topic__name__icontains=q)
  q = request.GET.get('q', '')

  if len(topic):
    rooms = Room.objects.filter(topic__name=topic)
  elif len(q):
    rooms = Room.objects.filter(
      Q(topic__name__icontains=q) 
      | Q(name__icontains=q)
      | Q(description__icontains=q)
    )
  else:
    rooms = Room.objects.all()

  # topics = Topic.objects.all()
  ordered_topics = Topic.orderByRooms()
  # room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
  # Filter messages of selected rooms only
  room_messages = Message.objects.filter(room__in=rooms)[0:8]
  
  context = {
    'rooms': rooms, 
    'q_topic': topic,
    'topics': ordered_topics[0:5], 
    'q': q, 
    'room_count' : rooms.count(), 
    'room_messages': room_messages,
    'total_rooms': Room.objects.all().count(),
  }
  return render(request, 'base/home.html', context)

def room(request, pk):
  # return HttpResponse('Room') 
  # room = None
  # for i in rooms:
  #   if i['id'] == int(pk):
  #     room = i
  room = Room.objects.get(id=pk)

  if request.method == 'POST':
    if len(request.POST.get('body','')) > 0:
      message = Message.objects.create(
        user=request.user,
        room=room,
        body=request.POST.get('body')
      )
      room.participants.add(request.user)
      return redirect('room', room.id)

  room_messages = room.message_set.all()
  participants = room.participants.all()
  context = {
    'room': room, 
    'room_messages': room_messages, 
    'participants': participants,
  }
  return render(request, 'base/room.html', context)

def userProfile(request, pk):
  user = User.objects.get(id=pk)
  rooms = user.room_set.all()
  # topics = Topic.objects.all()
  topics = Topic.orderByRooms()
  room_messages = user.message_set.all()
  context = {
    'user': user, 
    'rooms': rooms,
    'topics': topics,
    'room_messages': room_messages,
    'total_rooms': Room.objects.all().count(),
  }
  return render(request, 'base/profile.html', context)

@login_required(login_url='login')
def createRoom(request):
  form = RoomForm()
  topics = Topic.objects.all()
  if request.method == 'POST':
    # print(request.POST)
    topic_name = request.POST.get('topic')
    topic, created = Topic.objects.get_or_create(name=topic_name)
    Room.objects.create(
      host=request.user,
      topic=topic,
      name=request.POST.get('name'),
      description=request.POST.get('description'),
    )
    messages.success(request, 'Room has been created successfully')
    return redirect('home')

    # form = RoomForm(request.POST)
    # if form.is_valid():
    #   room = form.save(commit=False)
    #   room.host = request.user
    #   room.save()
      # messages.add_message(request, messages.SUCCESS, 'Room has been created successfully')
      # messages.success(request, 'Room has been created successfully')
      # return redirect('home')

  context = {'form': form, 'topics': topics}
  return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
  room = Room.objects.get(id=pk)
  form = RoomForm(instance=room)
  topics = Topic.objects.all()

  if request.user != room.host:
    return HttpResponse('You are not allowed here')

  if request.method == 'POST':
    # form = RoomForm(request.POST, instance=room)
    # if form.is_valid():
    #   form.save()
    #   return redirect('home')
    topic_name = request.POST.get('topic')
    topic, created = Topic.objects.get_or_create(name=topic_name)
    room.name = request.POST.get('name')
    room.description = request.POST.get('description')
    room.topic = topic
    room.save()
    return redirect('home')

  context = {'form': form, 'topics': topics, 'room': room}
  return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
  room = Room.objects.get(id=pk)

  if request.user != room.host:
    return HttpResponse('You are not allowed here')

  if request.method == 'POST':
    room.delete()
    messages.success(request, 'Room %s has been deleted' % str(room.name)[0:30])
    return redirect('home')
  return render(request, 'base/delete.html', {'obj': room})

@login_required(login_url='login')
def deleteMessage(request, pk):
  message = Message.objects.get(id=pk)

  if request.user != message.user:
    return HttpResponse('You are not allowed here')

  if request.method == 'POST':
    message.delete()
    messages.success(request, 'Message %s has been deleted' % str(message.body)[0:30])
    return redirect('home')
  return render(request, 'base/delete.html', {'obj': message})

@login_required(login_url='login')
def updateUser(request):
  user = request.user
  form = UserForm(instance=user)

  if request.method == 'POST':
    form = UserForm(request.POST, request.FILES, instance=user)
    if form.is_valid():
      form.save()
      messages.success(request, 'User has been updated')
      return redirect('user-profile', pk=user.id)
  context = {'form': form}
  return render(request, 'base/update-user.html', context)

def topicsPage(request):
  q = request.GET.get('q', '')
  topics = Topic.objects.filter(name__icontains=q).annotate(num_rooms=Count('room')).order_by('-num_rooms')
  context = {
    'topics' : topics,
    'rooms_total': Room.objects.all().count,
  }
  return render(request, 'base/topics.html', context)

def activityPage(request):
  room_messages = Message.objects.all()
  current_page = request.META['wsgi.url_scheme'] +'://' +request.META['HTTP_HOST'] + request.META['PATH_INFO']
  referer = request.META.get('HTTP_REFERER', None)
  print('current', current_page)
  print('referer', referer)
  backpage = reverse('home') if referer is None or current_page==referer  else referer
  
  context = {'room_messages' : room_messages, 'backpage': backpage}
  return render(request, 'base/activity.html', context)