from django.db import models
from django import forms
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from .managers import UserManager
# Create your models here.

class User(AbstractUser, PermissionsMixin):
  name = models.CharField(max_length=200, null=True)
  email = models.EmailField(unique=True, null=True)
  bio = models.TextField(null=True)

  avatar = models.ImageField(null=True, default='avatar.svg', upload_to='user_photos/')

  objects = UserManager()

  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = []

  class Meta:
    db_table = 'studyb_users'

class Topic(models.Model):
  name = models.CharField(max_length=200)

  def __str__(self):
    return self.name[0:100]

  def orderByRooms(ord_t = -1):
    return Topic.objects.annotate(num_rooms=models.Count('room')).order_by(  ('' if ord_t != -1 else '-') +'num_rooms', 'name')

  class Meta:
    db_table = 'studyb_topics'

class Room(models.Model):
  host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
  topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True) 
  name = models.CharField(max_length=200)
  description = models.TextField(null=True, blank=True)
  participants = models.ManyToManyField(User, related_name='participants', blank=True)
  updated = models.DateTimeField(auto_now=True)
  created = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ['-updated', '-created']
    db_table = 'studyb_rooms'

  def __str__(self):
    return self.name

class Message(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  room = models.ForeignKey(Room, on_delete=models.CASCADE)
  body = models.TextField()
  updated = models.DateTimeField(auto_now=True)
  created = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ['-updated', '-created']
    db_table = 'studyb_messages'

  def __str__(self):
    return self.body[0:50]