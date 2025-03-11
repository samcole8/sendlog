"""Utility functions for getting information about a class or object's origins."""

# Class functions

def cls_name(cls):
    return cls.__name__

def cls_fullname(cls):
    return f"{cls.__module__}.{cls.__qualname__}"

def cls_bases(cls):
    return cls.__bases__

# Object functions

def obj_class(obj):
    return obj.__class__

def obj_name(obj):
    return cls_name(obj_class(obj))

def obj_fullname(obj):
    return cls_fullname(obj_class(obj))

def obj_bases(obj):
    return cls_bases(obj_class(obj))
