# -*- coding: utf-8
from __future__ import absolute_import, unicode_literals

import json
from datetime import datetime
from decimal import Decimal

import pytest
import pytz
from rest_framework import status, permissions

from apps.partnership.models import Deal, ChurchDeal
from apps.payment.api.filters import FilterByDealDate
from apps.payment.api.views import PaymentDealListView
from apps.payment.models import Payment


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


def get_payment_deal(self):
    return


@pytest.mark.django_db
@pytest.mark.urls('apps.payment.tests.urls')
class TestPaymentUpdateDestroyView:
    def test_delete_payment(self, rf, user, allow_any_payment_update_destroy_view, purpose_payment):
        request = rf.delete('/payment/{}/'.format(purpose_payment.id))
        request.user = user
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
            self, api_client, supervisor_user, purpose_payment, method, code):
        url = '/payment/{}/'.format(purpose_payment.id)
        api_client.force_login(supervisor_user)
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
            self, user, rf, allow_any_payment_update_destroy_view, summit_anket_payment):
        anket = summit_anket_payment.purpose

        old_value = anket.value
        request = rf.delete('/payment/{}/'.format(summit_anket_payment.id))
        request.user = user
        view = allow_any_payment_update_destroy_view.as_view()
        view(request, pk=summit_anket_payment.id)

        anket.refresh_from_db()
        new_value = anket.value
        assert old_value > new_value

    def test_update_deal_after_delete_payment(
            self, user, rf, allow_any_payment_update_destroy_view, deal_payment):
        deal = deal_payment.purpose
        deal.done = True
        deal.save()

        request = rf.delete('/payment/{}/'.format(deal_payment.id))
        request.user = user
        view = allow_any_payment_update_destroy_view.as_view()
        view(request, pk=deal_payment.id)

        deal.refresh_from_db()
        assert not deal.done

    @pytest.mark.parametrize(
        'field,new_value,is_required', CHANGED_FIELDS)
    def test_update_deal_after_update_payment(
            self, user, request, rf, allow_any_payment_update_destroy_view,
            deal_payment, field, new_value, is_required):
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
        request.user = user
        view = allow_any_payment_update_destroy_view.as_view()
        view(request, pk=deal_payment.id)

        deal.refresh_from_db()
        if is_required:
            assert not deal.done
        else:
            assert deal.done

    def test_update_summit_anket_after_update_payment(
            self, user, rf, allow_any_payment_update_destroy_view, summit_anket_payment, summit_anket_factory):
        anket = summit_anket_payment.purpose
        new_anket = summit_anket_factory()

        old_value = anket.value
        params = json.dumps({"object_id": new_anket.id})
        request = rf.patch('/payment/{}/'.format(summit_anket_payment.id), data=params,
                           content_type='application/json')
        request.user = user
        view = allow_any_payment_update_destroy_view.as_view()
        r = view(request, pk=summit_anket_payment.id)
        assert r.status_code == status.HTTP_200_OK

        anket.refresh_from_db()
        new_value = anket.value
        assert old_value > new_value


@pytest.mark.django_db
@pytest.mark.urls('apps.payment.tests.urls')
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


@pytest.mark.django_db
@pytest.mark.urls('apps.payment.tests.urls')
class TestPaymentDealListView:
    def test_list_payment(self, rf, allow_any_payment_list_view):
        request = rf.get('/payments/deal/')
        view = allow_any_payment_list_view.as_view()
        response = view(request)

        assert response.status_code == status.HTTP_200_OK

    def test_filter_by_sum(self, monkeypatch, api_client, deal_payment_factory):
        monkeypatch.setattr(PaymentDealListView, 'permission_classes', (permissions.AllowAny,))
        monkeypatch.setattr(
            PaymentDealListView, 'get_queryset',
            lambda self: self.queryset.filter(content_type__model='deal').add_deal_fio())
        deal_payment_factory(sum=Decimal(100))
        deal_payment_factory(sum=Decimal(200))
        deal_payment_factory(sum=Decimal(300))
        deal_payment_factory(sum=Decimal(400))
        response = api_client.get('/payments/deal/?from_sum=200&to_sum=300', format='json')

        assert len(response.data['results']) == 2

    def test_filter_by_effective_sum(self, monkeypatch, api_client, deal_payment_factory):
        monkeypatch.setattr(PaymentDealListView, 'permission_classes', (permissions.AllowAny,))
        monkeypatch.setattr(
            PaymentDealListView, 'get_queryset',
            lambda self: self.queryset.filter(content_type__model='deal').add_deal_fio())
        deal_payment_factory(effective_sum=Decimal(100), sum=Decimal(100))
        deal_payment_factory(effective_sum=Decimal(200), sum=Decimal(200))
        deal_payment_factory(effective_sum=Decimal(300), sum=Decimal(300))
        deal_payment_factory(effective_sum=Decimal(400), sum=Decimal(400))
        response = api_client.get('/payments/deal/?from_eff_sum=200&to_eff_sum=300', format='json')

        assert len(response.data['results']) == 2

    def test_filter_by_currency_sum(self, monkeypatch, api_client, deal_payment_factory, currency_factory):
        monkeypatch.setattr(PaymentDealListView, 'permission_classes', (permissions.AllowAny,))
        monkeypatch.setattr(
            PaymentDealListView, 'get_queryset',
            lambda self: self.queryset.filter(content_type__model='deal').add_deal_fio())
        cur1 = currency_factory()
        cur2 = currency_factory()
        deal_payment_factory(currency_sum=cur1)
        deal_payment_factory(currency_sum=cur1)
        deal_payment_factory(currency_sum=cur2)
        deal_payment_factory(currency_sum=cur2)
        response = api_client.get('/payments/deal/?currency_sum={}'.format(cur1.id), format='json')

        assert len(response.data['results']) == 2

    def test_filter_by_currency_rate(
            self, monkeypatch, api_client, payment_factory, currency_factory, deal_factory):
        monkeypatch.setattr(PaymentDealListView, 'permission_classes', (permissions.AllowAny,))
        monkeypatch.setattr(
            PaymentDealListView, 'get_queryset',
            lambda self: self.queryset.filter(content_type__model='deal').add_deal_fio())
        cur1 = currency_factory()
        cur2 = currency_factory()
        deal1 = deal_factory(partnership__currency=cur1)
        deal2 = deal_factory(partnership__currency=cur1)
        deal3 = deal_factory(partnership__currency=cur2)
        deal4 = deal_factory(partnership__currency=cur2)
        payment_factory(purpose=deal1)
        payment_factory(purpose=deal2)
        payment_factory(purpose=deal3)
        payment_factory(purpose=deal4)
        response = api_client.get('/payments/deal/?currency_rate={}'.format(cur1.id), format='json')

        assert len(response.data['results']) == 2

    def test_search_by_description(self, monkeypatch, api_client, deal_payment_factory):
        monkeypatch.setattr(PaymentDealListView, 'permission_classes', (permissions.AllowAny,))
        monkeypatch.setattr(
            PaymentDealListView, 'get_queryset',
            lambda self: self.queryset.filter(content_type__model='deal').add_deal_fio())
        deal_payment_factory(description='visa')
        deal_payment_factory(description='mastercard')
        deal_payment_factory(description='I am master.')
        deal_payment_factory(description='I am superman.')
        response = api_client.get('/payments/deal/?search_description=master', format='json')

        assert len(response.data['results']) == 2

    def test_filter_by_created_at(self, monkeypatch, api_client, deal_payment_factory):
        monkeypatch.setattr(PaymentDealListView, 'permission_classes', (permissions.AllowAny,))
        monkeypatch.setattr(
            PaymentDealListView, 'get_queryset',
            lambda self: self.queryset.filter(content_type__model='deal').add_deal_fio())
        deal_payment_factory(created_at=datetime(2000, 2, 20, 11, tzinfo=pytz.utc))
        deal_payment_factory(created_at=datetime(2000, 2, 21, 11, tzinfo=pytz.utc))
        deal_payment_factory(created_at=datetime(2000, 2, 22, 11, tzinfo=pytz.utc))
        deal_payment_factory(created_at=datetime(2000, 2, 23, 11, tzinfo=pytz.utc))
        response = api_client.get('/payments/deal/?from_create=2000-02-21&to_create=2000-02-22', format='json')

        assert len(response.data['results']) == 2

    def test_filter_by_sent_date(self, monkeypatch, api_client, deal_payment_factory):
        monkeypatch.setattr(PaymentDealListView, 'permission_classes', (permissions.AllowAny,))
        monkeypatch.setattr(
            PaymentDealListView, 'get_queryset',
            lambda self: self.queryset.filter(content_type__model='deal').add_deal_fio())
        deal_payment_factory(sent_date=datetime(2000, 2, 20, tzinfo=pytz.utc))
        deal_payment_factory(sent_date=datetime(2000, 2, 21, tzinfo=pytz.utc))
        deal_payment_factory(sent_date=datetime(2000, 2, 22, tzinfo=pytz.utc))
        deal_payment_factory(sent_date=datetime(2000, 2, 23, tzinfo=pytz.utc))
        response = api_client.get('/payments/deal/?from_sent=2000-02-21&to_sent=2000-02-22', format='json')

        assert len(response.data['results']) == 2

    def test_filter_by_manager(self, monkeypatch, api_client, deal_payment_factory, user_factory):
        monkeypatch.setattr(PaymentDealListView, 'permission_classes', (permissions.AllowAny,))
        monkeypatch.setattr(
            PaymentDealListView, 'get_queryset',
            lambda self: self.queryset.filter(content_type__model='deal').add_deal_fio())
        manager = user_factory()
        other_manager = user_factory()
        deal_payment_factory(manager=manager)
        deal_payment_factory(manager=manager)
        deal_payment_factory(manager=other_manager)
        deal_payment_factory(manager=other_manager)
        response = api_client.get('/payments/deal/?manager={}'.format(manager.id), format='json')

        assert len(response.data['results']) == 2
    #
    # def test_search_by_purpose_fio(self, monkeypatch, api_client, payment_factory, deal_factory):
    #     monkeypatch.setattr(PaymentDealListView, 'permission_classes', (permissions.AllowAny,))
    #     monkeypatch.setattr(
    #         PaymentDealListView, 'get_queryset',
    #         lambda self: self.queryset.filter(content_type__model='deal').add_deal_fio())
    #     monkeypatch.setattr(FilterByDealDate, 'get_user_deals', lambda self, req: Deal.objects.all())
    #     monkeypatch.setattr(FilterByDealDate, 'get_church_deals', lambda self, req: ChurchDeal.objects.all())
    #
    #     deal1 = deal_factory(partnership__user__first_name='Lee', partnership__user__last_name='Bruce')
    #     deal2 = deal_factory(partnership__user__first_name='Bruce', partnership__user__last_name='Willis')
    #     deal3 = deal_factory(partnership__user__first_name='First', partnership__user__last_name='Last')
    #     deal4 = deal_factory(partnership__user__first_name='Name', partnership__user__last_name='Main')
    #     payment_factory(purpose=deal1)
    #     payment_factory(purpose=deal2)
    #     payment_factory(purpose=deal3)
    #     payment_factory(purpose=deal4)
    #
    #     response = api_client.get('/payments/deal/?search_purpose_fio=bruce', format='json')
    #
    #     assert len(response.data['results']) == 2

    def test_filter_by_purpose_date(self, monkeypatch, api_client, payment_factory, deal_factory):
        monkeypatch.setattr(PaymentDealListView, 'permission_classes', (permissions.AllowAny,))
        monkeypatch.setattr(
            PaymentDealListView, 'get_queryset',
            lambda self: self.queryset.filter(content_type__model='deal').add_deal_fio())
        monkeypatch.setattr(FilterByDealDate, 'get_user_deals', lambda self, req: Deal.objects.all())
        monkeypatch.setattr(FilterByDealDate, 'get_church_deals', lambda self, req: ChurchDeal.objects.all())

        deal1 = deal_factory(date_created=datetime(2000, 1, 1, tzinfo=pytz.utc))
        deal2 = deal_factory(date_created=datetime(2000, 2, 21, tzinfo=pytz.utc))
        deal3 = deal_factory(date_created=datetime(2000, 3, 22, tzinfo=pytz.utc))
        deal4 = deal_factory(date_created=datetime(2000, 4, 23, tzinfo=pytz.utc))
        payment_factory(purpose=deal1)
        payment_factory(purpose=deal2)
        payment_factory(purpose=deal3)
        payment_factory(purpose=deal4)

        response = api_client.get(
            '/payments/deal/?from_purpose_date=2000-02-21&to_purpose_date=2000-03-22', format='json')

        assert len(response.data['results']) == 2
    #
    # def test_search_by_purpose_manager_fio(
    #         self, monkeypatch, api_client, payment_factory, deal_factory, partner_factory):
    #     monkeypatch.setattr(PaymentDealListView, 'permission_classes', (permissions.AllowAny,))
    #     monkeypatch.setattr(
    #         PaymentDealListView, 'get_queryset',
    #         lambda self: self.queryset.filter(content_type__model='deal').add_deal_fio())
    #     monkeypatch.setattr(FilterByDealManagerFIO, 'get_deals', lambda self, req: Deal.objects.all())
    #
    #     responsible1 = partner_factory(user__first_name='Lee', user__last_name='Bruce')
    #     responsible2 = partner_factory(user__first_name='Bruce', user__last_name='Willis')
    #     responsible3 = partner_factory(user__first_name='First', user__last_name='Last')
    #     responsible4 = partner_factory(user__first_name='Name', user__last_name='Main')
    #     deal1 = deal_factory(partnership=partner_factory(responsible=responsible1))
    #     deal2 = deal_factory(partnership=partner_factory(responsible=responsible2))
    #     deal3 = deal_factory(partnership=partner_factory(responsible=responsible3))
    #     deal4 = deal_factory(partnership=partner_factory(responsible=responsible4))
    #     payment_factory(purpose=deal1)
    #     payment_factory(purpose=deal2)
    #     payment_factory(purpose=deal3)
    #     payment_factory(purpose=deal4)
    #
    #     response = api_client.get('/payments/deal/?search_purpose_manager_fio=bruce', format='json')
    #
    #     assert len(response.data['results']) == 2
