# -*- coding: utf-8
from __future__ import absolute_import, unicode_literals

import pytest
from django.conf import settings

from account.models import CustomUser
from account.permissions import CanSeeAccountPage, can_see_account_page, CanCreateUser, CanExportUserList, \
    CanSeeUserList, can_create_user, can_export_user_list, can_see_user_list, can_edit_status_block, \
    can_edit_description_block


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

    def test_is_ancestor(self, user, user_factory):
        u = user_factory(master=user)
        request = type('Request', (), {'user': user})
        assert CanSeeAccountPage().has_object_permission(request, None, u)

    def test_not_is_ancestor(self, user, user_factory):
        u = user_factory(master=user_factory())
        request = type('Request', (), {'user': user})
        assert not CanSeeAccountPage().has_object_permission(request, None, u)

    def test_is_partner_responsible(self, partner, partner_factory):
        p = partner_factory(responsible=partner)
        request = type('Request', (), {'user': partner.user})
        assert CanSeeAccountPage().has_object_permission(request, None, p.user)

    def test_not_is_partner_responsible(self, partner, partner_factory):
        p = partner_factory(responsible=partner_factory())
        request = type('Request', (), {'user': partner.user})
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
        profile = summit_anket_factory(role=level)
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

    def test_have_children(self, user, user_factory):
        user_factory(master=user)
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

    def test_is_ancestor(self, user, user_factory):
        u = user_factory(master=user)
        assert can_see_account_page(user, u)

    def test_not_is_ancestor(self, user, user_factory):
        u = user_factory(master=user_factory())
        assert not can_see_account_page(user, u)

    def test_is_partner_responsible(self, partner, partner_factory):
        p = partner_factory(responsible=partner)
        assert can_see_account_page(partner.user, p.user)

    def test_not_is_partner_responsible(self, partner, partner_factory):
        p = partner_factory(responsible=partner_factory())
        assert not can_see_account_page(partner.user, p.user)


@pytest.mark.django_db
class TestCanCreateUserFunc:
    @pytest.mark.parametrize('is_staff', (True, False))
    def test_is_staff(self, user, is_staff):
        user.is_staff = is_staff
        user.save()
        assert can_create_user(user) == is_staff

    @pytest.mark.parametrize('hierarchy_level', list(range(11)))
    def test_hierarchy_level(self, user, hierarchy_level, hierarchy_factory):
        user.hierarchy = hierarchy_factory(level=hierarchy_level)
        user.save()
        assert can_create_user(user) == user.is_leader_or_high

    @pytest.mark.parametrize('level', list(settings.PARTNER_LEVELS.values()), ids=list(settings.PARTNER_LEVELS.keys()))
    def test_by_partnership(self, monkeypatch, user, level):
        has_perm = level <= settings.PARTNER_LEVELS['supervisor']
        monkeypatch.setattr(CustomUser, 'is_partner_supervisor_or_high', property(lambda s: has_perm))
        assert can_create_user(user) == has_perm

    @pytest.mark.parametrize(
        'level', list(settings.SUMMIT_ANKET_ROLES.values()), ids=list(settings.SUMMIT_ANKET_ROLES.keys()))
    def test_by_summit_level(self, summit_anket_factory, level):
        profile = summit_anket_factory(role=level)
        assert can_create_user(profile.user) == (level >= settings.SUMMIT_ANKET_ROLES['supervisor'])


@pytest.mark.django_db
class TestCanExportUserListFunc:
    @pytest.mark.parametrize('is_staff', (True, False))
    def test_is_staff(self, user, is_staff):
        user.is_staff = is_staff
        user.save()
        assert can_export_user_list(user) == is_staff

    @pytest.mark.parametrize('hierarchy_level', list(range(11)))
    def test_hierarchy_level(self, user, hierarchy_level, hierarchy_factory):
        user.hierarchy = hierarchy_factory(level=hierarchy_level)
        user.save()
        assert can_export_user_list(user) == user.is_pastor_or_high


@pytest.mark.django_db
class TestCanSeeUserListFunc:
    @pytest.mark.parametrize('is_staff', (True, False))
    def test_is_staff(self, user, is_staff):
        user.is_staff = is_staff
        user.save()
        assert can_see_user_list(user) == is_staff

    def test_have_children(self, user, user_factory):
        user_factory(master=user)
        assert can_see_user_list(user)

    def test_dont_have_children(self, user):
        assert not can_see_user_list(user)


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

    def test_is_ancestor(self, user, user_factory):
        u = user_factory(master=user)
        assert can_edit_status_block(user, u)

    def test_not_is_ancestor(self, user, user_factory):
        u = user_factory(master=user_factory())
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

    def test_is_ancestor(self, user, user_factory):
        u = user_factory(master=user)
        assert can_edit_description_block(user, u)

    def test_not_is_ancestor(self, user, user_factory):
        u = user_factory(master=user_factory())
        assert not can_edit_description_block(user, u)
