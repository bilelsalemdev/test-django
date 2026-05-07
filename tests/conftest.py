import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email='bilelsalem2019@gmail.com', first_name='Bilel', last_name='Salem', password='AZEwxc1234@',
    )


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(
        email='bilelsalemdev@gmail.com', first_name='Bilel', last_name='Salem', password='AZEwxc1234@', role='admin',
    )


@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def admin_client(admin_user):
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client


@pytest.fixture(autouse=True)
def _clear_cache():
    from django.core.cache import cache
    cache.clear()
    yield
    cache.clear()
