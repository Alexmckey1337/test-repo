from datetime import datetime
from random import choice, randint, choices

import pytz
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.account.models import CustomUser
from apps.lesson.models import (
    TextLesson, VideoLesson, TextLessonLike, TextLessonView, VideoLessonLike, VideoLessonView
)

YOUTUBE_URLS = [
    'tGKlj-g6dWY',
    'y4gWr2fya0I',
    'jW3hrpmM4x8',
    'vf4opUPLms0',
    '3my2mOOHoNU',
    'eSAaezNVois',
    'op_ezfXiZuA',
    'boah9hNHhi0',
    'q1T1gZ5RRTU',
    'Qvz3azTWDNo',
    '0DTHf7NwREY',
    'w-kBRUXsuSQ',
    'SNEABGfkWhQ',
    'kEf1xSwX5D8',
    'EGqRV-oFEzk',
    '8vWhKGugn9M',
    '01ic3jagLOs',
    '3gvjDqhYJ60',
]


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--size', type=int, default=2)

    def handle(self, *args, **options):
        size = options.get('size')
        size = size if size > 0 else 2

        self.stdout.write('Start...')

        creators = list(CustomUser.objects.filter(hierarchy__level__gt=2).values_list('pk', flat=True)[:10*size])
        authors = [None] + creators
        viewers = list(CustomUser.objects.filter(hierarchy__level__gte=1).values_list('pk', flat=True))
        now = timezone.now()

        texts = list()
        videos = list()

        timestamp = now.timestamp()
        month_secs = 30 * 24 * 60 * 60  # days * hours * minutes * seconds
        published_date_range = (int(timestamp - 5 * month_secs), int(timestamp + 2 * month_secs))

        for i in range(100 * size):
            texts.append(TextLesson(
                title=f'Текстовый урок #{i}',
                author_id=choice(authors),
                creator_id=choice(creators),
                published_date=datetime.fromtimestamp(
                    randint(*published_date_range),
                    tz=pytz.utc
                ),
                status=choice([s[0] for s in TextLesson.STATUS]),
                content='<p>Слушайтесь маму.</p>' * randint(3, 11),
            ))
            videos.append(VideoLesson(
                title=f'Видео урок #{i}',
                author_id=choice(authors),
                creator_id=choice(creators),
                published_date=datetime.fromtimestamp(
                    randint(*published_date_range),
                    tz=pytz.utc
                ),
                status=choice([s[0] for s in TextLesson.STATUS]),
                description='<p>Это мой видео урок.</p>' * randint(3, 11),
                url='https://www.youtube.com/embed/' + choice(YOUTUBE_URLS),
            ))

        text_lessons = [l.pk for l in TextLesson.objects.bulk_create(texts)]
        video_lessons = [l.pk for l in VideoLesson.objects.bulk_create(videos)]

        text_views = list()
        video_views = list()
        text_likes = list()
        video_likes = list()
        for i in range(10_000 * size):
            text_views.append(TextLessonView(
                lesson_id=choice(text_lessons),
                user_id=choice(viewers)
            ))
            video_views.append(VideoLessonView(
                lesson_id=choice(video_lessons),
                user_id=choice(viewers)
            ))

        for l in choices(text_lessons, k=int(len(text_lessons)*0.8)):
            for u in choices(viewers, k=randint(1, 11)):
                text_likes.append(TextLessonLike(
                    lesson_id=l,
                    user_id=u,
                ))

        for l in choices(video_lessons, k=int(len(video_lessons)*0.8)):
            for u in choices(viewers, k=randint(1, 11)):
                video_likes.append(VideoLessonLike(
                    lesson_id=l,
                    user_id=u,
                ))

        TextLessonView.objects.bulk_create(text_views)
        TextLessonLike.objects.bulk_create(text_likes)
        VideoLessonView.objects.bulk_create(video_views)
        VideoLessonLike.objects.bulk_create(video_likes)

        self.stdout.write(
            'Successfully created %s lessons\n' % (200 * size))
