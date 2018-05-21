import factory
import factory.fuzzy

from . import models


class TextLessonFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.TextLesson

    title = factory.Sequence(lambda n: f'Text lesson #{n}')
    creator = factory.SubFactory('apps.account.factories.UserFactory')
    content = factory.Sequence(lambda n: f'Text lesson #{n}')


class VideoLessonFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.VideoLesson

    title = factory.Sequence(lambda n: f'Video lesson #{n}')
    creator = factory.SubFactory('apps.account.factories.UserFactory')
    url = factory.Sequence(lambda n: f'https://www.youtube.com/embed/l{n}')


class TextLessonViewFactory(factory.DjangoModelFactory):
    user = factory.SubFactory('apps.account.factories.UserFactory')
    lesson = factory.SubFactory('apps.lesson.factories.TextLessonFactory')

    class Meta:
        model = models.TextLessonView


class TextLessonLikeFactory(factory.DjangoModelFactory):
    user = factory.SubFactory('apps.account.factories.UserFactory')
    lesson = factory.SubFactory('apps.lesson.factories.TextLessonFactory')

    class Meta:
        model = models.TextLessonLike


class VideoLessonViewFactory(factory.DjangoModelFactory):
    user = factory.SubFactory('apps.account.factories.UserFactory')
    lesson = factory.SubFactory('apps.lesson.factories.VideoLessonFactory')

    class Meta:
        model = models.VideoLessonView


class VideoLessonLikeFactory(factory.DjangoModelFactory):
    user = factory.SubFactory('apps.account.factories.UserFactory')
    lesson = factory.SubFactory('apps.lesson.factories.VideoLessonFactory')

    class Meta:
        model = models.VideoLessonLike
