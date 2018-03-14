# -*- coding: utf-8
from __future__ import absolute_import, unicode_literals

import pytest

from apps.partnership.models import Partnership, Deal


@pytest.mark.django_db
class TestPartnerManager:
    @pytest.mark.parametrize('method, value_name', (
            ('annotate_full_name', 'full_name'),))
    def test_annotate_(self, method, value_name, partner):
        manager_value = getattr(getattr(Partnership.objects, method)()[0], value_name)
        qs_value = getattr(getattr(Partnership.objects.get_queryset(), method)()[0], value_name)
        assert manager_value == qs_value

    def test_for_user(self, user):
        assert len(Partnership.objects.for_user(user)) == len(Partnership.objects.get_queryset().for_user(user))


@pytest.mark.django_db
class TestPartnerQuerySet:
    def test_annotate_full_name(self, partner_factory, user):
        user.first_name = 'Bruce'
        user.last_name = 'Lee'
        user.middle_name = 'Best'
        user.save()
        partner = partner_factory(user=user)
        assert Partnership.objects.filter(id=partner.id).annotate_full_name()[0].full_name == 'Lee Bruce Best'

    def test_annotate_full_name_without_name(self, partner_factory, user):
        user.first_name = ''
        user.last_name = ''
        user.middle_name = ''
        user.save()
        partner = partner_factory(user=user)
        assert Partnership.objects.filter(id=partner.id).annotate_full_name()[0].full_name == '  '


@pytest.mark.django_db
class TestDealManager:
    @pytest.mark.parametrize('method, value_name', (
            ('annotate_full_name', 'full_name'),
            ('annotate_responsible_name', 'responsible_name'),
            ('annotate_total_sum', 'total_sum')))
    def test_annotate_(self, method, value_name, deal_factory):
        deal_factory()
        values = dict(getattr(Deal.objects, method)().values()[0])
        assert value_name in values.keys()

    def test_for_user_if_user_is_anon(self, user, monkeypatch):
        assert Deal.objects.get_queryset().for_user(user).query.is_empty()

    def test_for_user_if_user_is_not_partner(self, user_factory, monkeypatch):
        user = user_factory()
        assert Deal.objects.get_queryset().for_user(user).query.is_empty()

    def test_for_user_if_partner(self, deal_factory, user_user, monkeypatch):
        dd = [i.id for i in deal_factory.create_batch(2)]
        d = [deal_factory(partnership__responsible=user_user).id]
        assert Deal.objects.for_user(user_user).filter(id__in=dd + d).count() == 0

    def test_for_user_if_manager(self, deal_factory, user_manager, monkeypatch):
        dd = [i.id for i in deal_factory.create_batch(2)]
        d = [deal_factory(partnership__responsible=user_manager).id]
        assert Deal.objects.for_user(user_manager).filter(id__in=dd + d).count() == 1

    def test_for_user_if_supervisor(self, deal_factory, user_supervisor, monkeypatch):
        dd = [i.id for i in deal_factory.create_batch(2)]
        d = [deal_factory(partnership__responsible=user_supervisor).id]
        assert Deal.objects.for_user(user_supervisor).filter(id__in=dd + d).count() == 3

    def test_for_user_if_director(self, deal_factory, user_director, monkeypatch):
        dd = [i.id for i in deal_factory.create_batch(2)]
        d = [deal_factory(partnership__responsible=user_director).id]
        assert Deal.objects.for_user(user_director).filter(id__in=dd + d).count() == 3
