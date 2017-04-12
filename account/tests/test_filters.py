import pytest
from datetime import date

from rest_framework import exceptions

from account.filters import FilterMasterTree, FilterMasterTreeWithSelf, FilterByUserBirthday
from account.models import CustomUser


class BaseTestFilterMasterTree:
    filter_class = None

    def test_without_master_tree(self, user_factory):
        user_factory.create_batch(6)
        qs = CustomUser.objects.all()
        filter_qs = self.filter_class().filter_queryset(
            type('Request', (), {'query_params': dict()}),
            qs, None
        )
        assert filter_qs.count() == qs.count()

    def test_master_is_leaf_node(self, user_factory):
        user = user_factory()
        qs = CustomUser.objects.all()
        filter_qs = self.filter_class().filter_queryset(
            type('Request', (), {'query_params': {'master_tree': user.id}}),
            qs, None
        )
        assert filter_qs.count() == 0


@pytest.mark.django_db
class TestFilterMasterTree(BaseTestFilterMasterTree):
    filter_class = FilterMasterTree

    def test_with_master(self, user_factory):
        user = user_factory()  # count: + 0, = 0, all_users_count: +1, = 1

        user_factory.create_batch(3, master=user)  # count: + 3, = 3, all_users_count: +3, = 4
        second_level_user = user_factory(master=user)  # count: + 1, = 4, all_users_count: +1, = 5
        user_factory.create_batch(8, master=second_level_user)  # count: + 8, = 12, all_users_count: +8, = 13

        user_factory.create_batch(15)  # count: + 0, = 12, all_users_count: +15, = 28
        other_user = user_factory()  # count: + 0, = 12, all_users_count: +1, = 29
        user_factory.create_batch(32, master=other_user)  # count: + 0, = 12, all_users_count: + 32, = 61

        qs = CustomUser.objects.all()
        filter_qs = self.filter_class().filter_queryset(
            type('Request', (), {'query_params': {'master_tree': user.id}}),
            qs, None
        )
        assert filter_qs.count() == 12


@pytest.mark.django_db
class TestFilterMasterTreeWithSelf(BaseTestFilterMasterTree):
    filter_class = FilterMasterTreeWithSelf

    def test_with_master(self, user_factory):
        user = user_factory()  # count: + 1, = 1, all_users_count: +1, = 1

        user_factory.create_batch(3, master=user)  # count: + 3, = 4, all_users_count: +3, = 4
        second_level_user = user_factory(master=user)  # count: + 1, = 5, all_users_count: +1, = 5
        user_factory.create_batch(8, master=second_level_user)  # count: + 8, = 13, all_users_count: +8, = 13

        user_factory.create_batch(15)  # count: + 0, = 13, all_users_count: +15, = 28
        other_user = user_factory()  # count: + 0, = 13, all_users_count: +1, = 29
        user_factory.create_batch(32, master=other_user)  # count: + 0, = 13, all_users_count: + 32, = 61

        qs = CustomUser.objects.all()
        filter_qs = self.filter_class().filter_queryset(
            type('Request', (), {'query_params': {'master_tree': user.id}}),
            qs, None
        )
        assert filter_qs.count() == 13


@pytest.mark.django_db
class TestFilterByBirthday:
    def test_without_from_date(self, user_factory):
        from_date = date(1999, 12, 31)
        to_date = date(2000, 1, 2)
        u1 = user_factory(born_date=date(1999, 12, 30))
        u2 = user_factory(born_date=from_date)
        u3 = user_factory(born_date=date(2000, 1, 1))
        u4 = user_factory(born_date=to_date)
        u5 = user_factory(born_date=date(2000, 1, 3))
        ids = (u1.id, u2.id, u3.id, u4.id, u5.id)

        filter_qs = FilterByUserBirthday().filter_queryset(
            type('Request', (), {'query_params': {'to_date': to_date.strftime('%Y-%m-%d')}}),
            CustomUser.objects.filter(id__in=ids), None
        )
        assert filter_qs.count() == 5

    def test_without_to_date(self, user_factory):
        from_date = date(1999, 12, 31)
        to_date = date(2000, 1, 2)
        u1 = user_factory(born_date=date(1999, 12, 30))
        u2 = user_factory(born_date=from_date)
        u3 = user_factory(born_date=date(2000, 1, 1))
        u4 = user_factory(born_date=to_date)
        u5 = user_factory(born_date=date(2000, 1, 3))
        ids = (u1.id, u2.id, u3.id, u4.id, u5.id)

        filter_qs = FilterByUserBirthday().filter_queryset(
            type('Request', (), {'query_params': {'from_date': from_date.strftime('%Y-%m-%d')}}),
            CustomUser.objects.filter(id__in=ids), None
        )
        assert filter_qs.count() == 5

    def test_with_empty_from_date(self, user_factory):
        from_date = date(1999, 12, 31)
        to_date = date(2000, 1, 2)
        u1 = user_factory(born_date=date(1999, 12, 30))
        u2 = user_factory(born_date=from_date)
        u3 = user_factory(born_date=date(2000, 1, 1))
        u4 = user_factory(born_date=to_date)
        u5 = user_factory(born_date=date(2000, 1, 3))
        ids = (u1.id, u2.id, u3.id, u4.id, u5.id)

        filter_qs = FilterByUserBirthday().filter_queryset(
            type('Request', (), {'query_params': {'from_date': '', 'to_date': to_date.strftime('%Y-%m-%d')}}),
            CustomUser.objects.filter(id__in=ids), None
        )
        assert filter_qs.count() == 5

    def test_with_empty_to_date(self, user_factory):
        from_date = date(1999, 12, 31)
        to_date = date(2000, 1, 2)
        u1 = user_factory(born_date=date(1999, 12, 30))
        u2 = user_factory(born_date=from_date)
        u3 = user_factory(born_date=date(2000, 1, 1))
        u4 = user_factory(born_date=to_date)
        u5 = user_factory(born_date=date(2000, 1, 3))
        ids = (u1.id, u2.id, u3.id, u4.id, u5.id)

        filter_qs = FilterByUserBirthday().filter_queryset(
            type('Request', (), {'query_params': {'from_date': from_date.strftime('%Y-%m-%d'), 'to_date': ''}}),
            CustomUser.objects.filter(id__in=ids), None
        )
        assert filter_qs.count() == 5

    def test_with_from_date_more_than_to_date(self):
        with pytest.raises(exceptions.ValidationError):
            FilterByUserBirthday().filter_queryset(
                type('Request', (), {'query_params': {
                    'from_date': date(2000, 2, 22).strftime('%Y-%m-%d'),
                    'to_date': date(2000, 2, 20).strftime('%Y-%m-%d')}}),
                None, None
            )

    def test_filter_queryset(self, user_factory):
        from_date = date(1999, 12, 31)
        to_date = date(2000, 1, 2)
        u1 = user_factory(born_date=date(1999, 12, 30))
        u2 = user_factory(born_date=from_date)
        u3 = user_factory(born_date=date(2000, 1, 1))
        u4 = user_factory(born_date=to_date)
        u5 = user_factory(born_date=date(2000, 1, 3))
        ids = (u1.id, u2.id, u3.id, u4.id, u5.id)

        filter_qs = FilterByUserBirthday().filter_queryset(
            type('Request', (), {'query_params': {
                'from_date': from_date.strftime('%Y-%m-%d'),
                'to_date': to_date.strftime('%Y-%m-%d')}}),
            CustomUser.objects.filter(id__in=ids), None
        )
        assert filter_qs.count() == 3
