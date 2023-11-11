import datetime
import warnings

from django.core.cache import CacheKeyWarning
from django.core.management.base import BaseCommand


# To disable cache key warnings
# https://docs.djangoproject.com/en/4.0/topics/cache/#cache-key-warnings
warnings.simplefilter("ignore", CacheKeyWarning)


class OfirioCommand(BaseCommand):
    """
    Base command class for our commands
    """
    def log(self, *args):
        """
        Use this method to print command messages
        """
        dt = datetime.datetime.utcnow()
        string = ' '.join([str(arg) for arg in args])
        self.stdout.write(f'{dt}: {string}')
