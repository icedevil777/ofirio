import logging

from email.mime.image import MIMEImage
from celery import shared_task

import common.tasks as tasks
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from common.utils import get_absolute_url, strip_tags


logger = logging.getLogger('emails')


@shared_task
def send_mail(to, subject='', body='', template='', context=None, images=(), attachment=None):
    """
    Sending mail abstraction

    It's possible to pass template path and context,
    or already formed html (or plain) body as a 'body' arg
    """
    from_email = settings.PROJECT_BACK_EMAIL
    to = [to] if isinstance(to, str) else to

    if not body:
        context = context or {}
        context['subject'] = context.get('subject', subject)
        body = render_to_string(template, context).strip()

    mail = _form_mail(subject, body, from_email, to, images, attachment=attachment)
    logger.info('Sending "%s" email to %s...', subject, to)
    status = mail.send()
    logger.info('Sending "%s" email to %s completed with status %s', subject, to, status)
    return status


def _form_mail(subject, body, from_email, to, images, attachment=None):
    mail = EmailMultiAlternatives(subject, strip_tags(body))
    mail.from_email = from_email
    mail.to = to
    mail.mixed_subtype = 'related'
    mail.attach_alternative(body, 'text/html')
    _attach_images(mail, images)
    if attachment:
        # TODO: type always text/csv
        with open(attachment, 'rb') as f:
            mail.attach(attachment.split('/')[-1], f.read(), 'text/csv')
    return mail


def _attach_images(mail, filenames):
    for filename in filenames:
        mime_image = _to_mime_image(filename)
        mail.attach(mime_image)
    return mail


def _to_mime_image(filename):
    path = settings.EMAIL_STATIC_PATH / 'img' / filename
    with open(path, 'rb') as image:
        mime_image = MIMEImage(image.read())
        mime_image.add_header('Content-ID', f'<{filename}>')
    return mime_image


class BaseEmail:
    """
    Base class for a predefined email.
    You have to define 'subject', 'template' and 'images' properties in a subclass
    """
    images = ()

    @classmethod
    def get_context(cls):
        initial_context = {
            'base_url': get_absolute_url(),
            'INVEST_ENABLED': settings.INVEST_ENABLED,
        }
        return initial_context

    @classmethod
    def _send(cls, to_user, context, attachment=None):
        is_sent = send_mail.delay(
            to=to_user.email, subject=cls.subject, template=cls.template, context=context,
            images=cls.images, attachment=attachment,
        )
        return is_sent

    @classmethod
    def send(cls, to_user):
        """
        Redefine this method in a subclass and pass here all the needed objects
        to form the context for cls._send() method
        """
        context = cls.get_context()
        return cls._send(to_user, context)


class EmailToAdmin(BaseEmail):
    """
    Base class for an email to be sent to administration
    """
    @classmethod
    def send(cls, context=None):
        context = context or {}
        sender = context.get('email')
        name = context.get('full_name')
        body = f'[{cls.subject}]<br>' + render_to_string(cls.template, context).strip()
        # email will not be sent. only create message in intercom
        tasks.send_to_intercom.delay(sender, name, body)
