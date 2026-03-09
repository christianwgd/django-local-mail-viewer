import datetime
import email
import fnmatch
import os
import traceback
from email.header import make_header, decode_header

from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy


def mail_list(request):
    """ Liste von Mails anzeigen """

    class MailFile:
        def __init__(self, name, subject, date, receiver):
            self.name = name
            self.subject = subject
            self.date = date
            self.rec = receiver

    def sort_filenameby_date(logfile):
        return logfile.date  # date

    filelist = []

    email_path = getattr(settings, 'EMAIL_FILE_PATH', None)
    if email_path is not None:
        # pylint: disable=broad-except
        try:
            # pylint: disable=unused-variable
            for _root, _dirs, files in os.walk(email_path):  # @UnusedVariable
                mails = fnmatch.filter(files, '*.log')
                if len(mails) > 0:
                    for mail in mails:
                        mail_path = os.path.join(email_path, mail)
                        filedate = datetime.datetime.fromtimestamp(os.path.getmtime(mail_path))
                        with open(mail_path, encoding="utf-8") as mail_file:
                            msg = email.message_from_file(mail_file)
                            mail_subject = make_header(decode_header(msg['subject']))
                            mail_to = msg['to']
                            mailfile = MailFile(mail, mail_subject, filedate, mail_to)
                            filelist.append(mailfile)
                        mail_file.close()
                    filelist.sort(key=sort_filenameby_date, reverse=True)
        except Exception as exc:
            traceback.print_exc()
            messages.add_message(request, messages.ERROR, f'Dateifehler: {exc}!')

    return render(request, 'local_mail_viewer/mail_list.html', {
        'filelist': filelist,
    })


def mail_detail(request, filename):
    """ Mail-Datei anzeigen """

    mail = []

    email_path = getattr(settings, 'EMAIL_FILE_PATH', None)
    if email_path is not None:
        mail_file_name = os.path.join(email_path, filename)

        with open(mail_file_name, "rb") as mail_file:
            mail = mail_file.read()
            msg = email.message_from_bytes(mail)

            context = {
                'filename': filename,
                'date': msg['date'],
                'from': msg['from'],
                'to': msg['to'],
                'cc': msg['cc'],
                'subject': make_header(decode_header(msg['subject']))
            }

            if msg.is_multipart():
                for part in msg.walk():
                    attachments = []
                    content_type = part.get_content_type()
                    name = 'HTML Content' if part.get_filename() is None else part.get_filename()
                    if content_type == 'text/plain':
                        context['body'] = part.get_payload(decode=True).decode('utf-8')
                    elif content_type == 'text/html':
                        payload = part.get_payload(decode=True)
                        if payload is not None:
                            content = payload.decode('utf-8')
                        attachment = {'name': name, 'type': content_type, 'content': content}
                    else:
                        attachment = {'name': name, 'type': content_type, 'content': None}
                        # payload = part.get_payload(decode=True)
                        # if payload and att_name:
                            # media_path = 'media/attachments/'
                            # Path(media_path).mkdir(parents=True, exist_ok=True)
                            # att_file_name = Path(media_path) / att_name
                            # with open(att_file_name, 'wb') as f:
                            #     f.write(payload)
                            #     context['att_content'] = (
                            #         f'<a href="/{att_file_name}" target="_blank" rel="noopener noreferrer">'
                            #         f'{att_file_name}</a>'
                            #     )
                    attachments.append(attachment)
                context['attachments'] = attachments



            else:
                context['body'] = msg.get_payload(decode=True).decode('utf-8')

        mail_file.close()

    return render(request, 'local_mail_viewer/mail_detail.html', context)


def mail_delete(request, filename):
    """ Eine einzelne Mail-Datei löschen """

    email_path = getattr(settings, 'EMAIL_FILE_PATH', None)
    if email_path is not None:
        filepath = os.path.join(email_path, filename)
        os.remove(filepath)

    return redirect(reverse_lazy('mail:mails'))


def mail_delete_all(request):
    """ Alle Mail-Dateien löschen """

    email_path = getattr(settings, 'EMAIL_FILE_PATH', None)
    if email_path is not None:
        # pylint: disable=broad-except
        try:
            # pylint: disable=unused-variable
            for _root, _dirs, files in os.walk(email_path):  # @UnusedVariable
                filelist = fnmatch.filter(files, '*.log')
                if len(filelist) > 0:
                    for filename in filelist:
                        filepath = os.path.join(email_path, filename)
                        os.remove(filepath)
        except Exception as exc:
            messages.add_message(request, messages.ERROR, f'Dateifehler: {exc}!')

    return redirect(reverse_lazy('mail:mails'))
