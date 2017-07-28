from datetime import date

import pytest
from rest_framework import exceptions

from partnership.filters import FilterPartnerMasterTreeWithSelf, FilterByPartnerBirthday
from partnership.models import Partnership


@pytest.mark.django_db
class TestFilterPartnerMasterTreeWithSelf:
    def test_without_master_tree(self, partner_factory):
        partner_factory.create_batch(6)
        qs = Partnership.objects.all()
        filter_qs = FilterPartnerMasterTreeWithSelf().filter_queryset(
            type('Request', (), {'query_params': dict()}),
            qs, None
        )
        assert filter_qs.count() == qs.count()

    def test_master_is_leaf_node(self, partner_factory):
        partner = partner_factory()
        partner_factory.create_batch(6)
        qs = Partnership.objects.all()
        filter_qs = FilterPartnerMasterTreeWithSelf().filter_queryset(
            type('Request', (), {'query_params': {'master_tree': partner.user.id}}),
            qs, None
        )
        assert filter_qs.count() == 1

    def test_with_master(self, partner_factory):
        partner = partner_factory()  # count: + 1, = 1, all_users_count: +1, = 1

        partner_factory.create_batch(3, user__master=partner.user)  # count: + 3, = 4, all_users_count: +3, = 4
        second_level_partner = partner_factory(user__master=partner.user)  # count: + 1, = 5, all_users_count: +1, = 5
        partner_factory.create_batch(
            8, user__master=second_level_partner.user)  # count: + 8, = 13, all_users_count: +8, = 13

        partner_factory.create_batch(15)  # count: + 0, = 13, all_users_count: +15, = 28
        other_partner = partner_factory()  # count: + 0, = 13, all_users_count: +1, = 29
        partner_factory.create_batch(
            32, user__master=other_partner.user)  # count: + 0, = 13, all_users_count: + 32, = 61

        qs = Partnership.objects.all()
        filter_qs = FilterPartnerMasterTreeWithSelf().filter_queryset(
            type('Request', (), {'query_params': {'master_tree': partner.user.id}}),
            qs, None
        )
        assert filter_qs.count() == 13


@pytest.mark.django_db
class TestFilterByPartnerBirthday:
    def test_without_from_date(self, partner_factory):
        from_date = date(1999, 12, 31)
        to_date = date(2000, 1, 2)
        p1 = partner_factory(user__born_date=date(1999, 12, 30))
        p2 = partner_factory(user__born_date=from_date)
        p3 = partner_factory(user__born_date=date(2000, 1, 1))
        p4 = partner_factory(user__born_date=to_date)
        p5 = partner_factory(user__born_date=date(2000, 1, 3))
        ids = (p1.id, p2.id, p3.id, p4.id, p5.id)

        filter_qs = FilterByPartnerBirthday().filter_queryset(
            type('Request', (), {'query_params': {'to_date': to_date.strftime('%Y-%m-%d')}}),
            Partnership.objects.filter(id__in=ids), None
        )
        assert filter_qs.count() == 5

    def test_without_to_date(self, partner_factory):
        from_date = date(1999, 12, 31)
        to_date = date(2000, 1, 2)
        p1 = partner_factory(user__born_date=date(1999, 12, 30))
        p2 = partner_factory(user__born_date=from_date)
        p3 = partner_factory(user__born_date=date(2000, 1, 1))
        p4 = partner_factory(user__born_date=to_date)
        p5 = partner_factory(user__born_date=date(2000, 1, 3))
        ids = (p1.id, p2.id, p3.id, p4.id, p5.id)

        filter_qs = FilterByPartnerBirthday().filter_queryset(
            type('Request', (), {'query_params': {'from_date': from_date.strftime('%Y-%m-%d')}}),
            Partnership.objects.filter(id__in=ids), None
        )
        assert filter_qs.count() == 5

    def test_with_empty_from_date(self, partner_factory):
        from_date = date(1999, 12, 31)
        to_date = date(2000, 1, 2)
        p1 = partner_factory(user__born_date=date(1999, 12, 30))
        p2 = partner_factory(user__born_date=from_date)
        p3 = partner_factory(user__born_date=date(2000, 1, 1))
        p4 = partner_factory(user__born_date=to_date)
        p5 = partner_factory(user__born_date=date(2000, 1, 3))
        ids = (p1.id, p2.id, p3.id, p4.id, p5.id)

        filter_qs = FilterByPartnerBirthday().filter_queryset(
            type('Request', (), {'query_params': {'from_date': '', 'to_date': to_date.strftime('%Y-%m-%d')}}),
            Partnership.objects.filter(id__in=ids), None
        )
        assert filter_qs.count() == 5

    def test_with_empty_to_date(self, partner_factory):
        from_date = date(1999, 12, 31)
        to_date = date(2000, 1, 2)
        p1 = partner_factory(user__born_date=date(1999, 12, 30))
        p2 = partner_factory(user__born_date=from_date)
        p3 = partner_factory(user__born_date=date(2000, 1, 1))
        p4 = partner_factory(user__born_date=to_date)
        p5 = partner_factory(user__born_date=date(2000, 1, 3))
        ids = (p1.id, p2.id, p3.id, p4.id, p5.id)

        filter_qs = FilterByPartnerBirthday().filter_queryset(
            type('Request', (), {'query_params': {'from_date': from_date.strftime('%Y-%m-%d'), 'to_date': ''}}),
            Partnership.objects.filter(id__in=ids), None
        )
        assert filter_qs.count() == 5

    def test_with_from_date_more_than_to_date(self):
        with pytest.raises(exceptions.ValidationError):
            FilterByPartnerBirthday().filter_queryset(
                type('Request', (), {'query_params': {
                    'from_date': date(2000, 2, 22).strftime('%Y-%m-%d'),
                    'to_date': date(2000, 2, 20).strftime('%Y-%m-%d')}}),
                None, None
            )

    def test_filter_queryset(self, partner_factory):
        from_date = date(1999, 12, 31)
        to_date = date(2000, 1, 2)
        p1 = partner_factory(user__born_date=date(1999, 12, 30))
        p2 = partner_factory(user__born_date=from_date)
        p3 = partner_factory(user__born_date=date(2000, 1, 1))
        p4 = partner_factory(user__born_date=to_date)
        p5 = partner_factory(user__born_date=date(2000, 1, 3))
        ids = (p1.id, p2.id, p3.id, p4.id, p5.id)

        filter_qs = FilterByPartnerBirthday().filter_queryset(
            type('Request', (), {'query_params': {
                'from_date': from_date.strftime('%Y-%m-%d'),
                'to_date': to_date.strftime('%Y-%m-%d')}}),
            Partnership.objects.filter(id__in=ids), None
        )
        assert filter_qs.count() == 3
