"""Models for django-oauth2-lite application."""

from django.db import models
from django.db.models.fields import SmallIntegerField, TextField, URLField,\
    CharField, BooleanField
from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.contrib.auth.models import User
from django.db.models.fields.files import ImageField
import random, string, socket, os, datetime
from urlparse import urlparse, parse_qs, urlunparse
from django.http import HttpResponseRedirect
from django.db.models.signals import pre_save
from urllib import urlencode
 
CONFIDENTIAL = 0
PUBLIC = 1
 
class Scope(models.Model):
    name = CharField(max_length=255,unique=True)
    description = TextField(null=True,blank=True)
    uri = URLField(null=True,blank=True)
    icon = ImageField(upload_to="scopes",blank=True,null=True)
 
    def __unicode__(self):
        return self.name
 
def scope_by_name(name):
    try:
        return Scope.objects.get(name=name)
    except Scope.DoesNotExist:
        return None

def rcode(sz):
    return os.urandom(sz).encode("hex")
 
def rpwd(sz):
    rg = random.SystemRandom()
    alphabet = string.letters[0:52] + string.digits
    return str().join(rg.choice(alphabet) for _ in range(sz))
 
def client_by_id(client_id):
    try:
        return Client.objects.get(client_id=client_id)
    except Client.DoesNotExist:
        return None
 
class Client(models.Model):
    client_type = SmallIntegerField(default=CONFIDENTIAL,choices=((CONFIDENTIAL,"Web Application"),(PUBLIC,"Native Application")))
    client_id = CharField(editable=False,max_length=255)
    client_secret = CharField(editable=False,max_length=255)
    owner = ForeignKey(User,editable=False)
    redirection_uri = URLField(verify_exists=False)
    logo = ImageField(upload_to="clients",blank=True,null=True)
    name = CharField(max_length=255)
    description = TextField()
    
    timecreated = models.DateTimeField(auto_now_add=True)
    lastupdated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.client_id

    def new_token(self,owner,ttl=None,sz=30,refresh_token=None,scopes=[]):
        exp = None
        if ttl != None:
            exp = datetime.datetime.now()+datetime.timedelta(0,ttl)
        if not scopes and refresh_token:
            scopes = refresh_token.scopes.all()
        
        t = Token.objects.create(client=self,owner=owner,value=rcode(sz),expiration_time=exp,refresh_token=refresh_token)
        for scope in scopes:
            t.scopes.add(scope)
        return t
    
    def new_authz_code(self,owner,state=None):
        token = self.new_token(owner,ttl=600)
        return Code.objects.create(token=token,state=state)
        
    def new_access_token(self,owner,refresh_token=None,scopes=[]):
        if refresh_token == None:
            refresh_token = self.new_token(owner,scopes=scopes)
        at = self.new_token(owner,ttl=3600,refresh_token=refresh_token)
        return at
    
    def redirect(self,qs):
        o = urlparse(self.redirection_uri,'https',False)
        if o.query:
            qs.update(parse_qs(o.query))
        url = urlunparse((o[0],o[1],o[2],o[3],urlencode(qs),''))
        return HttpResponseRedirect(url)
    
def _generate_client(sender, **kwargs):
    client = kwargs['instance']
    if not client:
        return
    
    if not client.client_id:
        client.client_id = "%s@%s" % (os.urandom(10).encode('hex'),socket.getfqdn(socket.gethostname()))
    if not client.client_secret:
        client.client_secret = rpwd(40)

pre_save.connect(_generate_client,sender=Client)
    
class Token(models.Model):
    owner = ForeignKey(User,editable=False)
    client = ForeignKey(Client,editable=False)
    value = CharField(max_length=255,editable=False,unique=True)
    scopes = ManyToManyField(Scope,blank=True,null=True)
    timecreated = models.DateTimeField(auto_now_add=True)
    lastupdated = models.DateTimeField(auto_now=True)
    expiration_time = models.DateTimeField(null=True,blank=True)
    refresh_token = ForeignKey('self',null=True,blank=True)
    
    def __unicode__(self):
        return "token for %s from %s [%s]" % (self.owner.__unicode__(),self.client.__unicode__(),self.scope())
    
    def scope(self):
        return ' '.join([scope.name for scope in self.scopes.all()])
    
    def is_valid(self): # We're checdking lastupdated since that is when the code is authorized
        return self.expiration_time >= datetime.datetime.now()
    
    def type(self):
        return self.refresh_token and 'access_token' or 'refresh_token'
    
    def has_scope(self,scope_name):
        for s in self.scopes.all():
            if scope_name == s.name:
                return True
        return False
    
def _generate_token(sender, **kwargs):
    token = kwargs['instance']
    if not token:
        return
    
    if not token.value:
        token.value = rcode(40)
    
pre_save.connect(_generate_token,sender=Token)
    
class Code(models.Model):
    token = ForeignKey(Token,editable=False)
    used = BooleanField(default=False,editable=False)
    authorized = BooleanField(default=False)
    state = CharField(max_length=255,editable=False,blank=True,null=True)
    
    def __unicode__(self):
        return "%s grant for %s" % (self.authorized and 'authorized' or 'un-authorized',self.token.owner)
    
    def new_access_token(self):
        return self.token.client.new_access_token(owner=self.token.owner,scopes=self.token.scopes.all())
    
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
        return Code.objects.get(token__value=token_value)
    except Code.DoesNotExist:
        return None