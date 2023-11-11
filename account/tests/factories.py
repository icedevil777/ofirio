from django.contrib.auth import get_user_model

from common.tests.base import run_commit_hooks
from common.utils import generate_random_hex_str


User = get_user_model()


def create_user(data=None):
    random_str = generate_random_hex_str()
    user_data = {
        'email': f'test+{random_str}@ofirio.com',
        'password': 'qWe123$',
    }
    user_data.update(data or {})
    user = User.objects.create_user(**user_data)
    run_commit_hooks()
    return user
