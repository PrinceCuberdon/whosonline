# -*- coding: UTF-8 -*-

from bandcochon.models import Utilisateur
from online.models import AnonymousOnline, Online

def online(request):
    """ """
    avatars = []
    for b in Utilisateur.objects.filter(user__pk__in=Online.objects.filter(online=True).only('user__pk')):
        avatars.append(b.avatar_or_default())
        
    return {
        'online_user_count': Online.objects.filter(online=True).only('pk').count(),
        'online_anonymous_count': AnonymousOnline.objects.all().only('pk').count(),
        'online_user_avatars': avatars
    }