# -*- coding: utf-8
from __future__ import absolute_import, unicode_literals

import pytest
from django.urls import reverse
from django.utils import timezone
import datetime

from rest_framework import status


@pytest.mark.django_db
class TestNotificationTheme:
    def test_today_less_30_notifications(self, api_login_client, notification_factory):
        url = reverse('notification-today')
        notification_factory.create_batch(20, date=timezone.now().date())
        notification_factory.create_batch(
            30, date=timezone.now().date() + datetime.timedelta(days=1))
        notification_factory.create_batch(
            30, date=timezone.now().date() - datetime.timedelta(days=1))

        response = api_login_client.get(url, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 20

    def test_today_more_30_notifications(self, api_login_client, notification_factory):
        url = reverse('notification-today')
        notification_factory.create_batch(40, date=timezone.now().date())
        notification_factory.create_batch(
            50, date=timezone.now().date() + datetime.timedelta(days=1))
        notification_factory.create_batch(
            50, date=timezone.now().date() - datetime.timedelta(days=1))

        response = api_login_client.get(url, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 30
