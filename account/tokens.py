from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()


class OfirioRefreshToken(RefreshToken):
    """
    Customized Refresh JWToken, to return full user info
    in access token
    """
    _user = None

    def __init__(self, token=None, verify=True):
        super().__init__(token=token, verify=verify)

        # if there is no exceptions, then the token is valid
        # and it's safe to associate it with a user
        email = self.payload.get('email')
        if email and self._user is None:
            self._user = User.objects.filter(email=email).first()

    @property
    def access_token(self):
        from account.serializers import AccountSerializer  # unfortunately
        access = super().access_token

        serializer = AccountSerializer(self._user)
        if serializer.data.get('pk'):
            for claim, value in serializer.data.items():
                if claim not in self.no_copy_claims:
                    access[claim] = value

        return access

    @classmethod
    def for_user(cls, user):
        """
        Stick User object to the token instance
        """
        token = super().for_user(user)
        token._user = user
        return token
