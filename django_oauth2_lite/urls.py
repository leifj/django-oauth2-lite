"""URLs for django-oauth2-lite application."""

from django.conf.urls.defaults import patterns,url

urlpatterns = patterns('django_oauth2_lite.views',
    url(r'^token/?$', view='token'),
    url(r'^authorize/?$', view='authorize'),
    url(r'^clients?/?$', view='clients'),
    url(r'^client/add/?$', view='add_client'),
    url(r'^client/(?P<id>[0-9]+)/remove/?$', view='remove_client'),
)
