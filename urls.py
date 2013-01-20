# -*- coding: UTF-8 -*-

from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    url("^online/$",        'online.views.set_online', name="online"),
    url('^offline/$',       'online.views.set_offline', name="offline"),
    url('^whosonline/$',    'online.views.get_whos_online', name="whosonline"),
)
