"""Models for django-oauth2-lite application."""

from django.db import models
from django.db.models.fields import SmallIntegerField, TextField, URLField,\
    CharField, BooleanField
from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.contrib.auth.models import User
from django.db.models.fields.files import ImageField
import datetime
import os
from urlparse import urlparse, parse_qs
from django.http import HttpResponseRedirect
 
CONFIDENTIAL = 0
PUBLIC = 1
 
class Scope(models.Model):
    name = CharField(unique=True)
    description = TextField(null=True,blank=True)
    uri = URLField(null=True,blank=True)
    icon = ImageField(blank=True,null=True)
 
def scope_by_name(self,name):
    try:
        return Scope.objects.get(name=name)
    except Scope.DoesNotExist:
        return None

def rcode(sz):
    return os.urandom(sz).encode("hex")
 
def client_by_id(client_id):
    try:
        return Client.objects.get(client_id=client_id)
    except Client.DoesNotExist:
        return None
 
class Client(models.Model):
    client_type = SmallIntegerField(default=CONFIDENTIAL,choices=((CONFIDENTIAL,"Web Application"),(PUBLIC,"Native Application")))
    client_id = CharField()
    client_secret = CharField(editable=False)
    owner = ForeignKey(User)
    redirection_uri = URLField()
    logo = ImageField(blank=True,null=True)
    
    timecreated = models.DateTimeField(auto_now_add=True)
    lastupdated = models.DateTimeField(auto_now=True)

    def new_token(self,ttl=None,sz=30,refresh_token=None,scopes=[]):
        exp = None
        if ttl != None:
            exp = datetime.datetime.now()+datetime.timedelta(0,ttl)
        if not scopes:
            scopes = refresh_token.scopes
        
        t = Token.objects.create(client=self,value=rcode(sz),expiration_time=exp,refresh_token=refresh_token)
        for scope in scopes:
            t.scopes.add(scope)
        return t
    
    def new_authz_code(self,state=None):
        token = self.new_token(600)
        return Code.objects.create(token=token,state=state)
        
    def new_access_token(self,refresh_token=None,scopes=[]):
        if refresh_token == None:
            refresh_token = self.new_token(scopes=scopes)
        at = self.new_token(3600,refresh_token=refresh_token)
        return at
    
    def redirect(self,qs):
        o = urlparse(self.redirection_uri,'https',False)
        if o.has_key('query'):
            qs.update(parse_qs(o.query))
        o.query = qs
        return HttpResponseRedirect(o.geturl())
    
class Token(models.Model):
    client = ForeignKey(Client,editable=False)
    value = CharField(editable=False,unique=True)
    scopes = ManyToManyField(Scope,editable=False,blank=True,null=True)
    timecreated = models.DateTimeField(auto_now_add=True)
    lastupdated = models.DateTimeField(auto_now=True)
    expiration_time = models.DateTimeField(null=True,blank=True)
    refresh_token = ForeignKey('self',null=True,blank=True)
    
    type = 'bearer'
    
    def scope(self):
        return ' '.join([scope.name for scope in self.scopes])
    
    def is_valid(self): # We're checdking lastupdated since that is when the code is authorized
        return not self.used and self.expiration_time >= datetime.datetime.now()
    
    def type(self):
        return self.refresh_token and 'access_token' or 'refresh_token'
    
    def has_scope(self,scope_name):
        for s in self.scopes:
            if scope_name == s.name:
                return True
        return False
    
class Code(models.Model):
    token = ForeignKey(Token)
    used = BooleanField(default=False,editable=False)
    authorized = BooleanField(default=False)
    state = CharField(editable=False,blank=True,null=True)
    
    def new_access_token(self):
        return self.client.new_access_token(scopes=self.scopes)
    
    def is_valid(self):
        return not self.used and self.token.is_valid()

def token_by_value(token_value):
    if token_value == None:
        return None
    try:
        return Token.objects.get(value=token_value)
    except Token.DoesNotExist:
        return None

def code_by_token(token_value):
    if token_value == None:
        return None
    try:
        return Code.objects.get(token_value=token_value)
    except Code.DoesNotExist:
        return None