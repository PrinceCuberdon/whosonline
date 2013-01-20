# -*- coding: UTF-8 -*-

from django.contrib import admin

from online.models import Online, AnonymousOnline

class OnlineAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'online', 'last_visit',)
    
class AnonymousOnlineAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'last_visit', )
    
admin.site.register(Online, OnlineAdmin)
admin.site.register(AnonymousOnline, AnonymousOnlineAdmin)