'''
Created on Nov 1, 2011

@author: leifj
'''

from django.forms.models import ModelForm
from django_oauth2_lite.models import Code
from django.forms.forms import Form
from django.forms.fields import CharField, URLField
    
class CodeForm(ModelForm):
    
    class Meta:
        model = Code
        
class AccessRequest(Form):
    grant_type = CharField(required=True)
    code = CharField(required=True)
    redirect_uri = URLField(required=True)