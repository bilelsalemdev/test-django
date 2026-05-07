import uuid

import pytest

from apps.approvals.models import Approval

pytestmark = pytest.mark.django_db


@pytest.fixture
def company(auth_client):
    data = {
        'name': 'Salem Consulting',
        'type': 'startup',
        'funding_stage': 'Seed',
        'founded_year': 2023,
    }
    response = auth_client.post('/api/companies/', data, format='json')
    return response.data['data']


CLIENT_DATA = {
    'first_name': 'Bilel',
    'last_name': 'Salem',
    'email': 'bilel.salem@polytechnicien.tn',
    'phone': '+21628206707',
}


class TestCreateClient:
    def test_create_client(self, auth_client, company):
        data = {**CLIENT_DATA, 'company': company['id']}
        response = auth_client.post('/api/clients/', data, format='json')
        assert response.status_code == 201
        assert response.data['data']['first_name'] == 'Bilel'
        assert response.data['data']['email'] == 'bilel.salem@polytechnicien.tn'
        assert response.data['approval']['status'] == 'pending'

    def test_approval_auto_created(self, auth_client, company):
        data = {**CLIENT_DATA, 'company': company['id']}
        auth_client.post('/api/clients/', data, format='json')
        assert Approval.objects.count() == 2

    def test_duplicate_email(self, auth_client, company):
        data = {**CLIENT_DATA, 'company': company['id']}
        auth_client.post('/api/clients/', data, format='json')
        response = auth_client.post('/api/clients/', data, format='json')
        assert response.status_code == 400

    def test_missing_required_fields(self, auth_client, company):
        data = {'company': company['id']}
        response = auth_client.post('/api/clients/', data, format='json')
        assert response.status_code == 400

    def test_invalid_company(self, auth_client):
        data = {**CLIENT_DATA, 'company': str(uuid.uuid4())}
        response = auth_client.post('/api/clients/', data, format='json')
        assert response.status_code == 400

    def test_blank_first_name(self, auth_client, company):
        data = {**CLIENT_DATA, 'first_name': '  ', 'company': company['id']}
        response = auth_client.post('/api/clients/', data, format='json')
        assert response.status_code == 400

    def test_invalid_name_chars(self, auth_client, company):
        data = {**CLIENT_DATA, 'first_name': 'Bilel@123', 'company': company['id']}
        response = auth_client.post('/api/clients/', data, format='json')
        assert response.status_code == 400

    def test_invalid_phone(self, auth_client, company):
        data = {**CLIENT_DATA, 'phone': 'not-a-phone', 'company': company['id']}
        response = auth_client.post('/api/clients/', data, format='json')
        assert response.status_code == 400

    def test_email_normalized(self, auth_client, company):
        data = {**CLIENT_DATA, 'email': 'Bilel.Salem@Polytechnicien.TN', 'company': company['id']}
        response = auth_client.post('/api/clients/', data, format='json')
        assert response.status_code == 201
        assert response.data['data']['email'] == 'bilel.salem@polytechnicien.tn'


class TestListClients:
    def test_list_clients(self, auth_client, company):
        data = {**CLIENT_DATA, 'company': company['id']}
        auth_client.post('/api/clients/', data, format='json')
        response = auth_client.get('/api/clients/')
        assert response.status_code == 200
        assert len(response.data['results']) == 1
        assert 'data' in response.data['results'][0]
        assert 'approval' in response.data['results'][0]

    def test_list_empty_raises_validation_error(self, auth_client):
        response = auth_client.get('/api/clients/')
        assert response.status_code == 400


class TestRetrieveClient:
    def test_retrieve(self, auth_client, company):
        data = {**CLIENT_DATA, 'company': company['id']}
        create_resp = auth_client.post('/api/clients/', data, format='json')
        client_id = create_resp.data['data']['id']
        response = auth_client.get(f'/api/clients/{client_id}/')
        assert response.status_code == 200
        assert response.data['data']['id'] == client_id

    def test_retrieve_not_found(self, auth_client):
        response = auth_client.get(f'/api/clients/{uuid.uuid4()}/')
        assert response.status_code == 404


class TestClientCache:
    def test_cache_populated(self, auth_client, company):
        from django.core.cache import cache

        data = {**CLIENT_DATA, 'company': company['id']}
        auth_client.post('/api/clients/', data, format='json')
        cache.clear()
        auth_client.get('/api/clients/')
        assert cache.get('clients_list') is not None

    def test_cache_invalidated_on_create(self, auth_client, company):
        from django.core.cache import cache

        data = {**CLIENT_DATA, 'company': company['id']}
        auth_client.post('/api/clients/', data, format='json')
        auth_client.get('/api/clients/')
        assert cache.get('clients_list') is not None

        data2 = {**CLIENT_DATA, 'email': 'salem.bilel@company.tn', 'company': company['id']}
        auth_client.post('/api/clients/', data2, format='json')
        assert cache.get('clients_list') is None
