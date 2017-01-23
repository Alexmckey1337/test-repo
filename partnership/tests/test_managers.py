# -*- coding: utf-8
from __future__ import absolute_import, unicode_literals

import pytest
#
# import rest_framework.compat

from partnership.models import Partnership, Deal


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

    # # TODO
    # def test_for_user(self, user, monkeypatch):
    #     def mockreturn(user):
    #         return True
    #     monkeypatch.setattr(rest_framework.compat, 'is_authenticated', mockreturn)
    #
    #     assert Partnership.objects.get_queryset().for_user(user).count() == 0


@pytest.mark.django_db
class TestDealManager:
    @pytest.mark.parametrize('method, value_name', (
            ('annotate_full_name', 'full_name'),
            ('annotate_responsible_name', 'responsible_name'),
            ('annotate_total_sum', 'total_sum')))
    def test_annotate_(self, method, value_name, partner):
        manager_value = getattr(getattr(Deal.objects, method)()[0], value_name)
        qs_value = getattr(getattr(Deal.objects.get_queryset(), method)()[0], value_name)
        assert manager_value == qs_value
