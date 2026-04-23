# django-local-mail-viewer

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Run Test](https://github.com/christianwgd/django-local-mail-viewer/actions/workflows/python-test.yml/badge.svg)](https://github.com/christianwgd/django-local-mail-viewer/actions/workflows/python-test.yml)
[![codecov](https://codecov.io/github/christianwgd/django-local-mail-viewer/graph/badge.svg?token=i3jXueSzIY)](https://codecov.io/github/christianwgd/django-local-mail-viewer)


``django-local-mail-viewer``is a Django app that provides a simple email viewer 
for emails during development. It is used together with the email backend 
``django.core.mail.backends.filebased.EmailBackend``. You can browse the emails
from through a web interface and view the content of those emails as well as 
possible attachments.

## Documentation

Install via pipy running ``pip install django-local-mail-viewer`` and add 
``django_local_mail_viewer`` to your ``INSTALLED_APPS`` of your development 
settings file or add this for more flexibility:
```
if DEBUG:
    INSTALLED_APPS += ['django_local_mail_viewer']
```

Add ``path('mail/', include('local_mail_viewer.urls'))`` to your ``urls.py``.
This can also be done conditionally:
```
if settings.DEBUG:
    urlpatterns += path('mail/', include('local_mail_viewer.urls'))
```

Set your email config as follows:
```
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
DEFAULT_FROM_EMAIL = 'some_name@some_domain.tld'
EMAIL_FILE_PATH = BASE_DIR / 'sent_emails'
```

You can choose the EMAIL_FILE_PATH to any name, it will be detected automatically.

**Don't use the local mail viewer in production!**
