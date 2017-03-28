# -*- coding: utf-8
from __future__ import absolute_import, unicode_literals

import json

import pytest
from rest_framework import status

from payment.models import Payment


class Factory:
    def __init__(self, factory_name):
        self.name = factory_name


CHANGED_FIELDS = (
    # required
    ('sum', '124', True),
    ('rate', '1.246', True),
    ('object_id', Factory('deal_factory'), True),

    # don't required
    ('currency_sum', Factory('currency_factory'), False),
    ('sent_date', '4002-06-22', False),
    ('description', 'other description', False),
)


@pytest.mark.django_db
@pytest.mark.urls('payment.tests.urls')
class TestPaymentUpdateDestroyView:
    def test_delete_payment(self, rf, allow_any_payment_update_destroy_view, purpose_payment):
        request = rf.delete('/payment/{}/'.format(purpose_payment.id))
        view = allow_any_payment_update_destroy_view.as_view()
        response = view(request, pk=purpose_payment.id)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Payment.objects.filter(pk=purpose_payment.id).exists()

    @pytest.mark.parametrize(
        'method,code',
        [('delete', status.HTTP_204_NO_CONTENT), ('patch', status.HTTP_200_OK)],
        ids=['delete', 'update'])
    def test_del_or_upd_payment_when_current_user_is_manager_of_payment(
            self, api_client, user, purpose_payment, method, code):
        url = '/payment/{}/'.format(purpose_payment.id)
        purpose_payment.manager = user
        purpose_payment.save()
        api_client.force_login(user)
        response = getattr(api_client, method)(url, format='json')

        assert response.status_code == code

    @pytest.mark.parametrize(
        'method,code',
        [('delete', status.HTTP_204_NO_CONTENT), ('patch', status.HTTP_200_OK)],
        ids=['delete', 'update'])
    def test_del_or_upd_payment_when_current_user_is_partner_supervisor(
            self, api_client, supervisor_partner, purpose_payment, method, code):
        url = '/payment/{}/'.format(purpose_payment.id)
        api_client.force_login(supervisor_partner.user)
        response = getattr(api_client, method)(url, format='json')

        if purpose_payment.content_type.app_label == 'partnership':
            assert response.status_code == code
        else:
            assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize(
        'method,code',
        [('delete', status.HTTP_204_NO_CONTENT), ('patch', status.HTTP_200_OK)],
        ids=['delete', 'update'])
    def test_del_or_upd_payment_when_current_user_is_summit_supervisor(
            self, api_client, supervisor_anket, purpose_payment, method, code):
        url = '/payment/{}/'.format(purpose_payment.id)
        api_client.force_login(supervisor_anket.user)
        if purpose_payment.content_type.app_label == 'summit':
            supervisor_anket.summit = purpose_payment.purpose.summit
            supervisor_anket.save()

        response = getattr(api_client, method)(url, format='json')

        if purpose_payment.content_type.app_label == 'summit':
            assert response.status_code == code
        else:
            assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize(
        'method', ['delete', 'patch'], ids=['delete', 'update'])
    def test_del_or_upd_payment_without_permission(
            self, api_client, dont_have_permission_user, purpose_payment, method):
        url = '/payment/{}/'.format(purpose_payment.id)
        manager = dont_have_permission_user
        user = manager.user if hasattr(manager, 'user') else manager
        api_client.force_login(user)

        response = getattr(api_client, method)(url, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize(
        'method', ['delete', 'patch'], ids=['delete', 'update'])
    def test_del_or_upd_own_payment(self, api_client, purpose_payment, method):
        url = '/payment/{}/'.format(purpose_payment.id)
        user = purpose_payment.purpose.user
        api_client.force_login(user)

        response = getattr(api_client, method)(url, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Payment.objects.filter(pk=purpose_payment.id).exists()

    def test_update_summit_anket_after_delete_payment(
            self, rf, allow_any_payment_update_destroy_view, summit_anket_payment):
        anket = summit_anket_payment.purpose

        old_value = anket.value
        request = rf.delete('/payment/{}/'.format(summit_anket_payment.id))
        view = allow_any_payment_update_destroy_view.as_view()
        view(request, pk=summit_anket_payment.id)

        anket.refresh_from_db()
        new_value = anket.value
        assert old_value > new_value

    def test_update_deal_after_delete_payment(
            self, rf, allow_any_payment_update_destroy_view, deal_payment):
        deal = deal_payment.purpose
        deal.done = True
        deal.save()

        request = rf.delete('/payment/{}/'.format(deal_payment.id))
        view = allow_any_payment_update_destroy_view.as_view()
        view(request, pk=deal_payment.id)

        deal.refresh_from_db()
        assert not deal.done

    @pytest.mark.parametrize(
        'field,new_value,is_required', CHANGED_FIELDS)
    def test_update_deal_after_update_payment(
            self, request, rf, allow_any_payment_update_destroy_view, deal_payment, field, new_value, is_required):
        deal = deal_payment.purpose
        deal.done = True
        deal.save()

        if isinstance(new_value, Factory):
            obj = request.getfuncargvalue(new_value.name)()
            data = {field: obj.id}
        else:
            data = {field: new_value}

        request = rf.patch('/payment/{}/'.format(deal_payment.id), data=json.dumps(data),
                           content_type='application/json')
        view = allow_any_payment_update_destroy_view.as_view()
        view(request, pk=deal_payment.id)

        deal.refresh_from_db()
        if is_required:
            assert not deal.done
        else:
            assert deal.done

    def test_update_summit_anket_after_update_payment(
            self, rf, allow_any_payment_update_destroy_view, summit_anket_payment, summit_anket_factory):
        anket = summit_anket_payment.purpose
        new_anket = summit_anket_factory()

        old_value = anket.value
        params = json.dumps({"object_id": new_anket.id})
        request = rf.patch('/payment/{}/'.format(summit_anket_payment.id), data=params,
                           content_type='application/json')
        view = allow_any_payment_update_destroy_view.as_view()
        r = view(request, pk=summit_anket_payment.id)
        assert r.status_code == status.HTTP_200_OK

        anket.refresh_from_db()
        new_value = anket.value
        assert old_value > new_value


@pytest.mark.django_db
@pytest.mark.urls('payment.tests.urls')
class TestPaymentListView:
    def test_list_payment(self, rf, allow_any_payment_list_view):
        request = rf.get('/payments/')
        view = allow_any_payment_list_view.as_view()
        response = view(request)

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.parametrize('purpose', ['deal', 'partnership', 'summitanket'])
    def test_list_payment_with_filter(self, rf, allow_any_payment_list_view, purpose):
        request = rf.get('/payments/', {'purpose': purpose})
        view = allow_any_payment_list_view.as_view()
        response = view(request)

        assert response.status_code == status.HTTP_200_OK
