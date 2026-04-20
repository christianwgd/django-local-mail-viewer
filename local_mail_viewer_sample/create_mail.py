from django.conf import settings
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.template.loader import render_to_string
from faker import Faker


def create_mail_plain(attachment: str | None = None):
    fake = Faker(settings.LANGUAGE_CODE)
    email = EmailMessage(
        subject=fake.sentence(),
        body='\n\n'.join(fake.texts(nb_texts=3, max_nb_chars=200)),
        from_email=fake.ascii_email(),
        to=[fake.ascii_email() for index in  range(2)],
        cc=[fake.ascii_email() for index in  range(2)],
    )
    if attachment is not None:
        email.attach_file(attachment)
    email.send(fail_silently=False)


def create_mail_html(attachment: str | None = None):
    fake = Faker(settings.LANGUAGE_CODE)
    email = EmailMultiAlternatives(
        subject=fake.sentence(),
        body='\n\n'.join(fake.texts(nb_texts=3, max_nb_chars=200)),
        from_email=fake.ascii_email(),
        to=[fake.ascii_email() for index in range(2)],
        cc=[fake.ascii_email() for index in range(2)],
    )
    context = {
        'topic': 'Test E-Mail',
        'body': email.body,
    }
    html_content = render_to_string(
        template_name='email.html',
        context=context,
    )
    email.attach_alternative(html_content, "text/html")
    if attachment is not None:
        email.attach_file(attachment)
    email.send(fail_silently=False)
