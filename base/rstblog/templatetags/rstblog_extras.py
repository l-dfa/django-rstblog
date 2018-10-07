# rstblog_extras.py

#import pdb
import os
from django import template

register = template.Library()

@register.filter
def tail(value, sep=None):
    """return tail from a string of words"""
    if sep == None:
        sep = os.sep
    #pdb.set_trace()
    splitted = value.rsplit(sep, 1)
    if len(splitted) == 1:
        result = splitted[0]
    else:
        result = splitted[1]
    return result[:]
    
@register.filter
def length(value):
    """return len(value)"""
    return len(value)
    
@register.filter
def bitwise_and(value, arg):
    """return (value & arg)"""
    return value & arg
    
@register.filter
def bitwise_or(value, arg):
    """return (value | arg)"""
    return value | arg
    