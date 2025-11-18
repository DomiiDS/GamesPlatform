from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Comment
from .views import User

class UserForm(UserCreationForm):

    class Meta:
        model = User
        exclude = ('profile_picture', 'bio')
        fields = ("username", "password1", "password2", "email")

class ProfileForm(forms.ModelForm):
    
    class Meta:
        model = User
        fields = ("username", "profile_picture", "bio")

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3})
        }