from django.forms import ModelForm
from .models import Post, Comment
from django import forms


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['group', 'text', 'image', ]
        required = {'group': False}
        widgets = {'text': forms.Textarea}


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {'text': forms.Textarea}
