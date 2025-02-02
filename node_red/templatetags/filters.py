import uuid
from django import template

register = template.Library()

@register.filter(name="append_uuid")
def append_uuid(value):
    return f"{value}_{uuid.uuid4()}"