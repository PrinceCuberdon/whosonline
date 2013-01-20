# -*- coding: UTF-8 -*-

from django.db import models
from django.contrib.auth.models import User as AuthUser

class Online(models.Model):
    user = models.ForeignKey(AuthUser, verbose_name=u"Utilisateur", help_text=u"Utilisateur")
    last_visit = models.DateTimeField(verbose_name=u"Dernière viste", help_text=u"Date de la dernière visite")
    online = models.BooleanField(verbose_name=u"En Ligne", help_text=u"Est-ce que l'utilisateur est en ligne ?")
        
    def __unicode__(self):
        return self.user.username
    
    class Meta:
        verbose_name = "Qui est en ligne ?"
        verbose_name_plural = "Qui est en ligne ?"
    
class AnonymousOnline(models.Model):
    key = models.CharField(max_length=60)
    last_visit = models.DateTimeField(auto_now_add=True, verbose_name="Heure de passage", help_text=u"Dernière heure de passage")
    ip = models.IPAddressField(null=True, blank=True)
    
    def __unicode__(self):
        return self.key
