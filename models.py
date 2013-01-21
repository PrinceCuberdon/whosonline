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
        db_table = "online_online"
    
class AnonymousOnline(models.Model):
    key = models.CharField(max_length=60)
    last_visit = models.DateTimeField(auto_now_add=True, verbose_name="Heure de passage", help_text=u"Dernière heure de passage")
    ip = models.IPAddressField(null=True, blank=True)
    
    def __unicode__(self):
        return self.key
    
    class Meta:
        db_table ="online_anonymousonline"
