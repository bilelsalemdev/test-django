import pytest

pytestmark = pytest.mark.django_db

class TestRegistration:
    def test_register_user(self, api_client):
        data = {'email': 'bilel.salem@polytechnicien.tn', 'first_name': 'Bilel', 'last_name': 'Salem', 'password': 'AZEwxc1234@'}
        response = api_client.post('/api/auth/register/', data)
        assert response.status_code == 201
        assert response.data['email'] == 'bilel.salem@polytechnicien.tn'
        assert response.data['first_name'] == 'Bilel'
        assert response.data['last_name'] == 'Salem'
        assert response.data['role'] == 'user'

    def test_register_admin(self, api_client):
        data = {'email': 'admin@polytechnicien.tn', 'first_name': 'Bilel', 'last_name': 'Salem', 'password': 'AZEwxc1234@', 'role': 'admin'}
        response = api_client.post('/api/auth/register/', data)
        assert response.status_code == 201
        assert response.data['role'] == 'admin'

    def test_register_duplicate_email(self, api_client, user):
        data = {'email': 'bilelsalem2019@gmail.com', 'first_name': 'Bilel', 'last_name': 'Salem', 'password': 'AZEwxc1234@'}
        response = api_client.post('/api/auth/register/', data)
        assert response.status_code == 400

    def test_register_short_password(self, api_client):
        data = {'email': 'bilel.salem@polytechnicien.tn', 'first_name': 'Bilel', 'last_name': 'Salem', 'password': 'short'}
        response = api_client.post('/api/auth/register/', data)
        assert response.status_code == 400

    def test_register_common_password(self, api_client):
        data = {'email': 'bilel.salem@polytechnicien.tn', 'first_name': 'Bilel', 'last_name': 'Salem', 'password': 'password123'}
        response = api_client.post('/api/auth/register/', data)
        assert response.status_code == 400

    def test_register_numeric_password(self, api_client):
        data = {'email': 'bilel.salem@polytechnicien.tn', 'first_name': 'Bilel', 'last_name': 'Salem', 'password': '12345678'}
        response = api_client.post('/api/auth/register/', data)
        assert response.status_code == 400

    def test_register_missing_fields(self, api_client):
        data = {'password': 'AZEwxc1234@'}
        response = api_client.post('/api/auth/register/', data)
        assert response.status_code == 400

    def test_register_blank_first_name(self, api_client):
        data = {'email': 'bilel.salem@polytechnicien.tn', 'first_name': '  ', 'last_name': 'Salem', 'password': 'AZEwxc1234@'}
        response = api_client.post('/api/auth/register/', data)
        assert response.status_code == 400

    def test_register_invalid_name_chars(self, api_client):
        data = {'email': 'bilel.salem@polytechnicien.tn', 'first_name': 'Bilel123', 'last_name': 'Salem', 'password': 'AZEwxc1234@'}
        response = api_client.post('/api/auth/register/', data)
        assert response.status_code == 400

    def test_register_email_normalized(self, api_client):
        data = {'email': 'Bilel.Salem@Polytechnicien.TN', 'first_name': 'Bilel', 'last_name': 'Salem', 'password': 'AZEwxc1234@'}
        response = api_client.post('/api/auth/register/', data)
        assert response.status_code == 201
        assert response.data['email'] == 'bilel.salem@polytechnicien.tn'

class TestLogin:
    def test_login_success(self, api_client, user):
        data = {'email': 'bilelsalem2019@gmail.com', 'password': 'AZEwxc1234@'}
        response = api_client.post('/api/auth/login/', data)
        assert response.status_code == 200
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert response.data['user']['email'] == 'bilelsalem2019@gmail.com'
        assert response.data['user']['first_name'] == 'Bilel'
        assert response.data['user']['role'] == 'user'

    def test_login_wrong_password(self, api_client, user):
        data = {'email': 'bilelsalem2019@gmail.com', 'password': 'wrongpassword'}
        response = api_client.post('/api/auth/login/', data)
        assert response.status_code == 401

    def test_login_nonexistent_user(self, api_client):
        data = {'email': 'nobody@gmail.com', 'password': 'AZEwxc1234@'}
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
        login = api_client.post('/api/auth/login/', {'email': 'bilelsalem2019@gmail.com', 'password': 'AZEwxc1234@'})
        token = login.data['access']
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = api_client.get('/api/companies/')
        assert response.status_code == 400

    def test_token_refresh(self, api_client, user):
        login = api_client.post('/api/auth/login/', {'email': 'bilelsalem2019@gmail.com', 'password': 'AZEwxc1234@'})
        refresh = login.data['refresh']
        response = api_client.post('/api/auth/token/refresh/', {'refresh': refresh})
        assert response.status_code == 200
        assert 'access' in response.data
