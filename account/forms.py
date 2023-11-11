from django import forms
from django.core.exceptions import ValidationError


class RegistrationForm(forms.Form):

    first_name = forms.CharField(
        label='First Name',
        required=True,
        max_length=100)

    last_name = forms.CharField(
        label='Last Name',
        required=True,
        max_length=100)

    email = forms.EmailField(
        label='Email',
        required=True,
        max_length=100)

    password = forms.CharField(
        label='Password',
        required=True,
        min_length=8,
        widget=forms.PasswordInput)

    password_repeat = forms.CharField(
        label='Repeat Password',
        required=True,
        min_length=8,
        widget=forms.PasswordInput)

    def validate(self):

        #super().validate()

        password = self.cleaned_data['password']
        password_repeat = self.cleaned_data['password_repeat']

        if password != password_repeat:
            raise ValidationError("Passwords don't match")


    #def clean(self):
    #
    #    cleaned_data = super().clean()
    #    password = cleaned_data.get("password")
    #    password_repeat = cleaned_data.get("password_repeat")
    #    print(cleaned_data)
    #
    #     print('password=', password)
    #    print('password_repeat=', password_repeat)
    #
    #    if password != password_repeat:
    #        raise ValidationError("Passwords don't match")
    #
    #    min_length = 8
    #    if len(password) < min_length:
    #        raise ValidationError('Password must be at least {0} characters long.').format(min_length)
    #
    #     if not any(char.isdigit() for char in password):
    #        raise ValidationError('Password must contain at least 1 digit.')
    #
    #    if not any(char.isalpha() for char in password):
    #        raise ValidationError('Password must contain at least 1 letter.')


class LoginForm(forms.Form):
    email = forms.EmailField(
        label='Email',
        required=True,
        max_length=100)

    password = forms.CharField(
        label='Password',
        required=True,
        min_length=8,
        widget=forms.PasswordInput)


class ProfileForm(forms.Form):
    first_name = forms.CharField(
        label='First Name',
        required=True,
        max_length=100)

    last_name = forms.CharField(
        label='Last Name',
        required=True,
        max_length=100)

    email = forms.EmailField(
        label='Email',
        widget=forms.TextInput(attrs={'readonly': 'readonly'}))


class ChangePasswordForm(forms.Form):
    password_old = forms.CharField(
        label='Old Password',
        required=True,
        min_length=8,
        widget=forms.PasswordInput)

    password_new = forms.CharField(
        label='New Password',
        required=True,
        min_length=8,
        widget=forms.PasswordInput)

    password_new_repeat = forms.CharField(
        label='Repeat New Password',
        required=True,
        min_length=8,
        widget=forms.PasswordInput)

    def clean(self):

        cleaned_data = super().clean()
        password_new = cleaned_data.get("password_new")
        password_new_repeat = cleaned_data.get("password_new_repeat")

        if password_new != password_new_repeat:
            raise ValidationError("New passwords don't match")

        min_length = 8
        if len(password_new) < min_length:
            raise ValidationError('New password must be at least {0} characters long.').format(min_length)

        if not any(char.isdigit() for char in password_new):
            raise ValidationError('New password must contain at least 1 digit.')


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        label='Email',
        required=True,
        max_length=100)


class NewPasswordRestoreForm(forms.Form):
    password_new = forms.CharField(
        label='New Password',
        required=True,
        min_length=8,
        widget=forms.PasswordInput)

    password_new_repeat = forms.CharField(
        label='Repeat New Password',
        required=True,
        min_length=8,
        widget=forms.PasswordInput)

    def clean(self):

        cleaned_data = super().clean()
        password_new = cleaned_data.get("password_new")
        password_new_repeat = cleaned_data.get("password_new_repeat")

        if password_new != password_new_repeat:
            raise ValidationError("New passwords don't match")

        min_length = 8
        if len(password_new) < min_length:
            raise ValidationError('New password must be at least {0} characters long.').format(min_length)

        if not any(char.isdigit() for char in password_new):
            raise ValidationError('New password must contain at least 1 digit.')
