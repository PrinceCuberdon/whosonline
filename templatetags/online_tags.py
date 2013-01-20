# -*- coding: UTF-8 -*-

from django import template

from online.models import Online

register = template.Library()

@register.filter
def is_online(value):
    """ Is online is not used anymore """
    return Online.objects.filter(user=value, online=True).values('pk').count() > 0