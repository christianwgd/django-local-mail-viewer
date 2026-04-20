import pathlib
import shutil

from django.conf import settings
from django.contrib import auth
from django.test import TestCase
from django.urls import reverse
from faker import Faker

from local_mail_viewer_sample.create_mail import create_mail_plain

user_model = auth.get_user_model()


class MailTest(TestCase):

    def setUp(self):
        self.fake = Faker('de_DE')
        self.user = user_model.objects.create(username=self.fake.user_name())
        pathlib.Path(f'{settings.BASE_DIR}/sent_emails').mkdir(parents=True, exist_ok=True)
        create_mail_plain()

    def tearDown(self):
        shutil.rmtree('sent_emails')

    def test_mail_list(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('mail:mails'))
        self.assertEqual(response.status_code, 200)
        # self.assertEqual(len(response.context['penalties'].qs), 2)
        # self.assertIsInstance(response.context['penalties'].qs.first(), Penalty)
