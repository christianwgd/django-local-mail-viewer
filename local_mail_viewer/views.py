import datetime
import email
import fnmatch
import os
from dataclasses import dataclass
from email.header import make_header, decode_header
from pathlib import Path

from django.conf import settings
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

DATE_TIME_FORMAT = '%a, %d %b %Y %H:%M:%S %z'


@dataclass
class MailFile:
    name: str
    subject: str
    date: datetime.datetime
    rec: str
    has_attachments: bool


def get_email_base_path():
    email_path = getattr(settings, 'EMAIL_FILE_PATH', None)
    if email_path is None:
        return None
    return Path(email_path).resolve()


def get_safe_mail_path(filename):
    base_path = get_email_base_path()
    if base_path is None:
        raise Http404("Email path is not configured")


def mail_list(request):
    """Show a list of mail files."""

    filelist = []
    email_path = get_email_base_path()

    if email_path is not None:
        for mail_path in email_path.glob('*.log'):
            filedate = datetime.datetime.fromtimestamp(mail_path.stat().st_mtime)

            with open(mail_path, encoding="utf-8") as mail_file:
                msg = email.message_from_file(mail_file)

            mailfile = MailFile(
                name=mail_path.name,
                subject=str(make_header(decode_header(msg.get('subject', '')))),
                date=filedate,
                rec=msg.get('to', ''),
                has_attachments=msg.is_multipart(),
            )
            filelist.append(mailfile)

    filelist.sort(key=lambda mail_file: mail_file.date, reverse=True)

    return render(request, 'local_mail_viewer/mail_list.html', {
        'filelist': filelist,
    })


def mail_detail(request, filename):

    """ Show mail details """

    mail = []

    email_path = getattr(settings, 'EMAIL_FILE_PATH', None)
    if email_path is not None:
        mail_file_name = os.path.join(email_path, filename)

        with open(mail_file_name, "rb") as mail_file:
            mail = mail_file.read()
            msg = email.message_from_bytes(mail)

            context = {
                'filename': filename,
                'date': datetime.datetime.strptime(msg['date'], DATE_TIME_FORMAT),
                'from': msg['from'],
                'to': msg['to'],
                'cc': msg['cc'],
                'subject': make_header(decode_header(msg['subject']))
            }

            if msg.is_multipart():
                attachments = []
                for part in msg.walk():
                    content_type = part.get_content_type()
                    name = 'HTML Content' if part.get_filename() is None else part.get_filename()
                    if content_type == 'text/plain':
                        context['body'] = part.get_payload(decode=True).decode('utf-8')
                    elif content_type == 'text/html':
                        payload = part.get_payload(decode=True)
                        if payload is not None:
                            content = payload.decode('utf-8')
                            attachments.append({'name': name, 'type': content_type, 'content': content})
                    elif content_type in ['multipart/alternative', 'multipart/mixed']:
                        pass  # skipt this
                    else:
                        attachments.append({'name': name, 'type': content_type, 'content': None})
                context['attachments'] = attachments
            else:
                context['body'] = msg.get_payload(decode=True).decode('utf-8')

        mail_file.close()

    return render(request, 'local_mail_viewer/mail_detail.html', context)


def download_attachment(request, filename, name):
    """ Download an mail attachment """

    mail = []

    email_path = getattr(settings, 'EMAIL_FILE_PATH', None)
    if email_path is not None:
        mail_file_name = os.path.join(email_path, filename)

        with open(mail_file_name, "rb") as mail_file:
            mail = mail_file.read()
            msg = email.message_from_bytes(mail)

            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_filename() == name:
                        return HttpResponse(part.get_payload(decode=True), content_type=part.get_content_type())
    return redirect(reverse_lazy('mail:mails'))


def mail_delete(request, filename):
    """ Delete a single mail file """

    email_path = getattr(settings, 'EMAIL_FILE_PATH', None)
    if email_path is not None:
        filepath = os.path.join(email_path, filename)
        os.remove(filepath)

    return redirect(reverse_lazy('mail:mails'))


def mail_delete_all(request):
    """ Delete all mail files """

    email_path = getattr(settings, 'EMAIL_FILE_PATH', None)
    if email_path is not None:
        for _root, _dirs, files in os.walk(email_path):  # @UnusedVariable
            filelist = fnmatch.filter(files, '*.log')
            if len(filelist) > 0:
                for filename in filelist:
                    filepath = os.path.join(email_path, filename)
                    os.remove(filepath)

    return redirect(reverse_lazy('mail:mails'))
