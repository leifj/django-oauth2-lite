django-oauth2-lite
==================

This is a "server" implementation of OAuth 2.0 for the django web framework

* Does not depend on any other python oauth module
* Only works with django
* Only works with oauth 2.0 (draft version 22) - no OAuth 1.x support at all
* Only implements bearer tokens
* For a django-integrated client for oauth 2.0 have a look at https://github.com/berggren/django-oauth2-lite-client

Installation

1. Add 'django_oauth2_lite' to INSTALLED_APPS and "mount" the django_oauth2_lite.urls under "/oauth2" in your urls.py
2. Run manage.py syncdb to create db-models
3. Create scopes using the admin UI. A scope is something that limits the .. scope of an oauth token.
4. Override the templates in templates/django_oauth2_lite. You may get away with just overriding base.html. Do this by creating a directory django_oauth2_lite in your template search path and create your version of the supplied templates in that directory.

Test

1. Visit /oauth2/clients and create a new client with redirect_uri https://your.host:port/oauth2/example/cb
2. Click the "Test" button and follow the flow. The resulting code is an access grant token.

Protect resources

@oauth2_required(scope='my-scope')
def view(request,...):
   #request.user contains the owner of the token
   pass
