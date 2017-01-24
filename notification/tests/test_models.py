# -*- coding: utf-8
from __future__ import absolute_import, unicode_literals

import pytest


@pytest.mark.django_db
class TestNotificationTheme:
    def test__str__(self, notification_theme):
        assert notification_theme.__str__() == notification_theme.title


@pytest.mark.django_db
class TestNotification:
    def test__str__(self, notification):
        assert notification.__str__() == '{} {}'.format(notification.fullname, notification.theme)

    def test_fullname(self, notification, user):
        assert notification.fullname == user.get_full_name()

    def test_uid(self, notification, user):
        assert notification.uid == str(user.id)
