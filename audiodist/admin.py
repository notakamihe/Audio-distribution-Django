from django.contrib import admin
from audiodist.models import *

# Register your models here.
admin.site.register(Account)
admin.site.register(Artist)
admin.site.register(Follower)
admin.site.register(Song)
admin.site.register(Collection)
admin.site.register(CollectionTrack)
