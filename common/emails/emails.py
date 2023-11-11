from common.emails import BaseEmail, EmailToAdmin


class ContactUsEmail(EmailToAdmin):
    subject = 'Contact Us'
    template = 'common/email_contact_us.html'


class GoogleIndexEmail(BaseEmail):
    subject = 'Sent to google index'
    template = 'common/google_index.html'

    @classmethod
    def send(cls, to_user, attach):
        context = cls.get_context()

        return super()._send(to_user, context, attach)
