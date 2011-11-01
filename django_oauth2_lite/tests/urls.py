from django.conf.urls.defaults import *


urlpatterns = patterns('',
    url(r'^example/', include('django-oauth2-lite.urls')),
)
