'''
Created on Nov 1, 2011

@author: leifj
'''

from django.forms.models import ModelForm
from django_oauth2_lite.models import Code, Client
from django.forms.forms import Form
from django.forms.fields import CharField, URLField
from django.forms.widgets import HiddenInput
    
class CodeForm(ModelForm):
    code = CharField(widget=HiddenInput)
    
    class Meta:
        fields = ['authorized']
        model = Code
        
class ClientForm(ModelForm):
    
    class Meta:
        model = Client
        
class AccessRequest(Form):
    grant_type = CharField(required=True)
    code = CharField(required=True)
    redirect_uri = URLField(required=True)