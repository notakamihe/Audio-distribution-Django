from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404

from .forms import *

# Create your views here.
def index_view (request):
    return render(request, 'audiodist/index.html', {})


def register_view (request):
    if request.method == 'POST':
        form = CreateAccountForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('artist', form.cleaned_data.get('username'))
    else:
        form = CreateAccountForm()
        
    return render(request, 'audiodist/register.html', { 'form': form })


def login_view (request):
    return render(request, 'audiodist/login.html', {})


def artist_view (request, username):
    if username in [ account.username for account in Account.objects.all() ]:
        artist = Artist.objects.get(account=Account.objects.get(username=username))
        artist_songs = Song.objects.filter(artist=artist)
        artist_collections = Collection.objects.filter(artist=artist)

        if request.method == 'POST':
            if request.is_ajax():
                collection_slug = request.POST.get('collection_slug')
                song_slug = request.POST.get('song_slug')

                if collection_slug and song_slug:
                    collection = get_object_or_404(Collection.objects.filter(artist=artist), slug=collection_slug)
                    song = get_object_or_404(Song.objects.filter(artist=artist), slug=song_slug)

                    try:
                        track = CollectionTrack.objects.get(collection=collection, song=song)
                        track.delete()
                    except:
                        track = CollectionTrack.objects.create(collection=collection, song=song)
                        track.save()

    else:
        raise Http404('User not found')

    return render(request, 'audiodist/artist.html', { 'artist': artist, 'songs': artist_songs, 
    'collections': artist_collections, 'tracks': CollectionTrack.objects.all() })


def song_create_view (request):
    if not request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = SongForm(request.POST, request.FILES)

        if form.is_valid():
            form.save(request.user)
            return redirect('artist', request.user.username)
    else:
        form = SongForm()
    return render(request, 'audiodist/create-song.html', { 'form': form })


def song_view (request, username, song_slug):
    if username in [ account.username for account in Account.objects.all() ]:
        artist = Artist.objects.get(account=Account.objects.get(username=username))
        song = get_object_or_404(Song.objects.filter(artist=artist), slug=song_slug)
    else:
        raise Http404('User not found')

    return render(request, 'audiodist/song.html', { 'artist': artist, 'song': song })


def collection_create_view (request):
    if not request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = CollectionForm(request.POST, request.FILES)

        if form.is_valid():
            form.save(request.user)
            return redirect('artist', request.user.username)
    else:
        form = CollectionForm()

    return render(request, 'audiodist/create-collection.html', { 'form': form })


def collection_view (request, username, collection_slug):
    if username in [ account.username for account in Account.objects.all() ]:
        artist = Artist.objects.get(account=Account.objects.get(username=username))
        collection = get_object_or_404(Collection.objects.filter(artist=artist), slug=collection_slug)
        songs = enumerate([ track.song for track in CollectionTrack.objects.filter(collection=collection) ], 1)
    else:
        raise Http404('User not found')

    return render(request, 'audiodist/collection.html', { 'artist': artist, 'collection': collection, 'songs': songs })