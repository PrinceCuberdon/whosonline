# -*- coding: UTF-8 -*-
# 
# WhosOnline (c) Prince Cuberdon 2011 and Later <princecuberdon@bandcochon.fr>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is furnished
# to do so, subject to the following conditions:
#
# * The above copyright notice and this permission notice shall be included in
#   all copies or substantial portions of the Software.
#
# * The Software is provided "as is", without warranty of any kind, express or
#   implied, including but not limited to the warranties of merchantability,
#   fitness for a particular purpose and noninfringement. In no event shall the
#   authors or copyright holders be liable for any claim, damages or other liability,
#   whether in an action of contract, tort or otherwise, arising from, out of or in
#   connection with the software or the use or other dealings in the Software.

import json

from django.core.context_processors import csrf
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.views.generic import View
try:
	from django.contrib.gis.geoip import GeoIP
except ImportError:
	# TODO: Fallback
	import pygeoip as GeoIP

from .models import Online, AnonymousOnline
from notification import ajax_log
from libs import MustBeAjaxMixin


def remove_older():
    """ Remove old anonymous and  and set users offline if  last_visit - 60 secs
    (cause status are refreshed every 30 s) """
    before_time = timezone.now() - timezone.timedelta(seconds=60)
    AnonymousOnline.objects.filter(last_visit__lte=before_time).delete()
    Online.objects.filter(last_visit__lte=before_time).update(online=False)


class SetOnlineView(MustBeAjaxMixin, View):
    def get(self, request):
        token = str(csrf(request)['csrf_token'])
        if request.user.is_authenticated():
            online, created = Online.objects.get_or_create(user=request.user, defaults={
                'last_visit': timezone.now(),
                'online': True,
                'url': request.META['HTTP_REFERER']
            })

            if not created:
                online.last_visit = timezone.now()
                online.online = True
            online.save()
        else:
            if 'HTTP_X_REAL_IP' in request.META:
                request.META['REMOTE_ADDR'] = request.META['HTTP_X_REAL_IP']

            anon, created = AnonymousOnline.objects.get_or_create(key=token, defaults={
                'key': token,
                'last_visit': timezone.now(),
                'ip': request.META['REMOTE_ADDR'],
                'url': request.META['HTTP_REFERER']
            })
            if not created:
                anon.last_visit = timezone.now()

            anon.save()
        remove_older()

        return JsonResponse({'success': True})


def set_online(request):
    """ Set the user online. We use csrf_token cause a Chrome private navigation
    bug. """
    token = request.session.session_key
    try:
        if request.user.is_authenticated():
            online, created = Online.objects.get_or_create(user=request.user, defaults={
                'last_visit': timezone.now(),
                'online': True
            })
            if not created:
                online.last_visit = timezone.now()
                online.online = True

            online.referer = request.META.get('HTTP_REFERER')
            online.save()
        else:
            if 'HTTP_X_REAL_IP' in request.META:
                request.META['REMOTE_ADDR'] = request.META['HTTP_X_REAL_IP']

            anon, created = AnonymousOnline.objects.get_or_create(key=token, defaults={
                'key': token,
                'last_visit': timezone.now(),
                'ip': request.META['REMOTE_ADDR']
            })

            if not created:
                anon.last_visit = timezone.now()

            anon.referer = request.META.get('HTTP_REFERER')
            anon.save()
        remove_older()

    except:
        """ sometime the database is not enougth fast. So we remove all keys """
        AnonymousOnline.objects.filter(key=token).delete()

    return HttpResponse('')


def set_offline(request):
    """ Set the user offline """
    try:
        if request.user.is_authenticated():
            online = Online.objects.get(user=request.user)
            online.online = False
            online.save()
        else:
            AnonymousOnline.objects.filter(key=request.session.session_key).delete()

        remove_older()

    except Exception as e:
        ajax_log("online.views.Set_offline: %s " % e)

    return HttpResponse('')


def get_whos_online(request):
    """ Ajax request. """
    try:
        set_online(request)
        remove_older()
        data = {
            'users': [],
            'visitors': AnonymousOnline.objects.all().values('pk').count(),
            'flags': []
        }

        flags = []
        if data['visitors'] > 0:
            geoip = GeoIP()
            for ip in AnonymousOnline.objects.all().only('ip'):
                country = geoip.country(str(ip.ip))
                if country['country_code'] is not None:
                    flags.append({
                        'code': country['country_code'].lower(),
                        'name': country['country_name']}
                    )
            codes = []
            for flag in flags:
                if flag['code'] in codes:
                    continue
                codes.append(flag['code'])
                data['flags'].append(flag)

        for user in Online.objects.filter(online=True):
            data['users'].append({
                'pk': user.user.pk,
                'avatar': user.user.profile.avatar_or_default(),
                'user': user.user.username
            })
        return HttpResponse(json.dumps(data), content_type="application/json")

    except Exception as e:
        ajax_log("online.views.get_whos_online : %s " % e)

    return HttpResponse('{}', content_type="application/json")


def admin_get_whos_online(request):
    """ Ajax request. """
    # TODO: Check user auth
    data = {
        'anonymous': [],
        'hunters': []
    }

    geoip = GeoIP()
    for anon in list(AnonymousOnline.objects.all()):
        data['anonymous'].append({
            'user': 'Anonymous : {0}'.format(anon.ip),
            'country': geoip.country(str(anon.ip)),
            'url': anon.referer,
            'time': str(anon.last_visit)
        })

    for hunter in list(Online.objects.filter(online=True)):
        data['hunters'].append({
            'user': hunter.user.username,
            'url': hunter.referer,
            'time': str(hunter.last_visit)
        })

    remove_older()

    return JsonResponse(data)
