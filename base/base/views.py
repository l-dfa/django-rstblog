# base/views.py

from django.shortcuts import redirect

def index(request):
    ''' list articles '''
    
    return redirect ( 'rstblog:index' )
