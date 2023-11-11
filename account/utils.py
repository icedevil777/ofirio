import re

from django.conf import settings
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError

from account.enums import UserAccessStatus


def get_access_status(user):
    """
    Calculate user access status
    """
    if user.is_authenticated:

        if user.verified:
            return UserAccessStatus.PREMIUM
        else:
            return UserAccessStatus.UNVERIFIED

    else:
        return UserAccessStatus.ANON


def is_premium(user):
    """Shortcut to check if user is Trial or Premium"""
    status = get_access_status(user)
    return status == UserAccessStatus.PREMIUM


def validate_password(raw_password, field_name='password', email=None):
    """
    Validate password and return it if everything's ok
    """
    password = raw_password.strip()
    email = str(email or '')

    # validate password by settings.AUTH_PASSWORD_VALIDATORS
    try:
        password_validation.validate_password(password)
    except (DjangoValidationError, ValidationError) as exc:
        raise ValidationError({field_name: str(exc)}) from exc

    # validate password by being only latin
    if re.fullmatch('[a-zA-Z]+', password):
        raise ValidationError({field_name: 'This password is entirely alphabetical'})

    # validate password for having atl east one letter
    if not any(char.isalpha() for char in password):
        raise ValidationError({field_name: 'Password must have at least one letter'})

    # validate password for having atl east one digit
    if not any(char.isdigit() for char in password):
        raise ValidationError({field_name: 'Password must have at least one digit'})

    # validate password by similarity to the email
    local = email.split('@')[0].strip()
    if local and (local in password or password in local):
        raise ValidationError({field_name: 'The password is too similar to the Email'})

    # validate password by side whitespace chars
    if password != raw_password:
        raise ValidationError({field_name: 'Whitespace characters are not allowed in the '
                                           'begginning and in the end of a password'})

    return password
