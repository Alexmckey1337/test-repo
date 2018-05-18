import pytest


@pytest.mark.django_db
class TestTextLesson:
    def test_save(self, text_lesson_factory):
        title = 'Урок номер один'
        assert text_lesson_factory(title=title).slug == 'urok-nomer-odin'

    def test_save_with_duplicate_title(self, text_lesson_factory):
        title = 'Урок номер один'
        text_lesson_factory(title=title)
        assert text_lesson_factory(title=title).slug == 'urok-nomer-odin_2'
        assert text_lesson_factory(title=title).slug == 'urok-nomer-odin_3'


@pytest.mark.django_db
class TestVideoLesson:
    def test_save(self, video_lesson_factory):
        title = 'Урок номер один'
        assert video_lesson_factory(title=title).slug == 'urok-nomer-odin'

    def test_save_with_duplicate_title(self, video_lesson_factory):
        title = 'Урок номер один'
        video_lesson_factory(title=title)
        assert video_lesson_factory(title=title).slug == 'urok-nomer-odin_2'
        assert video_lesson_factory(title=title).slug == 'urok-nomer-odin_3'

    def test_youtube_id_without_timestamp(self, video_lesson_factory):
        youtube_id = 'sLu2'
        url = f'https://www.youtube.com/embed/{youtube_id}'
        assert video_lesson_factory(url=url).youtube_id == youtube_id

    def test_youtube_id_with_timestamp(self, video_lesson_factory):
        youtube_id = 'sLu2'
        url = f'https://www.youtube.com/embed/{youtube_id}?t=1h24m42s&other=2'
        assert video_lesson_factory(url=url).youtube_id == youtube_id
