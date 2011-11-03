"""Admin classes for django-oauth2-lite application."""

from django.contrib import admin
from django_oauth2_lite.models import Scope, Code, Client, Token

admin.site.register(Scope)
admin.site.register(Code)
admin.site.register(Client)
admin.site.register(Token)