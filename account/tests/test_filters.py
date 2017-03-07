import pytest

from account.filters import FilterMasterTree
from account.models import CustomUser


@pytest.mark.django_db
class TestFilterMasterTree:
    def test_without_master_tree(self, user_factory):
        user_factory.create_batch(6)
        qs = CustomUser.objects.all()
        filter_qs = FilterMasterTree().filter_queryset(
            type('Request', (), {'query_params': dict()}),
            qs, None
        )
        assert filter_qs.count() == qs.count()

    def test_master_is_leaf_node(self, user_factory):
        user = user_factory()
        qs = CustomUser.objects.all()
        filter_qs = FilterMasterTree().filter_queryset(
            type('Request', (), {'query_params': {'master_tree': user.id}}),
            qs, None
        )
        assert filter_qs.count() == 0

    def test_with_master(self, user_factory):
        user = user_factory()  # count: + 0, = 0, all_users_count: +1, = 1

        user_factory.create_batch(3, master=user)  # count: + 3, = 3, all_users_count: +3, = 4
        second_level_user = user_factory(master=user)  # count: + 1, = 4, all_users_count: +1, = 5
        user_factory.create_batch(8, master=second_level_user)  # count: + 8, = 12, all_users_count: +8, = 13

        user_factory.create_batch(15)  # count: + 0, = 12, all_users_count: +15, = 28
        other_user = user_factory()  # count: + 0, = 12, all_users_count: +1, = 29
        user_factory.create_batch(32, master=other_user)  # count: + 0, = 12, all_users_count: + 32, = 61

        qs = CustomUser.objects.all()
        filter_qs = FilterMasterTree().filter_queryset(
            type('Request', (), {'query_params': {'master_tree': user.id}}),
            qs, None
        )
        assert filter_qs.count() == 12
