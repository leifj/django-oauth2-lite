"""URLs for django-oauth2-lite application."""

from django.conf.urls.defaults import *


urlpatterns = patterns('django-oauth2-lite.views',
    url(r'^$', view='index', name='django-oauth2-lite_index'),
)
