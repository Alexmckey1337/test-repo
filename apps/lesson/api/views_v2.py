from apps.lesson.api.serializers import EmptyTextLessonSerializer, EmptyVideoLessonSerializer
from apps.lesson.api.mixins_v2 import LessonLikeMixin
from apps.lesson.models import TextLesson, VideoLesson, TextLessonLike, VideoLessonLike


class TextLessonLikeView(LessonLikeMixin):
    model = TextLesson
    like_model = TextLessonLike
    serializer_class = EmptyTextLessonSerializer

    def post(self, request, *args, **kwargs):
        """
        Mark text lesson as liked.
        """
        return super().post(request, *args, **kwargs)


class VideoLessonLikeView(LessonLikeMixin):
    model = VideoLesson
    like_model = VideoLessonLike
    serializer_class = EmptyVideoLessonSerializer

    def post(self, request, *args, **kwargs):
        """
        Mark video lesson as liked.
        """
        return super().post(request, *args, **kwargs)