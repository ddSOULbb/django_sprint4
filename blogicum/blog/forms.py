from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .models import Comment, Post
from django.contrib.auth import get_user_model


User = get_user_model()


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "email")
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).\
                exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Это имя пользователя уже занято.")
        return username


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        exclude = ('is_staff', 'groups',
                   'user_permissions',
                   'is_active', 'is_superuser',
                   'last_login', 'date_joined',
                   'username', 'password')


class PostEditForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'text', 'image', 'pub_date', 'location', 'category')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Текст публикации'
            }),
            'pub_date': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control'
                },
                format='%Y-%m-%dT%H:%M'
            ),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image and image.size > 5 * 1024 * 1024:  # 5MB
            raise ValidationError("Максимальный размер изображения - 5MB")
        return image


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Оставьте ваш комментарий...'
            })
        }


class CommentEditForm(CommentForm):
    class Meta(CommentForm.Meta):
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            })
        }
