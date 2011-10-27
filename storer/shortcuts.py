
from django.template import RequestContext
from django.shortcuts import render_to_response

def render_to(template):
    """
    Decorator for Django views that sends returned dict to render_to_response function
    with given template and RequestContext as context instance.

    If view doesn't return dict then decorator simply returns output.
    Additionally view can return two-tuple, which must contain dict as first
    element and string with template name as second. This string will
    override template name, given as parameter

    Parameters:

     - template: template name to use

    Source: Template Tag Render Decorator
            http://djangosnippets.org/snippets/1937/
    """
    def renderer(func):
        def wrapper(request, *args, **kw):
            output = func(request, *args, **kw)
            if isinstance(output, (list, tuple)):
                return render_to_response(output[1], output[0], RequestContext(request))
            elif isinstance(output, dict):
                return render_to_response(template, output, RequestContext(request))
            return output
        return wrapper
    return renderer

def update_or_create(model, filter_dict, new_values_dict):
    """
    Update a elements filtered by filter_dict from the given model,
    setting values according to new_values_dict. If the filter_dict
    does not indicate an existing row in the model, create a new entry
    based on all fields.

    http://blog.roseman.org.uk/2010/03/9/easy-create-or-update/
    """
    rows = model.objects.filter(**filter_dict).update(**new_values_dict)
    if not rows:
        new_values_dict.update(filter_dict)
        model.objects.create(**new_values_dict)
