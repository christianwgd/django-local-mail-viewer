import fnmatch
import shutil
from pathlib import Path

import pytest
from django.conf import settings
from django.contrib import auth
from django.http import Http404
from django.test import TestCase
from django.urls import reverse
from faker import Faker

from local_mail_viewer.views import get_email_base_path, get_safe_mail_path

user_model = auth.get_user_model()

class MailTest(TestCase):

    def setUp(self):
        self.fake = Faker('de_DE')
        self.user = user_model.objects.create(username=self.fake.user_name())
        Path(f'{settings.BASE_DIR}/sent_emails').mkdir(parents=True, exist_ok=True)
        for _root, _dirs, files in Path('test_files').walk():
            mails = fnmatch.filter(files, '*.log')
            for mail_file in mails:
                shutil.copy2(f'test_files/{mail_file}', 'sent_emails')

    def tearDown(self):
        shutil.rmtree('sent_emails')

    def test_get_email_base_path(self):
        self.assertEqual(get_email_base_path(), Path(settings.BASE_DIR) / 'sent_emails')

    def test_get_email_base_path_none(self):
        with self.settings(EMAIL_FILE_PATH=None):
            self.assertIsNone(get_email_base_path())

    def test_get_safe_mail_path_no_base_path(self):
        with self.settings(EMAIL_FILE_PATH=None), pytest.raises(Http404):
            get_safe_mail_path('test.log')

    def test_mail_list(self):
        self.assertTrue((Path(settings.BASE_DIR) / 'sent_emails').is_dir())
        self.client.force_login(self.user)
        response = self.client.get(reverse('mail:mails'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['filelist']), 3)

    def test_mail_detail_plain(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('mail:mail-detail', args=['20260420-201457-4422803408.log'])
        )
        self.assertEqual(response.status_code, 200)

    def test_mail_detail_html(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('mail:mail-detail', args=['20260420-201457-4423828768.log'])
        )
        self.assertEqual(response.status_code, 200)

    def test_mail_detail_pdf_attachment(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('mail:mail-detail', args=['20260420-201457-4422595600.log'])
        )
        self.assertEqual(response.status_code, 200)

    def test_mail_download_attachment(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('mail:mail-attachment', args=['20260420-201457-4422595600.log', 'sample.pdf'])
        )
        self.assertEqual(response.status_code, 200)

    def test_mail_download_attachment_no_match(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('mail:mail-attachment', args=['20260420-201457-4422595600.log', 'test.pdf'])
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('mail:mails'))

    def test_mail_delete(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('mail:delete', args=['20260420-201457-4422595600.log']))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('mail:mails'))
        self.assertFalse((Path(settings.BASE_DIR) / 'sent_emails/20260420-201457-4422595600.log').is_file())

    def test_mail_delete_all(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('mail:delete_all'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(any(Path(settings.BASE_DIR / 'sent_emails').iterdir()))
