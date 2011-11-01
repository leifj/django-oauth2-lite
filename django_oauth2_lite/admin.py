"""Admin classes for django-oauth2-lite application."""

from django.contrib import admin

from django-oauth2-lite.models import Example


class ExampleAdmin(admin.ModelAdmin):
    """Admin class for Example model class."""
    pass


admin.site.register(Example, ExampleAdmin)
