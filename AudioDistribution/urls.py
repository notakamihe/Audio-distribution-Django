"""AudioDistribution URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from audiodist.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index_view, name='index'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('create/song/', song_create_view, name='create-song'),
    path('create/collection/', collection_create_view, name='create-collection'),
    path('<str:username>/', artist_view, name='artist'),
    path('<str:username>/songs/<slug:song_slug>', song_view, name='song'),
    path('<str:username>/collections/<slug:collection_slug>', collection_view, name='collection')
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)