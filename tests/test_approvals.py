import pytest

from apps.approvals.models import Approval

pytestmark = pytest.mark.django_db


@pytest.fixture
def company_with_approval(auth_client):
    data = {
        'name': 'Salem Digital',
        'type': 'startup',
        'funding_stage': 'Seed',
        'founded_year': 2023,
    }
    response = auth_client.post('/api/companies/', data, format='json')
    return response.data


class TestListApprovals:
    def test_admin_can_list(self, admin_client, company_with_approval):
        response = admin_client.get('/api/approvals/')
        assert response.status_code == 200
        assert len(response.data['results']) == 1

    def test_user_cannot_list(self, auth_client, company_with_approval):
        response = auth_client.get('/api/approvals/')
        assert response.status_code == 403


class TestUpdateApproval:
    def test_admin_approve(self, admin_client, company_with_approval):
        approval_id = company_with_approval['approval']['id']
        response = admin_client.patch(
            f'/api/approvals/{approval_id}/',
            {'status': 'approved'},
            format='json',
        )
        assert response.status_code == 200
        assert response.data['status'] == 'approved'

    def test_admin_reject(self, admin_client, company_with_approval):
        approval_id = company_with_approval['approval']['id']
        response = admin_client.patch(
            f'/api/approvals/{approval_id}/',
            {'status': 'rejected'},
            format='json',
        )
        assert response.status_code == 200
        assert response.data['status'] == 'rejected'

    def test_user_cannot_update(self, auth_client, company_with_approval):
        approval_id = company_with_approval['approval']['id']
        response = auth_client.patch(
            f'/api/approvals/{approval_id}/',
            {'status': 'approved'},
            format='json',
        )
        assert response.status_code == 403

    def test_reviewed_by_auto_set(self, admin_client, admin_user, company_with_approval):
        approval_id = company_with_approval['approval']['id']
        admin_client.patch(
            f'/api/approvals/{approval_id}/',
            {'status': 'approved'},
            format='json',
        )
        approval = Approval.objects.get(pk=approval_id)
        assert approval.reviewed_by == admin_user

    def test_invalid_status(self, admin_client, company_with_approval):
        approval_id = company_with_approval['approval']['id']
        response = admin_client.patch(
            f'/api/approvals/{approval_id}/',
            {'status': 'invalid'},
            format='json',
        )
        assert response.status_code == 400
