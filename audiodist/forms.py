from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model

from .models import *

import datetime

Acc = get_user_model()

class DateInput(forms.DateInput):
    input_type = 'date'


class CreateAccountForm (forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput, validators=[validate_password])
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput, validators=[validate_password])

    class Meta:
        model = Acc
        fields = [ 'email', 'username', 'dob', 'password1', 'password2' ]

    def __init__ (self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['email'].widget.attrs.update({ 'class': 'col-6 p-2', 'id': 'email' })
        self.fields['username'].widget.attrs.update({ 'class': 'col-3 p-2', 'id': 'username' })
        self.fields['password1'].widget.attrs.update({ 'class': 'p-2', 'id': 'password1' })
        self.fields['password2'].widget.attrs.update({ 'class': 'p-2', 'id': 'password2' })

        self.fields['dob'].widget = DateInput(attrs={
            'class': 'col-3 p-2', 'id': 'dob'
        })

    def clean_username (self):
        username = self.cleaned_data.get('username')

        if any([not char.isalnum() and char != '_' for char in username]):
            raise forms.ValidationError('Only letters, numbers and underscores allowed in username')
        return username

    def clean_password2 (self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 != password2:
            raise forms.ValidationError('Passwords do not match')
        return password2

    def clean_dob (self):
        dob = self.cleaned_data.get('dob')

        if dob.year < 1899 or dob > datetime.datetime.now().date():
            raise ValidationError('Invalid date.')
        if datetime.datetime.now().year - dob.year < 13:
            raise ValidationError('Too young. You must be at least 13.')

        return dob

    def save (self, commit=True):
        user = super(CreateAccountForm, self).save(commit=False)

        user.email = self.cleaned_data.get('email')
        user.username = self.cleaned_data.get('username')
        user.dob = self.cleaned_data.get('dob')
        user.set_password(self.cleaned_data.get('password1'))

        if commit:
            user.save()

            artist = Artist(account=user)
            artist.save()

        return user


class ArtistEditForm (forms.ModelForm):
    pfp = forms.ImageField(required=False, widget=forms.FileInput)

    class Meta:
        model = Artist
        fields = ['name', 'pfp', 'description']

    def __init__ (self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['name'].widget.attrs.update({ 'class': 'col-4 p-2', 'id': 'name' })
        self.fields['pfp'].widget.attrs.update({ 'class': 'col-4 p-2', 'id': 'pfp' })
        self.fields['description'].widget.attrs.update({ 'class': 'col-4 p-2', 'id': 'description' })

    def save(self, commit=True):
        artist = super(ArtistEditForm, self).save(commit=False)

        artist.name = self.cleaned_data.get('name')
        artist.description = self.cleaned_data.get('description')

        if self.cleaned_data.get('pfp'):
            artist.pfp = self.cleaned_data.get('pfp')

        if commit:
            artist.save()
        return artist


class SongForm (forms.ModelForm):
    class Meta:
        model = Song
        fields = ['title', 'audio_file', 'cover', 'release_date', 'is_public']

    def __init__ (self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['title'].widget.attrs.update({ 'class': 'col-9 p-2', 'id': 'title' })
        self.fields['is_public'].widget.attrs.update({ 'id': 'is-public' })
        self.fields['audio_file'].widget.attrs.update({ 'id': 'audio', 'accept': 'audio/*' })
        self.fields['cover'].widget.attrs.update({ 'id': 'cover', 'accept': 'image/*' })

        self.fields['release_date'].widget = DateInput(attrs={
            'class': 'col-2 p-2', 'id': 'release-date'
        })

    def clean_release_date (self):
        release_date = self.cleaned_data.get('release_date')

        if release_date.year < 0 or release_date.year > datetime.datetime.now().year + 10:
            raise ValidationError('Invalid release date.')

        return release_date

    def save (self, account, commit=True):
        song = super(SongForm, self).save(commit=False)

        song.artist = Artist.objects.get(account=account)
        song.title = self.cleaned_data.get('title')
        song.slug = ''
        song.release_date = self.cleaned_data.get('release_date')
        song.is_public = self.cleaned_data.get('is_public')

        if self.cleaned_data.get('audio_file'):
            song.audio_file = self.cleaned_data.get('audio_file')

        if self.cleaned_data.get('cover'):
            song.cover = self.cleaned_data.get('cover')

        if commit:
            song.save()
        return song


class SongEditForm (SongForm):
    audio_file = forms.FileField(required=False, widget=forms.FileInput)
    cover = forms.ImageField(required=False, widget=forms.FileInput)

    class Meta:
        model = Song
        fields = ['title', 'audio_file', 'cover', 'release_date', 'is_public']

    def __init__ (self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class CollectionForm (forms.ModelForm):
    cover = forms.ImageField(required=False, widget=forms.FileInput)

    class Meta:
        model = Collection
        fields = [ 'title', 'description', 'cover', 'kind', 'release_date', 'is_public' ]

    def __init__ (self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['title'].widget.attrs.update({ 'class': 'col-9 p-2', 'id': 'title' })
        self.fields['kind'].widget.attrs.update({ 'class': 'p-2', 'id': 'kind' })
        self.fields['description'].widget.attrs.update({ 'cols': '90', 'id': 'description' })
        self.fields['is_public'].widget.attrs.update({ 'id': 'is-public' })
        self.fields['cover'].widget.attrs.update({ 'id': 'cover' })

        self.fields['release_date'].widget = DateInput(attrs={
            'class': 'col-2 p-2', 'id': 'release-date'
        })

    def clean_release_date (self):
        release_date = self.cleaned_data.get('release_date')

        if release_date.year < 0 or release_date.year > datetime.datetime.now().year + 10:
            raise ValidationError('Invalid year.')

        return release_date

    def save (self, account, commit=True):
        collection = super(CollectionForm, self).save(commit=False)

        collection.artist = Artist.objects.get(account=account)
        collection.title = self.cleaned_data.get('title')
        collection.description = self.cleaned_data.get('description')
        collection.kind = self.cleaned_data.get('kind')
        collection.release_date = self.cleaned_data.get('release_date')
        collection.is_public = self.cleaned_data.get('is_public')

        if self.cleaned_data.get('cover'):
            collection.cover = self.cleaned_data.get('cover')

        if commit:
            collection.save()
        return collection


class CommentForm (forms.ModelForm):
    class Meta:
        model = Comment
        fields = [ 'content' ]

    def __init__ (self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['content'].widget.attrs.update({ 'id': 'content', 'cols': '90', 'rows': '5', 
        'style': 'border: 1px solid #3b8855; border-radius: 0.5rem;', 'class': 'p-2' })

    def save (self, by, to, commit=True):
        comment = super(CommentForm, self).save(commit=False)

        comment.by = by
        comment.to = to
        comment.content = self.cleaned_data.get('content')

        if commit:
            comment.save()
        return comment