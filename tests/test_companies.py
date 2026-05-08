import uuid

import pytest
from django.core.cache import cache

from apps.approvals.models import Approval

pytestmark = pytest.mark.django_db

SMALL_BUSINESS = {
    'name': 'Local Shop',
    'type': 'small_business',
    'employee_count': 15,
    'industry': 'Retail',
}

STARTUP = {
    'name': 'TechStart',
    'type': 'startup',
    'funding_stage': 'Series A',
    'founded_year': 2022,
}

CORPORATE = {
    'name': 'MegaCorp',
    'type': 'corporate',
    'revenue': '5000000.00',
    'stock_symbol': 'MEGA',
}

class TestCreateCompany:
    @pytest.mark.parametrize(
        'data',
        [SMALL_BUSINESS, STARTUP, CORPORATE],
        ids=['small_business', 'startup', 'corporate'],
    )
    def test_create_all_types(self, auth_client, data):
        response = auth_client.post('/api/companies/', data, format='json')
        assert response.status_code == 201
        assert response.data['data']['name'] == data['name']
        assert response.data['data']['type'] == data['type']
        assert response.data['approval']['status'] == 'pending'

    def test_approval_auto_created(self, auth_client):
        auth_client.post('/api/companies/', SMALL_BUSINESS, format='json')
        assert Approval.objects.count() == 1
        approval = Approval.objects.first()
        assert approval.status == 'pending'

    def test_invalid_type(self, auth_client):
        data = {'name': 'Test', 'type': 'invalid_type'}
        response = auth_client.post('/api/companies/', data, format='json')
        assert response.status_code == 400

    def test_missing_type_specific_fields(self, auth_client):
        data = {'name': 'Test', 'type': 'small_business'}
        response = auth_client.post('/api/companies/', data, format='json')
        assert response.status_code == 400

    def test_missing_name(self, auth_client):
        data = {'type': 'startup', 'funding_stage': 'Seed', 'founded_year': 2023}
        response = auth_client.post('/api/companies/', data, format='json')
        assert response.status_code == 400

    def test_blank_name(self, auth_client):
        data = {'name': '  ', 'type': 'startup', 'funding_stage': 'Seed', 'founded_year': 2023}
        response = auth_client.post('/api/companies/', data, format='json')
        assert response.status_code == 400

    def test_negative_employee_count(self, auth_client):
        data = {'name': 'Shop', 'type': 'small_business', 'employee_count': -5, 'industry': 'Retail'}
        response = auth_client.post('/api/companies/', data, format='json')
        assert response.status_code == 400

    def test_invalid_founded_year(self, auth_client):
        data = {'name': 'Future', 'type': 'startup', 'funding_stage': 'Seed', 'founded_year': 3000}
        response = auth_client.post('/api/companies/', data, format='json')
        assert response.status_code == 400

    def test_negative_revenue(self, auth_client):
        data = {'name': 'Corp', 'type': 'corporate', 'revenue': '-100.00', 'stock_symbol': 'BAD'}
        response = auth_client.post('/api/companies/', data, format='json')
        assert response.status_code == 400

    def test_invalid_stock_symbol(self, auth_client):
        data = {'name': 'Corp', 'type': 'corporate', 'revenue': '1000.00', 'stock_symbol': '123'}
        response = auth_client.post('/api/companies/', data, format='json')
        assert response.status_code == 400

class TestListCompanies:
    def test_list_empty_raises_validation_error(self, auth_client):
        response = auth_client.get('/api/companies/')
        assert response.status_code == 400

    def test_list_with_data(self, auth_client):
        auth_client.post('/api/companies/', SMALL_BUSINESS, format='json')
        auth_client.post('/api/companies/', STARTUP, format='json')
        response = auth_client.get('/api/companies/')
        assert response.status_code == 200
        assert len(response.data['results']) == 2

    def test_response_format(self, auth_client):
        auth_client.post('/api/companies/', STARTUP, format='json')
        response = auth_client.get('/api/companies/')
        item = response.data['results'][0]
        assert 'data' in item
        assert 'approval' in item
        assert 'id' in item['data']
        assert 'name' in item['data']
        assert item['approval']['status'] == 'pending'

class TestRetrieveCompany:
    def test_retrieve(self, auth_client):
        create_resp = auth_client.post('/api/companies/', CORPORATE, format='json')
        company_id = create_resp.data['data']['id']
        response = auth_client.get(f'/api/companies/{company_id}/')
        assert response.status_code == 200
        assert response.data['data']['id'] == company_id
        assert response.data['data']['stock_symbol'] == 'MEGA'

    def test_retrieve_not_found(self, auth_client):
        response = auth_client.get(f'/api/companies/{uuid.uuid4()}/')
        assert response.status_code == 404

class TestCompanyCache:
    def test_cache_populated_on_list(self, auth_client):
        auth_client.post('/api/companies/', SMALL_BUSINESS, format='json')
        assert cache.get('companies_list') is None
        auth_client.get('/api/companies/')
        assert cache.get('companies_list') is not None

    def test_cache_hit_on_second_request(self, auth_client):
        auth_client.post('/api/companies/', SMALL_BUSINESS, format='json')
        resp1 = auth_client.get('/api/companies/')
        resp2 = auth_client.get('/api/companies/')
        assert resp1.data == resp2.data

    def test_cache_invalidated_on_create(self, auth_client):
        auth_client.post('/api/companies/', SMALL_BUSINESS, format='json')
        auth_client.get('/api/companies/')
        assert cache.get('companies_list') is not None
        auth_client.post('/api/companies/', STARTUP, format='json')
        assert cache.get('companies_list') is None

class TestPagination:
    def test_pagination_structure(self, auth_client):
        auth_client.post('/api/companies/', SMALL_BUSINESS, format='json')
        response = auth_client.get('/api/companies/')
        assert 'count' in response.data
        assert 'next' in response.data
        assert 'previous' in response.data
        assert 'results' in response.data

    def test_page_size(self, auth_client):
        for i in range(25):
            auth_client.post(
                '/api/companies/',
                {'name': f'Co {i}', 'type': 'startup', 'funding_stage': 'Seed', 'founded_year': 2020},
                format='json',
            )
        response = auth_client.get('/api/companies/')
        assert response.data['count'] == 25
        assert len(response.data['results']) == 20
        assert response.data['next'] is not None
