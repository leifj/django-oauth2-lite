"""Views for django_oauth2_lite application."""

from django.shortcuts import render_to_response, get_object_or_404 
from django_oauth2_lite.models import Client, Code, Scope, scope_by_name, code_by_token, token_by_value
from django_oauth2_lite.forms import CodeForm, AccessRequest
from django.http import HttpResponseBadRequest, HttpResponse,\
    HttpResponseRedirect
from django.utils import simplejson
from django_oauth2_lite.decorators import clientauth_required
from django.views.generic.list_detail import object_list
from django.contrib.auth.decorators import login_required
from django.views.generic.create_update import create_object

def _get(request,key,dflt=None):
    if request.GET.has_key(key):
        return request.GET[key]
    else:
        return dflt
    
def _post(request,key,dflt=None):
    if request.POST.has_key(key):
        return request.POST[key]
    else:
        return dflt

@clientauth_required
def authorize(request,template='templates/django_oauth2_lite/authorize.html'):
    
    state = None
    if request.REQUEST.has_key('state'):
        state = request.REQUEST['state']
        
    if request.method == 'POST':
        form = CodeForm(request.POST)
        if form.is_valid():
            code = code_by_token(form.cleaned_data['code'])
            if code == None:
                return code.token.client.redirect({'state': state, 'error': 'invalid_request'})
            
            if form.cleaned_data['authorized']:
                code.authorized = True
                code.save()
                return code.token.client.redirect({'state': state,'code': code.value})
            else:
                code.delete()
                return code.token.client.redirect({'error': 'access_denied','state': state})
        else:
            return code.token.client.redirect({'error': 'invalid_request','state': state})  
    else:
        client = get_object_or_404(Client,client_id=_get(request,'client_id'))
        
        if _get(request,'response_type','code') != 'code':
            return code.client.redirect({'error': 'unsupported_response_type','state': state})
        
        code = client.new_authz_code(state=state)
        for n in _get(request,'scope',"").split(' '):
            scope = scope_by_name(n)
            if scope == None:
                return client.redirect({'error': 'invalid_scope','state': state})
            code.scopes.add(scope)
            
        form = CodeForm(instance=code,state=state)
    
    return render_to_response(template,{"form": form})

def json_response(data):
    r = HttpResponse(simplejson.dumps(data),content_type='application/json')
    r['Cache-Control'] = 'no-store'
    r['Pragma'] = 'no-cache'
    
    return r

def token_error(error):
    return json_response({'error': error})

@clientauth_required
def token(request):
    if not request.method == 'POST':
        return HttpResponseBadRequest()
    
    grant_type = _post(request,'grant_type')
    at = None
    if grant_type == 'authorization_code':
        code = code_by_token(_post(request,'code'))
        if not code or not code.is_valid():
            return token_error('invalid_grant')
        
        at = code.new_access_token()
    elif grant_type == 'refresh_token':
        rt = token_by_value(_post(request,'refresh_token'))
        if not rt or not rt.is_valid():
            return token_error('invalid_grant')
        ## TODO: scope is silently ignored right now - should honor request to narrow scope
        at = rt.client.new_access_token(refresh_token=rt)
    else:
        return token_error('unsupported_grant_type')
    
    return json_response({'access_token': at.value,
                          'token_type': at.type,
                          'expires_in': 3600,
                          'refresh_token': at.refresh_token.value})
    
@login_required
def clients(request,template_name='templates/django_oauth2_lite/clients.html'):
    queryset = Client.objects.filter(owner=request.user)
    return object_list(request, 
                       queryset=queryset, 
                       template_name=template_name)

@login_required
def add_client(request,template_name="templates/django_oauth2_lite/client_form.html"):
    return create_object(request, 
                         model=Client, 
                         template_name=template_name,
                         post_save_redirect="/oauth/clients",
                         extra_context={'user': request.user})

@login_required
def remove_client(request,pk):
    client = get_object_or_404(Client,id=pk)
    client.delete()
    return HttpResponseRedirect("/oauth/clients")
