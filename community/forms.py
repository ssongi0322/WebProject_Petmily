from django import forms
from .models import Post, Answer, Comment, Image
from django.utils.translation import gettext_lazy as _

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "content"]


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ["content"]


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]

class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ('image', )
        labels = {
            'image': _('Image'),
            
        }