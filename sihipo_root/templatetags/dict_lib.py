'''
Created on 9 Des 2017

@author: okky
'''

from django import template

register = template.Library()

@register.filter(name='dict_get')
def dict_get(dictionary, key):
    return dictionary.get(key)

@register.filter(name='dict_obj')
def dict_obj(dict_object):
    return dict_object.__dict__

@register.filter(name='dict_class')
def dict_class(class_object, attr):
    return eval('class_object.%s' % (attr))