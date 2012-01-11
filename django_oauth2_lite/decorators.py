'''
Created on Nov 1, 2011

@author: leifj
'''
import functools
from django_oauth2_lite.models import client_by_id, token_by_value
from django.http import HttpResponseForbidden, HttpResponseNotAllowed,\
    HttpResponseBadRequest

try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps  # Python 2.4 fallback.

def clientauth_required(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        request = args[0]
        client_id = None
        client_secret = None
        if request.META.has_key('HTTP_AUTHORIZATION'):
            ah = request.META['HTTP_AUTHORIZATION']
            parts = ah.split(' ')
            if parts[0] == 'Basic':
                client_id,sep,client_secret = parts[1].decode('base64') 

        if request.REQUEST.has_key('client_id'):
            client_id = request.REQUEST['client_id']
            if request.REQUEST.has_key('client_secret'):
                client_secret = request.REQUEST['client_secret']

        if not client_id:
            return func(*args,**kwargs)
        
        client = client_by_id(client_id)
        if client == None:
            return HttpResponseForbidden("no client")
        if client.client_secret != client_secret:
            return HttpResponseForbidden("bad secret")
        
        return func(*args,**kwargs)
    return wrapper
    
def oauth2_required(scope=None):
    def wrap(func):
        def wrapper(*args,**kwargs):
            request = args[0]
            if request.META.has_key('HTTP_AUTHORIZATION'):
                ah = request.META['HTTP_AUTHORIZATION']
                parts = ah.split(' ')
                if parts[0] == 'Bearer':
                    token = token_by_value(parts[1])
                    
                    if not token:
                        return HttpResponseForbidden("No token")
                    if not token.is_valid():
                        token.delete()
                        return HttpResponseForbidden("Token expired")
                    if scope and not token.has_scope(scope):
                        return HttpResponseForbidden("Token out of scope")
                    
                    request.user = token.owner
                    request.client = token.client
                    return func(*args,**kwargs)
                
            return HttpResponseBadRequest("No authorization")
        return wrapper
    return wrap
