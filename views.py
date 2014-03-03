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

import datetime
import json

from django.core.context_processors import csrf
from django.http import HttpResponse

try:
    # Django <= 1.3
    from django.contrib.gis.utils import GeoIP
    HAVE_GEOIP = True
except ImportError:
    # Django >= 1.4
    try:
        from django.contrib.gis.geoip import GeoIP
        HAVE_GEOIP = True
    except ImportError as e:
        print e
        HAVE_GEOIP = False

from .models import Online, AnonymousOnline
from libs.notification import ajax_log


def remove_older():
    """ Remove old anonymous and  and set users offline if  last_visit - 60 secs
    (cause status are refreshed every 30 s) """
    before_time = datetime.datetime.now() - datetime.timedelta(seconds=60)
    AnonymousOnline.objects.filter(last_visit__lte=before_time).delete()
    Online.objects.filter(last_visit__lte=before_time).update(online=False)


def set_online(request):
    """ Set the user online. We use csrf_token cause a Chrome private navigation
    bug. """
    token = str(csrf(request)['csrf_token'])
    try:
        if request.user.is_authenticated():
            online, created = Online.objects.get_or_create(user=request.user, defaults={
                'last_visit': datetime.datetime.now(),
                'online': True
            })
            if not created:
                online.last_visit = datetime.datetime.now()
                online.online = True
            online.save()
        else:
            anon, created = AnonymousOnline.objects.get_or_create(key=token, defaults={
                'key': token,
                'last_visit': datetime.datetime.now(),
                'ip': request.META['REMOTE_ADDR']
            })
            if not created:
                anon.last_visite = datetime.datetime.now()
                
            anon.save()
        remove_older()
                
    except Exception as e:
        """ sometime the database is not enougth fast. So we remove all keys """
        AnonymousOnline.objects.filter(key=token).delete()
        ajax_log("online.views.setonline : %s" % e)
        
    return HttpResponse('')


def set_offline(request):
    """ Set the user offline """
    try:
        if request.user.is_authenticated():
            online = Online.objects.get(user=request.user)
            online.online = False
            online.save()
        else:
            try:
                AnonymousOnline.objects.filter(key=str(csrf(request)['csrf_token'])).delete()
            except:
                pass

        remove_older();
            
    except Exception as e:
        ajax_log("online.views.Set_offline: %s "% e)

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
        if HAVE_GEOIP:
            if data['visitors'] > 0:
                g = GeoIP()        
                for ip in AnonymousOnline.objects.all().only('ip'):
                    country = g.country(str(ip.ip))
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
                'avatar': user.user.get_profile().avatar_or_default(),
                'user': user.user.username
            })
        return HttpResponse(json.dumps(data), mimetype="application/json")
    except Exception as e:
        ajax_log("online.views.get_whos_online : %s " % e)
    return HttpResponse('{}', mimetype="application/json")
