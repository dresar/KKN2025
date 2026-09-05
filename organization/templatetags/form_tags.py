from django import template
from django.template.defaultfilters import stringfilter
from django.contrib.humanize.templatetags.humanize import intcomma as django_intcomma

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    """
    Adds a CSS class to the specified form field.
    Usage: {{ form.field|add_class:"my-class" }}
    """
    if hasattr(field, 'as_widget'):
        return field.as_widget(attrs={"class": css_class})
    return field

@register.filter(name='attr')
def set_attr(field, attr_string):
    """
    Adds an attribute to the specified form field.
    Usage: {{ form.field|attr:"required:required" }}
    """
    if hasattr(field, 'as_widget'):
        attr_name, attr_value = attr_string.split(':', 1)
        attrs = {attr_name: attr_value}
        return field.as_widget(attrs=attrs)
    return field

@register.filter(name='intcomma')
def intcomma(value):
    """
    Converts an integer to a string containing commas every three digits.
    Usage: {{ value|intcomma }}
    """
    return django_intcomma(value)