from django import forms
from .models import Room, User
# from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class RoomForm(forms.ModelForm):

  name = forms.CharField(label='Room Name', widget=forms.TextInput(attrs={'placeholder':'Enter room name...'}))
  description = forms.CharField(label='Room Description', widget=forms.Textarea(attrs={'placeholder':'Enter room description...'}))

  class Meta:
    model = Room
    fields = '__all__'
    exclude = ['host', 'participants']

class UserForm(forms.ModelForm):

    class Meta:
      model = User
      fields = ['avatar', 'name', 'username', 'email', 'bio']

class MyUserCreationForm(UserCreationForm):
  class Meta:
    model = User
    fields = ['name', 'username', 'email', 'password1', 'password2']