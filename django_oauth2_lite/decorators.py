'''
Created on Nov 1, 2011

@author: leifj
'''
import functools
from django_oauth2_lite.models import client_by_id, token_by_value
from django.http import HttpResponseForbidden, HttpResponseNotAllowed

def clientauth_required(func):    
    @functools.wraps(func)
    def new_func(*args,**kwargs):
        request = args[0]
        client_id = None
        client_secret = None
        if request.META.has_key('HTTP_AUTHORIZATION'):
            ah = request.META['HTTP_AUTHORIZATION']
            parts = ah.split(' ')
            if parts[0] == 'Basic':
                client_id,sep,client_secret = parts[1].decode('base64') 
        elif request.GET.has_key('client_id'):
            client_id = request.GET['client_id']
            if request.GET.has_key('client_secret'):
                client_secret = request.GET['client_secret']
            else:
                return HttpResponseForbidden()
        else:
            return func(*args,**kwargs)
        
        client = client_by_id(client_id)
        if client == None:
            return HttpResponseForbidden()
        if client.client_secret != client_secret:
            return HttpResponseForbidden()
        
        return func(*args,**kwargs)
    return new_func
    
def oauth_required(func,scope=None):
    @functools.wraps(func)
    def new_func(*args,**kwargs):
        request = args[0]
        if request.META.has_key('HTTP_AUTHORIZATION'):
            ah = request.META['HTTP_AUTHORIZATION']
            parts = ah.split(' ')
            if parts[0] == 'Bearer':
                token = token_by_value(parts[1])
                
                if not token or not token.is_valid():
                    return HttpResponseForbidden()
                if scope and not token.has_scope(scope):
                    return HttpResponseForbidden()
                
                request.user = token.owner
                return func(*args,**kwargs)
            
        return HttpResponseForbidden()
    return new_func