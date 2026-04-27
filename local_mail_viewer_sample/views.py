from django.shortcuts import render, redirect
from django.urls import reverse

from local_mail_viewer_sample.create_mail import create_mail_plain, create_mail_html


def index(request):
    return render(request, 'index.html', {})


def create_some_emails(request):
    for _index in range(2):
        create_mail_plain(attachments=[])
    create_mail_plain(attachments=['test_files/sample.pdf'])
    create_mail_plain(attachments=['test_files/test.jpg', 'test_files/sample.pdf'])
    create_mail_html(attachments=['test_files/sample.mp3'])
    create_mail_html(attachments=[])
    return redirect(reverse('home'))
