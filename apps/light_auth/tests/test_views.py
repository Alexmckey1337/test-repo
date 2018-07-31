from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status, permissions

from apps.light_auth import app_settings
from apps.light_auth.api.views import LightAuthCreateView, LightAuthConfirmPhoneNumberView, VerifyPhoneView, \
    ResetPasswordView, LightLoginView, CheckLightTokenView
from apps.light_auth.models import PhoneNumber, PhoneConfirmation, LightToken
import apps.light_auth.utils


@pytest.mark.django_db
class TestLightAuthCreateView:
    url_pattern = 'light_auth:create'

    def test_user_does_not_exist(self, monkeypatch, api_client):
        monkeypatch.setattr(LightAuthCreateView, 'permission_classes', (permissions.AllowAny,))
        url = reverse(self.url_pattern, kwargs={'pk': 22222222})

        data = {}

        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_user_has_light_auth_account(self, monkeypatch, api_client, light_auth_user_factory):
        monkeypatch.setattr(LightAuthCreateView, 'permission_classes', (permissions.AllowAny,))
        light_user = light_auth_user_factory()
        url = reverse(self.url_pattern, kwargs={'pk': light_user.user.pk})

        data = {}

        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_user_dont_have_phone(self, monkeypatch, api_client, user_factory):
        monkeypatch.setattr(LightAuthCreateView, 'permission_classes', (permissions.AllowAny,))
        user = user_factory(phone_number='')
        url = reverse(self.url_pattern, kwargs={'pk': user.pk})

        data = {}

        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_phone_number_already_exist(self, monkeypatch, api_client, user_factory, phone_number_factory):
        monkeypatch.setattr(LightAuthCreateView, 'permission_classes', (permissions.AllowAny,))
        phone = '+380668886644'
        phone_number_factory(phone=phone)
        user = user_factory(phone_number=phone)
        url = reverse(self.url_pattern, kwargs={'pk': user.pk})

        data = {}

        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_successful(self, monkeypatch, api_client, user_factory):
        monkeypatch.setattr(LightAuthCreateView, 'permission_classes', (permissions.AllowAny,))
        monkeypatch.setattr(apps.light_auth.utils, 'send_sms', lambda t,p,c: 0)
        phone = '+380996664466'
        user = user_factory(phone_number=phone)
        url = reverse(self.url_pattern, kwargs={'pk': user.pk})

        data = {}

        assert PhoneNumber.objects.filter(phone=phone).count() == 0

        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert PhoneNumber.objects.filter(phone=phone).count() == 1
        assert PhoneConfirmation.objects.filter(phone_number__phone=phone).count() == 1
        phone_number = PhoneNumber.objects.get(phone=phone)
        assert phone_number.primary
        assert not phone_number.verified
        confirmation = PhoneConfirmation.objects.get(phone_number__phone=phone)
        assert confirmation.sent is not None


@pytest.mark.django_db
class TestLightAuthConfirmPhoneNumberView:
    url_pattern = 'light_auth:send_confirm'

    def test_user_does_not_exist(self, monkeypatch, api_client):
        monkeypatch.setattr(LightAuthConfirmPhoneNumberView, 'permission_classes', (permissions.AllowAny,))
        url = reverse(self.url_pattern, kwargs={'pk': 22222222})

        data = {}

        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_light_user_does_not_exist(self, monkeypatch, api_client, user_factory):
        monkeypatch.setattr(LightAuthConfirmPhoneNumberView, 'permission_classes', (permissions.AllowAny,))
        user = user_factory()
        url = reverse(self.url_pattern, kwargs={'pk': user.pk})

        data = {}

        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_user_dont_have_phone_number(self, monkeypatch, api_client, light_auth_user_factory):
        monkeypatch.setattr(LightAuthConfirmPhoneNumberView, 'permission_classes', (permissions.AllowAny,))
        light_user = light_auth_user_factory(user__phone_number='')
        url = reverse(self.url_pattern, kwargs={'pk': light_user.user_id})

        data = {}

        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_light_user_with_phone_already_exist(self, monkeypatch, api_client, phone_number_factory,
                                                 light_auth_user_factory):
        monkeypatch.setattr(LightAuthConfirmPhoneNumberView, 'permission_classes', (permissions.AllowAny,))
        phone = '+380667775533'
        phone_number_factory(phone=phone)
        light_user = light_auth_user_factory(user__phone_number=phone)
        url = reverse(self.url_pattern, kwargs={'pk': light_user.user_id})

        data = {}

        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_successful_without_phone(self, monkeypatch, api_client, light_auth_user_factory):
        monkeypatch.setattr(LightAuthConfirmPhoneNumberView, 'permission_classes', (permissions.AllowAny,))
        monkeypatch.setattr(apps.light_auth.utils, 'send_sms', lambda t,p,c: 0)
        phone = '+380667775533'
        light_user = light_auth_user_factory(user__phone_number=phone)
        url = reverse(self.url_pattern, kwargs={'pk': light_user.user_id})

        data = {}

        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_200_OK

    def test_successful_with_phone(self, monkeypatch, api_client, phone_number_factory):
        monkeypatch.setattr(LightAuthConfirmPhoneNumberView, 'permission_classes', (permissions.AllowAny,))
        phone = '+380667775533'
        light_user = phone_number_factory(auth_user__user__phone_number=phone, phone=phone).auth_user
        url = reverse(self.url_pattern, kwargs={'pk': light_user.user_id})

        data = {}

        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestVerifyPhoneView:
    url_pattern = 'light_auth:verify_phone'

    def test_have_perm(self, settings, api_client):
        url = reverse(self.url_pattern)

        data = {}
        response = api_client.post(url, data=data, format='json', **{
            settings.VO_ORG_UA_TOKEN_NAME: settings.VO_ORG_UA_TOKEN
        })

        assert response.status_code != status.HTTP_403_FORBIDDEN

    def test_dont_have_perm(self, api_client):
        url = reverse(self.url_pattern)

        data = {}
        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_invalid_phone(self, monkeypatch, api_client):
        monkeypatch.setattr(VerifyPhoneView, 'permission_classes', (permissions.AllowAny,))
        url = reverse(self.url_pattern)

        data = {'phone_number': "+38099", 'key': '12345678'}

        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_invalid_password(self, monkeypatch, api_client):
        monkeypatch.setattr(VerifyPhoneView, 'permission_classes', (permissions.AllowAny,))
        url = reverse(self.url_pattern)

        data = {'phone_number': "+380990004422", 'key': '12345678', 'new_password': '111'}

        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.parametrize('field', ['phone_number', 'key'])
    def test_without_required_data(self, monkeypatch, api_client, field):
        monkeypatch.setattr(VerifyPhoneView, 'permission_classes', (permissions.AllowAny,))
        url = reverse(self.url_pattern)

        data = {'phone_number': "+380990004422", 'key': '12345678'}
        data.pop(field, None)

        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_key_does_not_exist(self, monkeypatch, api_client, phone_confirmation_factory):
        monkeypatch.setattr(VerifyPhoneView, 'permission_classes', (permissions.AllowAny,))
        url = reverse(self.url_pattern)
        phone = "+380990004422"
        key = '12345678'
        sent = timezone.now()
        phone_confirmation_factory(
            phone_number__phone=phone,
            sent=sent,
            key=key)

        data = {'phone_number': phone, 'key': key + '9'}

        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_phone_does_not_exist(self, monkeypatch, api_client, phone_confirmation_factory):
        monkeypatch.setattr(VerifyPhoneView, 'permission_classes', (permissions.AllowAny,))
        url = reverse(self.url_pattern)
        phone = "+380990004422"
        key = '12345678'
        sent = timezone.now()
        phone_confirmation_factory(
            phone_number__phone=phone,
            sent=sent,
            key=key)

        data = {'phone_number': phone + '9', 'key': key}

        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_exprired_key(self, monkeypatch, api_client, phone_confirmation_factory):
        monkeypatch.setattr(VerifyPhoneView, 'permission_classes', (permissions.AllowAny,))
        url = reverse(self.url_pattern)
        phone = "+380990004422"
        key = '12345678'
        sent = timezone.now() - timedelta(days=app_settings.EMAIL_CONFIRMATION_EXPIRE_DAYS + 1)
        phone_confirmation_factory(
            phone_number__phone=phone,
            sent=sent,
            key=key)

        data = {'phone_number': phone, 'key': key}

        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_successful(self, monkeypatch, api_client, phone_confirmation_factory):
        monkeypatch.setattr(VerifyPhoneView, 'permission_classes', (permissions.AllowAny,))
        url = reverse(self.url_pattern)
        phone = "+380990004422"
        key = '12345678'
        sent = timezone.now()
        phone_confirmation_factory(
            phone_number__phone=phone,
            sent=sent,
            key=key)

        data = {'phone_number': phone, 'key': key}

        phone_number = PhoneNumber.objects.get(phone=phone)
        assert not phone_number.primary
        assert not phone_number.verified

        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_200_OK

        phone_number = PhoneNumber.objects.get(phone=phone)
        assert phone_number.primary
        assert phone_number.verified

    def test_successful_charge_password(self, monkeypatch, api_client, phone_confirmation_factory):
        monkeypatch.setattr(VerifyPhoneView, 'permission_classes', (permissions.AllowAny,))
        url = reverse(self.url_pattern)
        phone = "+380990004422"
        key = '12345678'
        old_password = 'myo1dpaSSworD'
        new_password = 'mynEwpa$SworD'
        sent = timezone.now()
        phone_confirmation_factory(
            phone_number__phone=phone,
            sent=sent,
            key=key)

        data = {'phone_number': phone, 'key': key, 'new_password': new_password}

        phone_number = PhoneNumber.objects.get(phone=phone)
        assert not phone_number.primary
        assert not phone_number.verified
        light_user = phone_number.auth_user
        light_user.set_password(old_password)
        light_user.save()
        assert light_user.check_password(old_password)
        assert not light_user.check_password(new_password)

        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_200_OK

        phone_number = PhoneNumber.objects.get(phone=phone)
        assert phone_number.primary
        assert phone_number.verified
        light_user = phone_number.auth_user
        assert not light_user.check_password(old_password)
        assert light_user.check_password(new_password)


@pytest.mark.django_db
class TestResetPasswordView:
    url_pattern = 'light_auth:reset_password'

    def test_have_perm(self, settings, api_client):
        url = reverse(self.url_pattern)

        data = {}
        response = api_client.post(url, data=data, format='json', **{
            settings.VO_ORG_UA_TOKEN_NAME: settings.VO_ORG_UA_TOKEN
        })

        assert response.status_code != status.HTTP_403_FORBIDDEN

    def test_dont_have_perm(self, api_client):
        url = reverse(self.url_pattern)

        data = {}
        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_invalid_phone(self, monkeypatch, api_client):
        monkeypatch.setattr(ResetPasswordView, 'permission_classes', (permissions.AllowAny,))
        url = reverse(self.url_pattern)

        data = {'phone_number': "+38099"}

        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_phone_not_primary(self, monkeypatch, api_client, phone_number_factory):
        monkeypatch.setattr(ResetPasswordView, 'permission_classes', (permissions.AllowAny,))
        url = reverse(self.url_pattern)

        phone_number = '+380996664466'
        phone_number_factory(phone=phone_number, primary=False, verified=True)

        data = {'phone_number': phone_number}

        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_phone_not_verified(self, monkeypatch, api_client, phone_number_factory):
        monkeypatch.setattr(ResetPasswordView, 'permission_classes', (permissions.AllowAny,))
        url = reverse(self.url_pattern)

        phone_number = '+380996664466'
        phone_number_factory(phone=phone_number, primary=True, verified=False)

        data = {'phone_number': phone_number}

        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_phone_not_exist(self, monkeypatch, api_client, phone_number_factory):
        monkeypatch.setattr(ResetPasswordView, 'permission_classes', (permissions.AllowAny,))
        url = reverse(self.url_pattern)

        phone_number = '+380996664466'
        phone_number_factory(phone=phone_number + '4', primary=True, verified=True)

        data = {'phone_number': phone_number}

        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_successful(self, monkeypatch, api_client, phone_number_factory):
        monkeypatch.setattr(ResetPasswordView, 'permission_classes', (permissions.AllowAny,))
        monkeypatch.setattr(apps.light_auth.utils, 'send_sms', lambda t,p,c: 0)
        url = reverse(self.url_pattern)

        phone_number = '+380996664466'
        phone_number_factory(phone=phone_number, primary=True, verified=True)

        data = {'phone_number': phone_number}

        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestLightLoginView:
    url_pattern = 'light_auth:login'

    def test_have_perm(self, settings, api_client):
        url = reverse(self.url_pattern)

        data = {}
        response = api_client.post(url, data=data, format='json', **{
            settings.VO_ORG_UA_TOKEN_NAME: settings.VO_ORG_UA_TOKEN
        })

        assert response.status_code != status.HTTP_403_FORBIDDEN

    def test_dont_have_perm(self, api_client):
        url = reverse(self.url_pattern)

        data = {}
        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_invalid_phone(self, monkeypatch, api_client):
        monkeypatch.setattr(LightLoginView, 'permission_classes', (permissions.AllowAny,))
        url = reverse(self.url_pattern)

        data = {'phone_number': "+38099", "password": "VerYhaRd"}

        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.xfail
    def test_phone_not_primary(self, monkeypatch, api_client, phone_number_factory):
        monkeypatch.setattr(LightLoginView, 'permission_classes', (permissions.AllowAny,))
        url = reverse(self.url_pattern)

        phone_number = '+380996664466'
        password = 'VerYhaRd'
        phone = phone_number_factory(phone=phone_number, primary=False, verified=True)
        user = phone.auth_user
        user.set_password(password)
        user.save()

        data = {'phone_number': phone_number, "password": password}

        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.xfail
    def test_phone_not_verified(self, monkeypatch, api_client, phone_number_factory):
        monkeypatch.setattr(LightLoginView, 'permission_classes', (permissions.AllowAny,))
        url = reverse(self.url_pattern)

        phone_number = '+380996664466'
        password = 'VerYhaRd'
        phone = phone_number_factory(phone=phone_number, primary=True, verified=False)
        user = phone.auth_user
        user.set_password(password)
        user.save()

        data = {'phone_number': phone_number, "password": password}

        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_phone_not_exist(self, monkeypatch, api_client, phone_number_factory):
        monkeypatch.setattr(LightLoginView, 'permission_classes', (permissions.AllowAny,))
        url = reverse(self.url_pattern)

        phone_number = '+380996664466'
        password = 'VerYhaRd'
        phone = phone_number_factory(phone=phone_number+'4', primary=True, verified=True)
        user = phone.auth_user
        user.set_password(password)
        user.save()

        data = {'phone_number': phone_number, "password": password}

        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_user_not_active(self, monkeypatch, api_client, phone_number_factory):
        monkeypatch.setattr(LightLoginView, 'permission_classes', (permissions.AllowAny,))
        url = reverse(self.url_pattern)

        phone_number = '+380996664466'
        password = 'VerYhaRd'
        phone = phone_number_factory(phone=phone_number, primary=True, verified=True)
        user = phone.auth_user
        user.set_password(password)
        user.is_active = False
        user.save()

        data = {'phone_number': phone_number, "password": password}

        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.xfail
    def test_password_invalid(self, monkeypatch, api_client, phone_number_factory):
        monkeypatch.setattr(LightLoginView, 'permission_classes', (permissions.AllowAny,))
        url = reverse(self.url_pattern)

        phone_number = '+380996664466'
        password = 'VerYhaRd'
        phone = phone_number_factory(phone=phone_number+'4', primary=True, verified=True)
        user = phone.auth_user
        user.set_password(password)
        user.save()

        data = {'phone_number': phone_number, "password": password + 'bad'}

        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.xfail
    def test_successful(self, monkeypatch, api_client, phone_number_factory):
        monkeypatch.setattr(LightLoginView, 'permission_classes', (permissions.AllowAny,))
        url = reverse(self.url_pattern)

        fields = (
            'key',
            'id',
            'first_name', 'last_name', 'middle_name',
            'image',
            'phone_number', 'extra_phone_numbers', 'email',
            'locality', 'address',
            'church', 'home_group',
            'master', 'repentance_date', 'hierarchy',
            'language',
        )

        phone_number = '+380996664466'
        password = 'VerYhaRd'
        phone = phone_number_factory(phone=phone_number, primary=True, verified=True)
        user = phone.auth_user
        user.set_password(password)
        user.save()

        data = {'phone_number': phone_number, "password": password}

        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_200_OK
        for f in fields:
            assert f in response.data
        assert LightToken.objects.filter(key=response.data['key'], user=user)

    # TODO delete it
    def test_very_bad_successful(self, monkeypatch, api_client, phone_number_factory):
        monkeypatch.setattr(LightLoginView, 'permission_classes', (permissions.AllowAny,))
        url = reverse(self.url_pattern)

        fields = (
            'key',
            'id',
            'first_name', 'last_name', 'middle_name',
            'image',
            'phone_number', 'extra_phone_numbers', 'email',
            'locality', 'address',
            'church', 'home_group',
            'master', 'repentance_date', 'hierarchy',
            'language',
        )

        phone_number = '+380996664466'
        phone = phone_number_factory(phone=phone_number, primary=True, verified=True)
        user = phone.auth_user
        confirm1 = PhoneConfirmation.create(phone_number=phone)
        confirm2 = PhoneConfirmation.create(phone_number=phone)

        data = {'phone_number': phone_number, "password": confirm1.key}
        response = api_client.post(url, data=data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        data = {'phone_number': phone_number, "password": confirm2.key}
        response = api_client.post(url, data=data, format='json')
        assert response.status_code == status.HTTP_200_OK

        for f in fields:
            assert f in response.data
        assert LightToken.objects.filter(key=response.data['key'], user=user)


@pytest.mark.django_db
class TestCheckTokenView:
    url_pattern = 'light_auth:check_key'

    def test_invalid_key(self, monkeypatch, api_client):
        monkeypatch.setattr(CheckLightTokenView, 'permission_classes', (permissions.AllowAny,))
        url = reverse(self.url_pattern)
        key = 'invalidkey'

        data = {
            'key': key
        }

        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data.get('code') == 'invalid_key'

    def test_successful_with_phone(self, monkeypatch, api_client, phone_number_factory):
        monkeypatch.setattr(CheckLightTokenView, 'permission_classes', (permissions.AllowAny,))
        url = reverse(self.url_pattern)
        phone = '+380994442244'
        phone_number = phone_number_factory(phone=phone, verified=True, primary=True)
        token = LightToken.objects.create(user=phone_number.auth_user)

        data = {
            'key': token.key
        }

        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data.get('phone_number') == phone

    def test_successful_without_phone(self, monkeypatch, api_client, light_auth_user_factory):
        monkeypatch.setattr(CheckLightTokenView, 'permission_classes', (permissions.AllowAny,))
        url = reverse(self.url_pattern)
        auth_user = light_auth_user_factory()
        token = LightToken.objects.create(user=auth_user)

        data = {
            'key': token.key
        }

        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data.get('phone_number') == ''
