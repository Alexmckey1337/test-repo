from datetime import datetime

import pytest
import pytz
from django.urls import reverse
from rest_framework import status, permissions

from apps.lesson.api.views import TextLessonListView, VideoLessonListView
from apps.lesson.tests.conftest import create_lessons, all_lessons


@pytest.mark.django_db
class TestTextLessonListView:
    def test_get_for_guest(self, monkeypatch, api_client, user_factory, text_lesson_factory):
        monkeypatch.setattr(TextLessonListView, 'pagination_class', None)

        create_lessons(text_lesson_factory)
        user = user_factory(hierarchy__level=0)

        api_client.force_login(user=user)
        url = reverse('lessons-text-list')
        response = api_client.get(url, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_for_staff_guest(self, monkeypatch, api_client, user_factory, text_lesson_factory):
        monkeypatch.setattr(TextLessonListView, 'pagination_class', None)

        create_lessons(text_lesson_factory)
        user = user_factory(hierarchy__level=0, is_staff=True)

        api_client.force_login(user=user)
        url = reverse('lessons-text-list')
        response = api_client.get(url, format='json')

        assert len(response.data) == 17

    def test_get_for_user_without_hierarchy(self, monkeypatch, api_client, user_factory, text_lesson_factory):
        monkeypatch.setattr(TextLessonListView, 'pagination_class', None)

        create_lessons(text_lesson_factory)
        user = user_factory(hierarchy=None)

        api_client.force_login(user=user)
        url = reverse('lessons-text-list')
        response = api_client.get(url, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_for_leader(self, monkeypatch, api_client, user_factory, text_lesson_factory):
        monkeypatch.setattr(TextLessonListView, 'pagination_class', None)

        create_lessons(text_lesson_factory)
        user = user_factory(hierarchy__level=1)

        api_client.force_login(user=user)
        url = reverse('lessons-text-list')
        response = api_client.get(url, format='json')

        assert len(response.data) == 16

    @pytest.mark.parametrize('level', list(range(2, 11)))
    def test_get_for_pastor_and_high(self, monkeypatch, api_client, user_factory, text_lesson_factory, level):
        monkeypatch.setattr(TextLessonListView, 'pagination_class', None)

        create_lessons(text_lesson_factory)
        user = user_factory(hierarchy__level=level)

        api_client.force_login(user=user)
        url = reverse('lessons-text-list')
        response = api_client.get(url, format='json')

        assert len(response.data) == 17

    def test_get_without_pagination(self, api_client, user_factory, video_lesson_factory):
        create_lessons(video_lesson_factory)
        user = user_factory(hierarchy__level=100)

        api_client.force_login(user=user)
        url = reverse('lessons-video-list')

        response = api_client.get(url, format='json')
        assert 'results' in response.data

        response = api_client.get(url + '?without_pagination', format='json')
        assert 'results' not in response.data

    def test_filter_by_month(self, monkeypatch, api_client, text_lesson_factory):
        monkeypatch.setattr(TextLessonListView, 'pagination_class', None)
        monkeypatch.setattr(TextLessonListView, 'permission_classes', (permissions.AllowAny,))
        monkeypatch.setattr(TextLessonListView, 'get_queryset', all_lessons)

        text_lesson_factory.create_batch(1, published_date=datetime(2000, 1, 2, tzinfo=pytz.utc))
        text_lesson_factory.create_batch(2, published_date=datetime(2000, 2, 2, tzinfo=pytz.utc))
        text_lesson_factory.create_batch(4, published_date=datetime(2000, 4, 2, tzinfo=pytz.utc))

        url = reverse('lessons-text-list')
        response = api_client.get(f'{url}?month=2000-04', format='json')

        assert len(response.data) == 4

    @pytest.mark.parametrize('is_viewed,count', (
            ('true', 2), ('t', 2), ('yes', 2), ('y', 2), ('on', 2), ('1', 2),
            ('false', 1), ('f', 1), ('no', 1), ('n', 1), ('off', 1), ('0', 1),
            ('', 3), ('other', 3), ('python', 3),
    ), ids=['true', 't', 'yes', 'y', 'on', '1', 'false', 'f', 'no', 'n', 'off', '0', '---', 'other', 'python'])
    def test_filter_by_views(
            self, monkeypatch, api_client, user, text_lesson_factory, text_lesson_view_factory, is_viewed, count):
        monkeypatch.setattr(TextLessonListView, 'pagination_class', None)
        monkeypatch.setattr(TextLessonListView, 'permission_classes', (permissions.AllowAny,))
        monkeypatch.setattr(TextLessonListView, 'get_queryset', all_lessons)

        text_lesson_factory()
        text_lesson_view_factory(lesson=text_lesson_factory(), user=user)
        text_lesson_view_factory(lesson=text_lesson_factory(), user=user)

        api_client.force_login(user=user)
        url = reverse('lessons-text-list')
        response = api_client.get(f'{url}?is_viewed={is_viewed}', format='json')

        assert len(response.data) == count

    @pytest.mark.parametrize('is_liked,count', (
            ('true', 2), ('t', 2), ('yes', 2), ('y', 2), ('on', 2), ('1', 2),
            ('false', 1), ('f', 1), ('no', 1), ('n', 1), ('off', 1), ('0', 1),
            ('', 3), ('other', 3), ('python', 3),
    ), ids=['true', 't', 'yes', 'y', 'on', '1', 'false', 'f', 'no', 'n', 'off', '0', '---', 'other', 'python'])
    def test_filter_by_likes(
            self, monkeypatch, api_client, user, text_lesson_factory, text_lesson_like_factory, is_liked, count):
        monkeypatch.setattr(TextLessonListView, 'pagination_class', None)
        monkeypatch.setattr(TextLessonListView, 'permission_classes', (permissions.AllowAny,))
        monkeypatch.setattr(TextLessonListView, 'get_queryset', all_lessons)

        text_lesson_factory()
        text_lesson_like_factory(lesson=text_lesson_factory(), user=user)
        text_lesson_like_factory(lesson=text_lesson_factory(), user=user)

        api_client.force_login(user=user)
        url = reverse('lessons-text-list')
        response = api_client.get(f'{url}?is_liked={is_liked}', format='json')

        assert len(response.data) == count

    def test_search_by_title(self, monkeypatch, api_client, text_lesson_factory):
        monkeypatch.setattr(TextLessonListView, 'pagination_class', None)
        monkeypatch.setattr(TextLessonListView, 'permission_classes', (permissions.AllowAny,))
        monkeypatch.setattr(TextLessonListView, 'get_queryset', all_lessons)

        text_lesson_factory(title='best lesson')
        text_lesson_factory(title='asbestos')
        text_lesson_factory(title='i need a doctor')
        text_lesson_factory(title='python')
        text_lesson_factory(title='other')

        url = reverse('lessons-text-list')
        response = api_client.get(f'{url}?search_title=best', format='json')

        assert len(response.data) == 2


@pytest.mark.django_db
class TestVideoLessonListView:
    def test_get_for_guest(self, monkeypatch, api_client, user_factory, video_lesson_factory):
        monkeypatch.setattr(VideoLessonListView, 'pagination_class', None)

        create_lessons(video_lesson_factory)
        user = user_factory(hierarchy__level=0)

        api_client.force_login(user=user)
        url = reverse('lessons-video-list')
        response = api_client.get(url, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_for_staff_guest(self, monkeypatch, api_client, user_factory, video_lesson_factory):
        monkeypatch.setattr(VideoLessonListView, 'pagination_class', None)

        create_lessons(video_lesson_factory)
        user = user_factory(hierarchy__level=0, is_staff=True)

        api_client.force_login(user=user)
        url = reverse('lessons-video-list')
        response = api_client.get(url, format='json')

        assert len(response.data) == 17

    def test_get_for_user_without_hierarchy(self, monkeypatch, api_client, user_factory, video_lesson_factory):
        monkeypatch.setattr(VideoLessonListView, 'pagination_class', None)

        create_lessons(video_lesson_factory)
        user = user_factory(hierarchy=None)

        api_client.force_login(user=user)
        url = reverse('lessons-video-list')
        response = api_client.get(url, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_for_leader(self, monkeypatch, api_client, user_factory, video_lesson_factory):
        monkeypatch.setattr(VideoLessonListView, 'pagination_class', None)

        create_lessons(video_lesson_factory)
        user = user_factory(hierarchy__level=1)

        api_client.force_login(user=user)
        url = reverse('lessons-video-list')
        response = api_client.get(url, format='json')

        assert len(response.data) == 16

    @pytest.mark.parametrize('level', list(range(2, 11)))
    def test_get_for_pastor_and_high(self, monkeypatch, api_client, user_factory, video_lesson_factory, level):
        monkeypatch.setattr(VideoLessonListView, 'pagination_class', None)

        create_lessons(video_lesson_factory)
        user = user_factory(hierarchy__level=level)

        api_client.force_login(user=user)
        url = reverse('lessons-video-list')
        response = api_client.get(url, format='json')

        assert len(response.data) == 17

    def test_get_without_pagination(self, api_client, user_factory, video_lesson_factory):
        create_lessons(video_lesson_factory)
        user = user_factory(hierarchy__level=100)

        api_client.force_login(user=user)
        url = reverse('lessons-video-list')

        response = api_client.get(url, format='json')
        assert 'results' in response.data

        response = api_client.get(url + '?without_pagination', format='json')
        assert 'results' not in response.data

    def test_filter_by_month(self, monkeypatch, api_client, video_lesson_factory):
        monkeypatch.setattr(VideoLessonListView, 'pagination_class', None)
        monkeypatch.setattr(VideoLessonListView, 'permission_classes', (permissions.AllowAny,))
        monkeypatch.setattr(VideoLessonListView, 'get_queryset', all_lessons)

        video_lesson_factory.create_batch(1, published_date=datetime(2000, 1, 2, tzinfo=pytz.utc))
        video_lesson_factory.create_batch(2, published_date=datetime(2000, 2, 2, tzinfo=pytz.utc))
        video_lesson_factory.create_batch(4, published_date=datetime(2000, 4, 2, tzinfo=pytz.utc))

        url = reverse('lessons-video-list')
        response = api_client.get(f'{url}?month=2000-04', format='json')

        assert len(response.data) == 4

    @pytest.mark.parametrize('is_viewed,count', (
            ('true', 2), ('t', 2), ('yes', 2), ('y', 2), ('on', 2), ('1', 2),
            ('false', 1), ('f', 1), ('no', 1), ('n', 1), ('off', 1), ('0', 1),
            ('', 3), ('other', 3), ('python', 3),
    ), ids=['true', 't', 'yes', 'y', 'on', '1', 'false', 'f', 'no', 'n', 'off', '0', '---', 'other', 'python'])
    def test_filter_by_views(
            self, monkeypatch, api_client, user, video_lesson_factory, video_lesson_view_factory, is_viewed, count):
        monkeypatch.setattr(VideoLessonListView, 'pagination_class', None)
        monkeypatch.setattr(VideoLessonListView, 'permission_classes', (permissions.AllowAny,))
        monkeypatch.setattr(VideoLessonListView, 'get_queryset', all_lessons)

        video_lesson_factory()
        video_lesson_view_factory(lesson=video_lesson_factory(), user=user)
        video_lesson_view_factory(lesson=video_lesson_factory(), user=user)

        api_client.force_login(user=user)
        url = reverse('lessons-video-list')
        response = api_client.get(f'{url}?is_viewed={is_viewed}', format='json')

        assert len(response.data) == count

    @pytest.mark.parametrize('is_liked,count', (
            ('true', 2), ('t', 2), ('yes', 2), ('y', 2), ('on', 2), ('1', 2),
            ('false', 1), ('f', 1), ('no', 1), ('n', 1), ('off', 1), ('0', 1),
            ('', 3), ('other', 3), ('python', 3),
    ), ids=['true', 't', 'yes', 'y', 'on', '1', 'false', 'f', 'no', 'n', 'off', '0', '---', 'other', 'python'])
    def test_filter_by_likes(
            self, monkeypatch, api_client, user, video_lesson_factory, video_lesson_like_factory, is_liked, count):
        monkeypatch.setattr(VideoLessonListView, 'pagination_class', None)
        monkeypatch.setattr(VideoLessonListView, 'permission_classes', (permissions.AllowAny,))
        monkeypatch.setattr(VideoLessonListView, 'get_queryset', all_lessons)

        video_lesson_factory()
        video_lesson_like_factory(lesson=video_lesson_factory(), user=user)
        video_lesson_like_factory(lesson=video_lesson_factory(), user=user)

        api_client.force_login(user=user)
        url = reverse('lessons-video-list')
        response = api_client.get(f'{url}?is_liked={is_liked}', format='json')

        assert len(response.data) == count

    def test_search_by_title(self, monkeypatch, api_client, video_lesson_factory):
        monkeypatch.setattr(VideoLessonListView, 'pagination_class', None)
        monkeypatch.setattr(VideoLessonListView, 'permission_classes', (permissions.AllowAny,))
        monkeypatch.setattr(VideoLessonListView, 'get_queryset', all_lessons)

        video_lesson_factory(title='best lesson')
        video_lesson_factory(title='asbestos')
        video_lesson_factory(title='i need a doctor')
        video_lesson_factory(title='python')
        video_lesson_factory(title='other')

        url = reverse('lessons-video-list')
        response = api_client.get(f'{url}?search_title=best', format='json')

        assert len(response.data) == 2
