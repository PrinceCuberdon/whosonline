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

"""
Test for Online app
"""
import datetime
from importlib import import_module

from django.contrib.auth.models import User

from django.test import TestCase, Client
from django.conf import settings
from django.core.urlresolvers import reverse

from core.bandcochon.models import Utilisateur
from .processor import *
from .views import *


class TestOnlineModel(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testusername", email="test@example.com")

    def test_create(self):
        ol = Online.objects.create(user=self.user, last_visit=timezone.now(), online=True)
        self.assertTrue(ol.online)
        self.assertEqual(unicode(ol), u"testusername")


class TestProcessor(TestCase):
    def setUp(self):
        user = User.objects.create(username="testusername", email="test@example.com")
        self.utili = Utilisateur.objects.create(user=user)
        self.anon = AnonymousOnline.objects.create(key="testkey", ip="127.0.0.1")
        self.ol = Online.objects.create(user=user, last_visit=timezone.now(), online=True)

    def test_online(self):
        resp = online(None)
        self.assertIsInstance(resp, dict)

        self.assertIn('online_user_count', resp)
        self.assertIn('online_anonymous_count', resp)
        self.assertIn('online_users', resp)

        self.assertEqual(resp['online_user_count'], 1)
        self.assertEqual(resp['online_anonymous_count'], 1)
        self.assertIsInstance(resp['online_users'], list)
        self.assertEqual(len(resp['online_users']), 1)


class TestView(TestCase):
    def _create_session_client(self):
        """
        Create a new client with session inside

        :return: A client object
        """
        c = Client()
        session_engine = import_module(settings.SESSION_ENGINE)
        store = session_engine.SessionStore()
        store.save()
        c.cookies[settings.SESSION_COOKIE_NAME] = store.session_key

        return c

    def setUp(self):
        self.user = User.objects.create_user(username="testusername", email="test@example.com", password="testpassword")
        self.utili = Utilisateur.objects.create(user=self.user)

    def test_remove_older(self):
        AnonymousOnline.objects.create(key="testkey", ip="127.0.0.1")
        anon_old = AnonymousOnline.objects.create(key="anothertestkey", ip="127.0.0.1")
        anon_old.last_visit = timezone.now() - datetime.timedelta(seconds=61)
        anon_old.save()

        Online.objects.create(user=self.user, last_visit=timezone.now(), online=True)
        Online.objects.create(user=self.user, last_visit=timezone.now() - datetime.timedelta(seconds=61), online=True)

        remove_older()
        self.assertEqual(Online.objects.filter(online=True).count(), 1)
        self.assertEqual(AnonymousOnline.objects.all().count(), 1)

    def test_set_online_anonymous(self):
        c = self._create_session_client()
        c.post(reverse('online'))
        self.assertEqual(Online.objects.all().count(), 0)
        self.assertEqual(AnonymousOnline.objects.all().count(), 1)

    def test_set_online_registred(self):
        client = self._create_session_client()
        success = client.login(username="testusername", password="testpassword")
        self.assertTrue(success)
        client.post(reverse('online'))
        self.assertEqual(Online.objects.all().count(), 1)
        self.assertEqual(AnonymousOnline.objects.all().count(), 0)

    def test_set_offline_anonymous(self):
        c = self._create_session_client()

        c.post(reverse('online'))  # Create an entry
        self.assertEqual(AnonymousOnline.objects.all().count(), 1)
        c.post(reverse('offline'))  # Remove this entry
        self.assertEqual(Online.objects.all().count(), 0)
        self.assertEqual(AnonymousOnline.objects.all().count(), 0)

    def test_set_offline_registred(self):
        c = self._create_session_client()
        success = c.login(username="testusername", password="testpassword")
        self.assertTrue(success)
        c.post(reverse('online'))  # Create an entry
        c.post(reverse('offline'))  # Remove this entry
        self.assertEqual(Online.objects.all().count(), 1)  # The registred user is still in database but marked as offline
        self.assertEqual(Online.objects.filter(online=True).count(), 0)
        self.assertEqual(Online.objects.filter(online=False).count(), 1)
        self.assertEqual(AnonymousOnline.objects.all().count(), 0)

    def test_get_whos_online_simple(self):
        """ Test values and types """
        c = self._create_session_client()
        response = c.get(reverse('whosonline'))
        self.assertEqual(response['Content-Type'], "application/json")
        response = json.loads(response.content)
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response.keys()), 3)
        self.assertTrue(response.has_key('visitors'))
        self.assertTrue(response.has_key('flags'))
        self.assertTrue(response.has_key('users'))

        self.assertEqual(response['visitors'], 1)
        self.assertIsInstance(response['flags'], list)
        self.assertEqual(len(response['flags']), 0)
        self.assertIsInstance(response['users'], list)
        self.assertEqual(len(response['users']), 0)

    def test_get_whos_online_registred(self):
        """ Type and values are tested in test_get_whos_online_simple """
        c = self._create_session_client()
        c.login(username="testusername", password="testpassword")
        response = c.get(reverse('whosonline'))
        response = json.loads(response.content)
        self.assertEqual(response['visitors'], 0)
        self.assertEqual(len(response['flags']), 0)
        self.assertEqual(len(response['users']), 1)

    def test_get_whos_online_flags(self):
        AnonymousOnline.objects.create(key="anothertestkey", ip="5.9.73.34")  # bandcochon.re IP (Germany)
        c = self._create_session_client()
        response = c.get(reverse('whosonline'))
        result = json.loads(response.content)
        self.assertTrue(result.has_key('flags'))
        flags = result['flags']
        self.assertIsInstance(flags, list)
        location = flags[0]
        self.assertIsInstance(location, dict)
        self.assertTrue(location.has_key('code'))
        self.assertTrue(location.has_key('name'))
        self.assertEqual(location['code'], u"de")
        self.assertEqual(location['name'].lower(), u"germany")
