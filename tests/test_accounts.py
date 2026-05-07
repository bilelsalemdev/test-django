import pytest

pytestmark = pytest.mark.django_db


class TestRegistration:
    def test_register_user(self, api_client):
        data = {'email': 'new@test.com', 'password': 'securepass123'}
        response = api_client.post('/api/auth/register/', data)
        assert response.status_code == 201
        assert response.data['email'] == 'new@test.com'
        assert response.data['role'] == 'user'

    def test_register_admin(self, api_client):
        data = {'email': 'admin@new.com', 'password': 'securepass123', 'role': 'admin'}
        response = api_client.post('/api/auth/register/', data)
        assert response.status_code == 201
        assert response.data['role'] == 'admin'

    def test_register_duplicate_email(self, api_client, user):
        data = {'email': 'user@test.com', 'password': 'securepass123'}
        response = api_client.post('/api/auth/register/', data)
        assert response.status_code == 400

    def test_register_short_password(self, api_client):
        data = {'email': 'new@test.com', 'password': 'short'}
        response = api_client.post('/api/auth/register/', data)
        assert response.status_code == 400

    def test_register_missing_email(self, api_client):
        data = {'password': 'securepass123'}
        response = api_client.post('/api/auth/register/', data)
        assert response.status_code == 400


class TestLogin:
    def test_login_success(self, api_client, user):
        data = {'email': 'user@test.com', 'password': 'testpass123'}
        response = api_client.post('/api/auth/login/', data)
        assert response.status_code == 200
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert response.data['user']['email'] == 'user@test.com'
        assert response.data['user']['role'] == 'user'

    def test_login_wrong_password(self, api_client, user):
        data = {'email': 'user@test.com', 'password': 'wrongpassword'}
        response = api_client.post('/api/auth/login/', data)
        assert response.status_code == 401

    def test_login_nonexistent_user(self, api_client):
        data = {'email': 'nobody@test.com', 'password': 'testpass123'}
        response = api_client.post('/api/auth/login/', data)
        assert response.status_code == 401


class TestJWTRequired:
    def test_companies_requires_auth(self, api_client):
        response = api_client.get('/api/companies/')
        assert response.status_code == 401

    def test_clients_requires_auth(self, api_client):
        response = api_client.get('/api/clients/')
        assert response.status_code == 401

    def test_approvals_requires_auth(self, api_client):
        response = api_client.get('/api/approvals/')
        assert response.status_code == 401

    def test_jwt_login_flow(self, api_client, user):
        login = api_client.post('/api/auth/login/', {'email': 'user@test.com', 'password': 'testpass123'})
        token = login.data['access']
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = api_client.get('/api/companies/')
        assert response.status_code == 400

    def test_token_refresh(self, api_client, user):
        login = api_client.post('/api/auth/login/', {'email': 'user@test.com', 'password': 'testpass123'})
        refresh = login.data['refresh']
        response = api_client.post('/api/auth/token/refresh/', {'refresh': refresh})
        assert response.status_code == 200
        assert 'access' in response.data
