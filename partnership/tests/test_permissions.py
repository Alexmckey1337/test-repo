# -*- coding: utf-8
from __future__ import absolute_import, unicode_literals

import pytest
from django.contrib.auth.models import AnonymousUser

from partnership.permissions import IsPartnership


@pytest.mark.django_db
class TestIsPartnership:
    def test_has_permission_for_anon_user(self, rf, user):
        request = rf.get('/')
        request.user = AnonymousUser()

        assert not IsPartnership().has_permission(request, None)

    def test_has_permission_for_non_partner_user(self, rf, user):
        request = rf.get('/')
        request.user = user

        assert not IsPartnership().has_permission(request, None)

    def test_has_permission_for_partner_user(self, rf, partner):
        request = rf.get('/')
        request.user = partner.user

        assert IsPartnership().has_permission(request, None)
