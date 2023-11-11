from django.utils import timezone

from account.models import RestorePasswordCheck
from common.constants import FRONTEND_URLS
from common.emails import BaseEmail
from common.utils import generate_random_hex_str, get_absolute_url


class RegistrationVerifyAddressEmail(BaseEmail):
    subject = 'Verify Your Email Address'
    template = 'account/email_registration_verify_address.html'

    @classmethod
    def send(cls, to_user):
        context = cls.get_context()

        email_address = to_user.email_address
        context['verification_url'] = email_address.get_frontend_verification_url()

        email_address.sent_at = timezone.now()
        email_address.save()
        return super()._send(to_user, context)


class PasswordResetRequestedEmail(BaseEmail):
    subject = 'Password Reset Requested'
    template = 'account/email_password_reset_requested.html'

    @classmethod
    def send(cls, to_user):
        context = cls.get_context()

        restore_check = RestorePasswordCheck(
            email=to_user.email, restore_code=generate_random_hex_str(),
        )
        restore_check.save()

        url = FRONTEND_URLS.restore_password.format(restore_code=restore_check.restore_code)
        context['password_reset_url'] = get_absolute_url(url)
        context['name'] = to_user.get_full_name()
        return super()._send(to_user, context)


class PasswordSetRequestedEmail(PasswordResetRequestedEmail):
    subject = 'Set Password To Complete Your Account'
    template = 'account/email_password_set.html'


class PasswordResetSuccessfullyEmail(BaseEmail):
    subject = 'Password Reset Successfully'
    template = 'account/email_password_reset_successfully.html'


class PasswordChangedEmail(PasswordResetSuccessfullyEmail):
    subject = 'Password Changed Successfully'
