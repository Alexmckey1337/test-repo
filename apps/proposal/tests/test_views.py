import pytest
from django.conf import settings
from django.urls import reverse
from rest_framework import status, permissions

from apps.proposal.api.views import CreateProposalView


@pytest.mark.django_db
class TestUserViewSet:
    @pytest.mark.parametrize(
        'del_field',
        ('first_name', 'last_name', 'sex', 'born_date', 'locality', 'email', 'phone_number', 'type')
    )
    def test_create_proposal_without_one_field(self, monkeypatch, api_client, city_factory, del_field):
        monkeypatch.setattr(CreateProposalView, 'permission_classes', (permissions.AllowAny,))
        url = reverse('proposal-create')

        data = {
            'first_name': 'test_first',
            'last_name': 'test_last',
            'sex': "male",
            'born_date': '2000-01-01',
            'locality': city_factory().pk,
            'email': 'a@a.com',
            'phone_number': '+44',
            'type': 'short'
        }
        data.pop(del_field, None)
        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_201_CREATED

    def test_create_proposal_without_fields(self, monkeypatch, api_client):
        monkeypatch.setattr(CreateProposalView, 'permission_classes', (permissions.AllowAny,))
        url = reverse('proposal-create')

        data = {}
        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_201_CREATED

    def test_create_proposal_without_token_access(self, api_client):
        url = reverse('proposal-create')

        data = {}
        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_proposal_with_token_access(self, api_client):
        url = reverse('proposal-create')

        data = {}
        response = api_client.post(url, data=data, format='json', **{
            settings.VO_ORG_UA_TOKEN_NAME: settings.VO_ORG_UA_TOKEN
        })

        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.parametrize(
        'in_value,db_value', (
                ('male', 'male'),
                ('female', 'female'),
                ('unknown', 'unknown'),
                ('man', 'unknown'),
                ('woman', 'unknown'),
                ('iamdont', 'unknown'),
                ('aaaa', 'unknown'),
                ('other', 'unknown'),
        )
    )
    def test_create_proposal_with_different_sex_values(self, monkeypatch, api_client, in_value, db_value):
        monkeypatch.setattr(CreateProposalView, 'permission_classes', (permissions.AllowAny,))
        url = reverse('proposal-create')

        data = {'sex': in_value}
        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data.get('sex') == db_value

    @pytest.mark.parametrize(
        'in_value,db_value', (
                ('short', 'short'),
                ('full', 'full'),
                ('other', 'other'),
                ('unknown', 'other'),
                ('cool', 'other'),
                ('big', 'other'),
                ('small', 'other'),
                ('iamdont', 'other'),
                ('aaaa', 'other'),
        )
    )
    def test_create_proposal_with_different_type_values(self, monkeypatch, api_client, in_value, db_value):
        monkeypatch.setattr(CreateProposalView, 'permission_classes', (permissions.AllowAny,))
        url = reverse('proposal-create')

        data = {'type': in_value}
        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data.get('type') == db_value
