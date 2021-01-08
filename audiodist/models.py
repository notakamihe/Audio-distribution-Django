from django.db import models
from django.db.models.signals import pre_save
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils.text import slugify

import django
import datetime
import time
from tinytag import TinyTag

# Create your models here.
class AccountManager (BaseUserManager):
    def create_user(self, email, username, dob, password=None):
        if not email:
            raise ValueError("User must have email address")
        if not username:
            raise ValueError("User must have username")
        if not dob:
            raise ValueError("User must have DOB")

        user = self.model(
            email=self.normalize_email(email), 
            username = username,
            dob = dob
        )

        user.set_password(password)
        user.save(using=self._db)

        return user


    def create_superuser(self, email, username, dob, password):
        user = self.create_user(
            email=self.normalize_email(email), 
            password = password,
            username = username,
            dob = dob
        )

        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class Account (AbstractBaseUser):
    email = models.EmailField(verbose_name="email", max_length=60, unique=True)
    username = models.CharField(max_length=30, unique=True)
    dob = models.DateField()

    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'dob']

    objects = AccountManager()

    def __str__ (self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True


class Artist (models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE)
    name = models.CharField(default='Artist', max_length=60)
    pfp = models.ImageField(default='defaultpfp.png', upload_to='artists/', null=True, blank=True)
    description = models.TextField(max_length=1000, blank=True, null=True)
    date_joined = models.DateField(auto_now_add=True)

    @property
    def pfp_url (self):
        try:
            return self.pfp.url
        except:
            return ''

    @property
    def followers (self):
        return True

    @property
    def date_joined_word_form (self):
        return self.date_joined.strftime('%B %d, %Y')

    @property
    def num_songs (self):
        return Song.objects.filter(artist=self).count()

    @property
    def num_public_songs (self):
        return Song.objects.filter(artist=self, is_public=True).count()

    @property
    def num_collections (self):
        return Collection.objects.filter(artist=self).count()

    @property
    def num_public_collections (self):
        return Collection.objects.filter(artist=self, is_public=True).count()

    @property
    def num_followers (self):
        return Follower.objects.filter(of=self).count()

    @property
    def num_following (self):
        return Follower.objects.filter(by=self).count()


class Follower (models.Model):
    of = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='artist_followed')
    by = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='artist_following')


class Song (models.Model):
    slug = models.SlugField(max_length=250, null=True, blank=True)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    audio_file = models.FileField(upload_to='music/', null=True)
    cover = models.ImageField(default='black.jpeg', upload_to='covers/', null=True, blank=True)
    release_date = models.DateField(default=django.utils.timezone.now)
    plays = models.IntegerField(default=0)
    is_public = models.BooleanField(default=True)

    @property
    def cover_url (self):
        try:
            return self.cover.url
        except:
            return ''

    @property
    def song_url (self):
        try:
            return self.audio_file.url
        except:
            return ''

    @property
    def time_ago (self):
        if (datetime.datetime.now().date() - self.release_date).days == 0:
            return 'Today'
        elif (datetime.datetime.now().date() - self.release_date).days == 1:
            return 'Yesterday'
        elif (datetime.datetime.now().date() - self.release_date).days < 7:
            return f'{(datetime.datetime.now().date() - self.release_date).days} days ago'
        elif (datetime.datetime.now().date() - self.release_date).days < 30:
            return f'{(datetime.datetime.now().date() - self.release_date).days // 7} weeks ago'
        else:
            if (datetime.datetime.now().year - self.release_date.year >= 1):
                return self.release_date.strftime('%B %d, %Y')
            else:
                return self.release_date.strftime('%B %d')

    @property
    def duration (self):
        tag = TinyTag.get('static/' + self.song_url)
        return int(tag.duration)

class Collection (models.Model):
    collection_types = [
        ('Collection', 'Collection'), ('Playlist', 'Playlist'), ('EP', 'EP'), ('Album', 'Album'), ('LP', 'LP'),
        ('Compilation', 'Compilation'), ('Mixtape', 'Mixtape')
    ]

    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=250, null=True, blank=True)
    description = models.TextField(max_length=2000, blank=True, null=True)
    cover = models.ImageField(default='black.jpeg', upload_to='covers/', null=True, blank=True)
    kind = models.CharField(default='Collection', max_length=25, choices=collection_types)
    release_date = models.DateField(default=django.utils.timezone.now)
    is_public = models.BooleanField(default=True)

    @property
    def cover_url (self):
        try:
            return self.cover.url
        except:
            return ''

    @property
    def time_ago (self):
        if (datetime.datetime.now().date() - self.release_date).days == 0:
            return 'Today'
        elif (datetime.datetime.now().date() - self.release_date).days == 1:
            return 'Yesterday'
        elif (datetime.datetime.now().date() - self.release_date).days < 7:
            return f'{(datetime.datetime.now().date() - self.release_date).days} days ago'
        elif (datetime.datetime.now().date() - self.release_date).days < 30:
            return f'{(datetime.datetime.now().date() - self.release_date).days // 7} weeks ago'
        else:
            if (datetime.datetime.now().year - self.release_date.year == 0):
                return self.release_date.strftime('%B %d')
            else:
                return self.release_date.strftime('%B %d, %Y')

    @property
    def num_tracks (self):
        return CollectionTrack.objects.filter(collection=self).count

    @property
    def length (self):
        songs = [ track.song for track in CollectionTrack.objects.filter(collection=self) ]
        total_duration = sum([song.duration for song in songs])
        return { 'minutes': total_duration // 60, 'seconds': total_duration % 60 }

    @property
    def length_rounded (self):
        return self.length['minutes'] if 0 <= self.length['seconds'] <= 30 else self.length['minutes'] + 1


class CollectionTrack (models.Model):
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)


class Comment (models.Model):
    to = models.ForeignKey(Song, on_delete=models.CASCADE)
    by = models.ForeignKey(Artist, on_delete=models.CASCADE)
    time_commented = models.DateTimeField(auto_now_add=True)
    content = models.TextField(max_length=500)

    @property
    def time_word_form (self):
        return self.time_commented.strftime('%B %d, %Y %-I:%M %p')


def slug_generator (sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.title, allow_unicode=True)
        instance.save()
        
        occurences = len(list(sender.objects.filter(slug=instance.slug)))

        if occurences > 1:
            instance.slug = slugify(instance.title + str(occurences), allow_unicode=True)


pre_save.connect(slug_generator, sender=Song)
pre_save.connect(slug_generator, sender=Collection)
