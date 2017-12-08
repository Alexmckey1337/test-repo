# -*- coding: utf-8
from __future__ import absolute_import, unicode_literals

import pytest
from django.conf import settings

from apps.account.models import CustomUser
from apps.account.api.permissions import CanSeeAccountPage, can_see_account_page, CanCreateUser, CanExportUserList, \
    CanSeeUserList, can_edit_status_block, \
    can_edit_description_block, SeeUserListPermission, CreateUserPermission, ExportUserListPermission


@pytest.mark.django_db
class TestCanSeeAccountPage:
    @pytest.mark.parametrize('is_staff', (True, False))
    def test_is_staff(self, user, user_factory, is_staff):
        u = user_factory()
        user.is_staff = is_staff
        user.save()
        request = type('Request', (), {'user': user})
        assert CanSeeAccountPage().has_object_permission(request, None, u) == is_staff

    @pytest.mark.parametrize('level', list(settings.PARTNER_LEVELS.values()), ids=list(settings.PARTNER_LEVELS.keys()))
    def test_by_partnership(self, monkeypatch, user, user_factory, level):
        has_perm = level <= settings.PARTNER_LEVELS['supervisor']
        u = user_factory()
        monkeypatch.setattr(CustomUser, 'is_partner_supervisor_or_high', property(lambda s: has_perm))
        request = type('Request', (), {'user': user})
        assert CanSeeAccountPage().has_object_permission(request, None, u) == has_perm

    def test_is_ancestor(self, user):
        # u = user_factory(master=user)
        u = user.add_child(username='user', master=user)
        request = type('Request', (), {'user': user})
        assert CanSeeAccountPage().has_object_permission(request, None, u)

    def test_not_is_ancestor(self, user, user_factory):
        # u = user_factory(master=user_factory())
        other_user = user_factory()
        u = other_user.add_child(username='user', master=other_user)
        request = type('Request', (), {'user': user})
        assert not CanSeeAccountPage().has_object_permission(request, None, u)

    def test_is_partner_responsible(self, user_factory, partner_factory, partner_role_factory):
        user = user_factory()
        partner_role_factory(user=user)
        p = partner_factory(responsible=user)
        request = type('Request', (), {'user': user})
        assert CanSeeAccountPage().has_object_permission(request, None, p.user)

    def test_not_is_partner_responsible(self, partner_factory, user_factory):
        user = user_factory()
        p = partner_factory(responsible=user_factory())
        request = type('Request', (), {'user': user})
        assert not CanSeeAccountPage().has_object_permission(request, None, p.user)


@pytest.mark.django_db
class TestCanCreateUser:
    @pytest.mark.parametrize('is_staff', (True, False))
    def test_is_staff(self, user, is_staff):
        user.is_staff = is_staff
        user.save()
        request = type('Request', (), {'user': user})
        assert CanCreateUser().has_permission(request, None) == is_staff

    @pytest.mark.parametrize('hierarchy_level', list(range(11)))
    def test_hierarchy_level(self, user, hierarchy_level, hierarchy_factory):
        user.hierarchy = hierarchy_factory(level=hierarchy_level)
        user.save()
        request = type('Request', (), {'user': user})
        assert CanCreateUser().has_permission(request, None) == user.is_leader_or_high

    @pytest.mark.parametrize('level', list(settings.PARTNER_LEVELS.values()), ids=list(settings.PARTNER_LEVELS.keys()))
    def test_by_partnership(self, monkeypatch, user, level):
        has_perm = level <= settings.PARTNER_LEVELS['supervisor']
        monkeypatch.setattr(CustomUser, 'is_partner_supervisor_or_high', property(lambda s: has_perm))
        request = type('Request', (), {'user': user})
        assert CanCreateUser().has_permission(request, None) == has_perm

    @pytest.mark.parametrize(
        'level', list(settings.SUMMIT_ANKET_ROLES.values()), ids=list(settings.SUMMIT_ANKET_ROLES.keys()))
    def test_by_summit_level(self, summit_anket_factory, level):
        profile = summit_anket_factory(role=level, user__hierarchy__level=0)
        request = type('Request', (), {'user': profile.user})
        assert CanCreateUser().has_permission(request, None) == (level >= settings.SUMMIT_ANKET_ROLES['supervisor'])


@pytest.mark.django_db
class TestCanExportUserList:
    @pytest.mark.parametrize('is_staff', (True, False))
    def test_is_staff(self, user, is_staff):
        user.is_staff = is_staff
        user.save()
        request = type('Request', (), {'user': user})
        assert CanExportUserList().has_permission(request, None) == is_staff

    @pytest.mark.parametrize('hierarchy_level', list(range(11)))
    def test_hierarchy_level(self, user, hierarchy_level, hierarchy_factory):
        user.hierarchy = hierarchy_factory(level=hierarchy_level)
        user.save()
        request = type('Request', (), {'user': user})
        assert CanExportUserList().has_permission(request, None) == user.is_pastor_or_high


@pytest.mark.django_db
class TestCanSeeUserList:
    @pytest.mark.parametrize('is_staff', (True, False))
    def test_is_staff(self, user, is_staff):
        user.is_staff = is_staff
        user.save()
        request = type('Request', (), {'user': user})
        assert CanSeeUserList().has_permission(request, None) == is_staff

    def test_have_children(self, user):
        # user_factory(master=user)
        user.add_child(username='user', master=user)
        request = type('Request', (), {'user': user})
        assert CanSeeUserList().has_permission(request, None)

    def test_dont_have_children(self, user):
        request = type('Request', (), {'user': user})
        assert not CanSeeUserList().has_permission(request, None)


@pytest.mark.django_db
class TestCanSeeAccountPageFunc:
    @pytest.mark.parametrize('is_staff', (True, False))
    def test_is_staff(self, user, user_factory, is_staff):
        u = user_factory()
        user.is_staff = is_staff
        user.save()
        assert can_see_account_page(user, u) == is_staff

    @pytest.mark.parametrize('level', list(settings.PARTNER_LEVELS.values()), ids=list(settings.PARTNER_LEVELS.keys()))
    def test_by_partnership(self, monkeypatch, user, user_factory, level):
        has_perm = level <= settings.PARTNER_LEVELS['supervisor']
        u = user_factory()
        monkeypatch.setattr(CustomUser, 'is_partner_supervisor_or_high', property(lambda s: has_perm))
        assert can_see_account_page(user, u) == has_perm

    def test_is_ancestor(self, user):
        # u = user_factory(master=user)
        u = user.add_child(username='user', master=user)
        assert can_see_account_page(user, u)

    def test_not_is_ancestor(self, user, user_factory):
        # u = user_factory(master=user_factory())
        other_user = user_factory()
        u = other_user.add_child(username='user', master=other_user)
        assert not can_see_account_page(user, u)

    def test_is_partner_responsible(self, user_factory, partner_role_factory, partner_factory):
        user = user_factory()
        partner_role_factory(user=user)
        p = partner_factory(responsible=user)
        assert can_see_account_page(user, p.user)

    def test_not_is_partner_responsible(self, partner_factory, user_factory):
        user = user_factory()
        p = partner_factory(responsible=user_factory())
        assert not can_see_account_page(user, p.user)


@pytest.mark.django_db
class TestCanCreateUserFunc:
    @pytest.mark.parametrize('is_staff', (True, False))
    def test_is_staff(self, user, is_staff):
        user.is_staff = is_staff
        user.save()
        assert CreateUserPermission(user).has_permission() == is_staff

    @pytest.mark.parametrize('hierarchy_level', list(range(11)))
    def test_hierarchy_level(self, user, hierarchy_level, hierarchy_factory):
        user.hierarchy = hierarchy_factory(level=hierarchy_level)
        user.save()
        assert CreateUserPermission(user).has_permission() == user.is_leader_or_high

    @pytest.mark.parametrize('level', list(settings.PARTNER_LEVELS.values()), ids=list(settings.PARTNER_LEVELS.keys()))
    def test_by_partnership(self, monkeypatch, user, level):
        has_perm = level <= settings.PARTNER_LEVELS['supervisor']
        monkeypatch.setattr(CustomUser, 'is_partner_supervisor_or_high', property(lambda s: has_perm))
        assert CreateUserPermission(user).has_permission() == has_perm

    @pytest.mark.parametrize(
        'level', list(settings.SUMMIT_ANKET_ROLES.values()), ids=list(settings.SUMMIT_ANKET_ROLES.keys()))
    def test_by_summit_level(self, summit_anket_factory, level):
        profile = summit_anket_factory(role=level, user__hierarchy__level=0)
        assert (CreateUserPermission(profile.user).has_permission() ==
                (level >= settings.SUMMIT_ANKET_ROLES['supervisor']))


@pytest.mark.django_db
class TestCanExportUserListFunc:
    @pytest.mark.parametrize('is_staff', (True, False))
    def test_is_staff(self, user, is_staff):
        user.is_staff = is_staff
        user.save()
        assert ExportUserListPermission(user).has_permission() == is_staff

    @pytest.mark.parametrize('hierarchy_level', list(range(11)))
    def test_hierarchy_level(self, user, hierarchy_level, hierarchy_factory):
        user.hierarchy = hierarchy_factory(level=hierarchy_level)
        user.save()
        assert ExportUserListPermission(user).has_permission() == user.is_pastor_or_high


@pytest.mark.django_db
class TestSeeUserListPermission:
    @pytest.mark.parametrize('is_staff', (True, False))
    def test_is_staff(self, user, is_staff):
        user.is_staff = is_staff
        user.save()
        assert SeeUserListPermission(user).has_permission() == is_staff

    def test_have_children(self, user):
        # user_factory(master=user)
        user.add_child(username='user', master=user)
        assert SeeUserListPermission(user).has_permission()

    def test_dont_have_children(self, user):
        assert not SeeUserListPermission(user).has_permission()


@pytest.mark.django_db
class TestCanEditStatusBlock:
    @pytest.mark.parametrize('level', list(settings.PARTNER_LEVELS.values()), ids=list(settings.PARTNER_LEVELS.keys()))
    def test_by_partnership(self, monkeypatch, user, user_factory, level):
        u = user_factory()
        has_perm = level <= settings.PARTNER_LEVELS['supervisor']
        monkeypatch.setattr(CustomUser, 'is_partner_supervisor_or_high', property(lambda s: has_perm))
        assert can_edit_status_block(user, u) == has_perm

    @pytest.mark.parametrize(
        'level', list(settings.SUMMIT_ANKET_ROLES.values()), ids=list(settings.SUMMIT_ANKET_ROLES.keys()))
    def test_by_summit_level(self, summit_anket_factory, user_factory, level):
        profile = summit_anket_factory(role=level)
        u = user_factory()
        assert can_edit_status_block(profile.user, u) == (level >= settings.SUMMIT_ANKET_ROLES['supervisor'])

    def test_is_ancestor(self, user):
        # u = user_factory(master=user)
        u = user.add_child(username='user', master=user)
        assert can_edit_status_block(user, u)

    def test_not_is_ancestor(self, user, user_factory):
        # u = user_factory(master=user_factory())
        other_user = user_factory()
        u = other_user.add_child(username='user', master=other_user)
        assert not can_edit_status_block(user, u)


@pytest.mark.django_db
class TestCanEditDescriptionBlock:
    @pytest.mark.parametrize('level', list(settings.PARTNER_LEVELS.values()), ids=list(settings.PARTNER_LEVELS.keys()))
    def test_by_partnership(self, monkeypatch, user, user_factory, level):
        u = user_factory()
        has_perm = level <= settings.PARTNER_LEVELS['supervisor']
        monkeypatch.setattr(CustomUser, 'is_partner_supervisor_or_high', property(lambda s: has_perm))
        assert can_edit_description_block(user, u) == has_perm

    @pytest.mark.parametrize(
        'level', list(settings.SUMMIT_ANKET_ROLES.values()), ids=list(settings.SUMMIT_ANKET_ROLES.keys()))
    def test_by_summit_level(self, summit_anket_factory, user_factory, level):
        profile = summit_anket_factory(role=level)
        u = user_factory()
        assert can_edit_description_block(profile.user, u) == (level >= settings.SUMMIT_ANKET_ROLES['supervisor'])

    def test_is_ancestor(self, user):
        # u = user_factory(master=user)
        u = user.add_child(username='user', master=user)
        assert can_edit_description_block(user, u)

    def test_not_is_ancestor(self, user, user_factory):
        # u = user_factory(master=user_factory())
        other_user = user_factory()
        u = other_user.add_child(username='user', master=other_user)
        assert not can_edit_description_block(user, u)
