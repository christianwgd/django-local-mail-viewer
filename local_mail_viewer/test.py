import os
import pathlib
import shutil

from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from faker import Faker


user_model = auth.get_user_model()


class MailTest(TestCase):

    def setUp(self):
        self.fake = Faker('de_DE')
        self.ka_group = Group.objects.create(name='Kontrollausschuss')
        self.user = user_model.objects.create(username=self.fake.user_name())
        self.user.groups.add(self.ka_group)

    def tearDown(self):
        os.remove('sent_emails/test_mail.log')

    def test_mail_list(self):
        pathlib.Path(f'{settings.BASE_DIR}/sent_emails').mkdir(parents=True, exist_ok=True)
        shutil.copy2('test/test_mail.log', 'sent_emails/test_mail.log')
        self.client.force_login(self.user)
        response = self.client.get(reverse('mail:mails'))
        self.assertEqual(response.status_code, 200)
        # self.assertEqual(len(response.context['penalties'].qs), 2)
        # self.assertIsInstance(response.context['penalties'].qs.first(), Penalty)
