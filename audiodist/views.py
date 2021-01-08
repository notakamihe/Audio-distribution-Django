from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, JsonResponse, HttpResponse, HttpResponseForbidden, HttpResponseNotAllowed
from django.template.context_processors import request
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.forms.models import model_to_dict

from .forms import *

# Create your views here.
def all_views (request):
    try:
        logged_in_artist = Artist.objects.get(account=request.user)
    except:
        logged_in_artist = None

    return { 'logged_in_artist': logged_in_artist, 'user': request.user }


def index_view (request):
    return render(request, 'audiodist/index.html', { 'artists': Artist.objects.all() })


def search_view (request):
    if request.method == 'GET':
        query = request.GET.get('search')

        if not query:
            return redirect('index')

        song_results = Song.objects.filter(Q(title__icontains=query))
        collection_results = Collection.objects.filter(Q(title__icontains=query) | Q(description__icontains=query))
        artist_results = list(Artist.objects.filter(Q(name__icontains=query) | Q(description__icontains=query)))

        accounts = Account.objects.filter(is_superuser=False)
        username_results = [ Artist.objects.get(account=account) for account in accounts.filter(Q(username__icontains=query)) ]

        song_results_count = len(list(filter(lambda s: request.user == s.artist.account or s.is_public, song_results)))
        collection_results_count = len(list(filter(lambda c: request.user == c.artist.account or c.is_public, collection_results)))
    elif request.method == 'POST':
        song_slug = request.POST.get('song_slug')
        song = get_object_or_404(Song.objects.filter(slug=song_slug))
        song.plays += 1
        song.save()

        return JsonResponse({ 'plays': song.plays })

    return render(request, 'audiodist/search.html', { 'query': query, 'results': {
        'songs': song_results,
        'collections': collection_results,
        'artists': list(set(artist_results + username_results)),
        'tracks': CollectionTrack.objects.all(),
        'num_results': song_results_count  + collection_results_count + len(list(set(artist_results + username_results)))
    } })


def register_view (request):
    if request.user.is_authenticated:
        return redirect('artist', request.user.username)

    if request.method == 'POST':
        form = CreateAccountForm(request.POST)

        if form.is_valid():
            registered_user = form.save()
            login(request, registered_user)
            return redirect('artist', form.cleaned_data.get('username'))
    else:
        form = CreateAccountForm()
        
    return render(request, 'audiodist/register.html', { 'form': form })


def login_view (request):
    if request.user.is_authenticated:
        return redirect('artist', request.user.username)

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        account = authenticate(request, username=email, password=password)

        if account is not None:
            login(request, account)
            return redirect('artist', account.username)
        else:
            messages.info(request, 'Invalid username or password')
            return redirect('login')

    return render(request, 'audiodist/login.html', {})


def logout_view (request):
    if request.method == 'GET':
        return Http404

    if request.method == 'POST':
        logout(request)
        return redirect('index')
    
    return JsonResponse({})


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
                    if request.POST.get('action') == 'play':
                        song_slug = request.POST.get('song_slug')
                        song = get_object_or_404(Song.objects.filter(artist=artist), slug=song_slug)
                        song.plays += 1
                        song.save()

                        return JsonResponse({ 'plays': song.plays })
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

        if request.user != artist.account:
            return HttpResponseForbidden('<h1>You cannot access this page</h1>')
        
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

        if request.user != artist.account:
            return HttpResponseForbidden('<h1>You cannot access this page</h1>')
        
        if request.method == 'POST':
            artist.account.delete()
            return HttpResponse('<h1>Account deleted</h1>')
    else:
        raise Http404('User not found')

    return render(request, 'audiodist/artist-delete.html', { 'artist': artist })


def song_create_view (request):
    if not request.user.is_authenticated:
        return redirect('login')

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
        collections = list(filter(lambda c: CollectionTrack.objects.filter(collection=c, song=song).exists(), Collection.objects.filter(artist=artist)))

        comments = Comment.objects.filter(to=song)

        if request.user != artist.account and not song.is_public:
            return HttpResponseNotAllowed('Access to song not allowed')

        if request.method == 'POST':
            if 'action' in request.POST:
                if request.POST.get('action') == 'song-visibility':
                    song.is_public = not song.is_public
                    song.save()
                    return JsonResponse({})
                if request.POST.get('action') == 'add-to-collection':
                    collection_slug = request.POST.get('collection_slug')
                    collection = Collection.objects.filter(artist=artist).get(slug=collection_slug)
                    
                    try:
                        track = CollectionTrack.objects.get(collection=collection, song=song)
                        track.delete()
                    except:
                        track = CollectionTrack.objects.create(collection=collection, song=song)
                        track.save()
                if request.POST.get('action') == 'play':
                    song.plays += 1
                    song.save()

                    return JsonResponse({ 'plays': song.plays })
            else:
                form = CommentForm(request.POST)

                if form.is_valid():
                    comment = form.save(Artist.objects.get(account=request.user), song)
                    return JsonResponse({ 'comment': { 'content': comment.content, 'name': comment.by.name, 
                    'username': comment.by.account.username, 'time': datetime.datetime.now().strftime('%B %d, %Y %-I:%M %p') } })
        else:
            form = CommentForm()
    else:
        raise Http404('User not found')

    return render(request, 'audiodist/song.html', { 'artist': artist, 'song': song, 'collections': collections, 
    'form': form, 'comments': comments })


def song_edit_view (request, username, song_slug):
    if username in [ account.username for account in Account.objects.all() ]:
        artist = Artist.objects.get(account=Account.objects.get(username=username))
        song = get_object_or_404(Song.objects.filter(artist=artist), slug=song_slug)

        if request.user != artist.account:
            return HttpResponseForbidden("<h1>You cannot access this page</h1>")

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
        return redirect('login')

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

        if request.user != artist.account and not collection.is_public:
            return HttpResponseNotAllowed('Access to collection not allowed')

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

        if request.user != artist.account:
            return HttpResponseForbidden("<h1>You cannot access this page</h1>")

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