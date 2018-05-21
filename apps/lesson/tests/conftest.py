from datetime import datetime

import pytest
import pytz
from pytest_factoryboy import register

from apps.account.factories import UserFactory
from apps.lesson.factories import (
    TextLessonFactory, TextLessonLikeFactory, TextLessonViewFactory,
    VideoLessonFactory, VideoLessonLikeFactory, VideoLessonViewFactory)
from apps.lesson.models import AbstractLesson

register(UserFactory)
register(TextLessonFactory)
register(TextLessonViewFactory)
register(TextLessonLikeFactory)
register(VideoLessonFactory)
register(VideoLessonViewFactory)
register(VideoLessonLikeFactory)


@pytest.fixture
def user(user_factory):
    return user_factory()


def create_lessons(lesson_factory):
    """
    +--------------------+-----------+----------+-----------+
    |  status            |  leader+  |  pastor  |  pastor+  |
    +--------------------+-----------+----------+-----------+
    |  PUBLISHED         |  80       |  5       |  85       |
    |  past              |  48       |  3       |  51       |
    +--------------------+-----------+----------+-----------+
    |  PUBLISHED + past  |  16       |  1       |  17       |
    +--------------------+-----------+----------+-----------+
    """
    lesson_factory.create_batch(
        1,
        status=AbstractLesson.PUBLISHED,
        published_date=datetime(2000, 2, 20, tzinfo=pytz.utc),
        access_level=AbstractLesson.PASTOR
    )
    lesson_factory.create_batch(
        2,
        status=AbstractLesson.DRAFT,
        published_date=datetime(2000, 2, 20, tzinfo=pytz.utc),
        access_level=AbstractLesson.PASTOR
    )
    lesson_factory.create_batch(
        4,
        status=AbstractLesson.PUBLISHED,
        published_date=datetime(2200, 2, 20, tzinfo=pytz.utc),
        access_level=AbstractLesson.PASTOR
    )
    lesson_factory.create_batch(
        8,
        status=AbstractLesson.DRAFT,
        published_date=datetime(2200, 2, 20, tzinfo=pytz.utc),
        access_level=AbstractLesson.PASTOR
    )
    lesson_factory.create_batch(
        16,
        status=AbstractLesson.PUBLISHED,
        published_date=datetime(2000, 2, 20, tzinfo=pytz.utc),
        access_level=AbstractLesson.LEADER
    )
    lesson_factory.create_batch(
        32,
        status=AbstractLesson.DRAFT,
        published_date=datetime(2000, 2, 20, tzinfo=pytz.utc),
        access_level=AbstractLesson.LEADER
    )
    lesson_factory.create_batch(
        64,
        status=AbstractLesson.PUBLISHED,
        published_date=datetime(2200, 2, 20, tzinfo=pytz.utc),
        access_level=AbstractLesson.LEADER
    )
    lesson_factory.create_batch(
        128,
        status=AbstractLesson.DRAFT,
        published_date=datetime(2200, 2, 20, tzinfo=pytz.utc),
        access_level=AbstractLesson.LEADER
    )


def all_lessons(self):
    qs = self.model.objects.all()
    qs = qs.annotate_count_views_of_user(self.request.user)
    qs = qs.annotate_total_views()
    qs = qs.annotate_total_likes()
    qs = qs.annotate_unique_views()
    qs = qs.annotate_unique_likes()
    qs = qs.annotate_is_liked(self.request.user)
    return qs
