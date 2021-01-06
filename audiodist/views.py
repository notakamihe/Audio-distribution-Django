from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, JsonResponse, HttpResponse
from django.template.context_processors import request

from .forms import *

# Create your views here.
def all_views (request):
    try:
        artist = Artist.objects.get(account=request.user)
    except:
        artist = None
    return { 'artist': artist }

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
        users_of_followers = [ follower.by.account for follower in Follower.objects.filter(of=artist) ]

        if request.method == 'POST':
            if request.is_ajax():
                if 'action' in request.POST:
                    if request.POST.get('action') == 'song-visibility':
                        song_slug = request.POST.get('song_slug')
                        song = get_object_or_404(Song.objects.filter(artist=artist), slug=song_slug)

                        song.is_public = not song.is_public
                        song.save()
                        return JsonResponse({})
                    if request.POST.get('action') == 'follow':
                        user_artist = Artist.objects.get(account=request.user)
                        
                        try:
                            follower = Follower.objects.get(of=artist, by=user_artist)
                            follower.delete()
                            return JsonResponse({ 'follow': False, "new_num_followers": artist.num_followers })
                        except:
                            follower = Follower.objects.create(of=artist, by=user_artist)
                            follower.save()
                            return JsonResponse({ 'follow': True, "new_num_followers": artist.num_followers })
                else:
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
    'collections': artist_collections, 'tracks': CollectionTrack.objects.all(), 
    'is_authorized': request.user == artist.account, 'is_user_following': request.user in users_of_followers })


def artist_edit_view (request, username):
    if username in [ account.username for account in Account.objects.all() ]:
        artist = Artist.objects.get(account=Account.objects.get(username=username))
        
        if request.method == 'POST':
            form = ArtistEditForm(request.POST, request.FILES, instance=artist)

            if form.is_valid():
                form.save()
                return redirect('artist', username)
        else:
            form = ArtistEditForm(initial={
                'name': artist.name,
                'pfp': artist.pfp,
                'description': artist.description
            })
    else:
        raise Http404('User not found')

    return render(request, 'audiodist/artist-edit.html', { 'artist': artist, 'form': form })


def artist_delete_view (request, username):
    if username in [ account.username for account in Account.objects.all() ]:
        artist = Artist.objects.get(account=Account.objects.get(username=username))
        
        if request.method == 'POST':
            artist.account.delete()
            return HttpResponse('<h1>Account deleted</h1>')
    else:
        raise Http404('User not found')

    return render(request, 'audiodist/artist-delete.html', { 'artist': artist })


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
        collections = Collection.objects.filter(artist=artist)

        if request.method == 'POST':
            if 'action' in request.POST:
                if request.POST.get('action') == 'song-visibility':
                    song.is_public = not song.is_public
                    song.save()
                    return JsonResponse({})
                if request.POST.get('action') == 'add-to-collection':
                    collection_slug = request.POST.get('collection_slug')
                    collection = collections.get(slug=collection_slug)
                    
                    try:
                        track = CollectionTrack.objects.get(collection=collection, song=song)
                        track.delete()
                    except:
                        track = CollectionTrack.objects.create(collection=collection, song=song)
                        track.save()
    else:
        raise Http404('User not found')

    return render(request, 'audiodist/song.html', { 'artist': artist, 'song': song, 'collections': collections })


def song_edit_view (request, username, song_slug):
    if username in [ account.username for account in Account.objects.all() ]:
        artist = Artist.objects.get(account=Account.objects.get(username=username))
        song = get_object_or_404(Song.objects.filter(artist=artist), slug=song_slug)

        if request.method == 'POST':
            form = SongEditForm(request.POST, request.FILES, instance=song)

            if form.is_valid():
                new_song = form.save(artist.account)
                return redirect('song', username=username, song_slug=new_song.slug)
        else:
            form = SongEditForm(initial={
                'title': song.title,
                'audio_file': song.audio_file,
                'cover': song.cover,
                'release_date': song.release_date,
                'is_public': song.is_public
            })
    else:
        raise Http404('User not found')

    return render(request, 'audiodist/song-edit.html', { 'artist': artist, 'song': song, 'form': form })


def song_delete_view (request, username, song_slug):
    if request.method == 'GET':
        raise Http404('User not found')

    if username in [ account.username for account in Account.objects.all() ]:
        artist = Artist.objects.get(account=Account.objects.get(username=username))
        song = get_object_or_404(Song.objects.filter(artist=artist), slug=song_slug)

        if (request.method == 'POST'):
            song.delete()
            return JsonResponse({})
    else:
        raise Http404('User not found')


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

        if request.method == 'POST':
            if 'action' in request.POST:
                if request.POST.get('action') == 'collection-visibility':
                    collection.is_public = not collection.is_public
                    collection.save()
                    return JsonResponse({})
                if request.POST.get('action') == 'remove-song':
                    song = Song.objects.get(slug=request.POST.get('slug'))
                    track = CollectionTrack.objects.get(collection=collection, song=song)
                    track.delete()
                    return JsonResponse({})
    else:
        raise Http404('User not found')

    return render(request, 'audiodist/collection.html', { 'artist': artist, 'collection': collection, 'songs': songs })


def collection_edit_view (request, username, collection_slug):
    if username in [ account.username for account in Account.objects.all() ]:
        artist = Artist.objects.get(account=Account.objects.get(username=username))
        collection = get_object_or_404(Collection.objects.filter(artist=artist), slug=collection_slug)

        if request.method == 'POST':
            form = CollectionForm(request.POST, request.FILES, instance=collection)

            if form.is_valid():
                form.save(artist.account)
                return redirect('collection', username=username, collection_slug=collection_slug)
        else:
            form = CollectionForm(initial={
                'title': collection.title,
                'description': collection.description,
                'release_date': collection.release_date,
                'kind': collection.kind,
                'cover': collection.cover,
                'is_public': collection.is_public
            })
    else:
        raise Http404('User not found')

    return render(request, 'audiodist/collection-edit.html', { 'artist': artist, 'collection': collection, 'form': form })


def collection_delete_view (request, username, collection_slug):
    if request.method == 'GET':
        raise Http404('User not found')

    if username in [ account.username for account in Account.objects.all() ]:
        artist = Artist.objects.get(account=Account.objects.get(username=username))
        collection = get_object_or_404(Collection.objects.filter(artist=artist), slug=collection_slug)

        if (request.method == 'POST'):
            collection.delete()
            return JsonResponse({})
    else:
        raise Http404('User not found')