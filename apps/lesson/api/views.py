from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from apps.lesson.api.mixins import MonthListMixin, LessonDetailMixin, LessonLikeMixin, LessonListMixin
from apps.lesson.api.permissions import CanSeeLessons
from apps.lesson.api.serializers import (
    TextLessonListSerializer, TextLessonDetailSerializer,
    VideoLessonListSerializer, VideoLessonDetailSerializer, EmptyTextLessonSerializer, EmptyVideoLessonSerializer,
    TextLessonViewSerializer)
from apps.lesson.models import TextLesson, VideoLesson, TextLessonLike, VideoLessonLike, TextLessonView


# Text lessons


class TextLessonMonthListView(MonthListMixin):
    model = TextLesson

    def get(self, request, *args, **kwargs):
        """
        Getting list of available months of text lessons

        Returning months and count of lessons
        """
        return super().get(request, *args, **kwargs)


class TextLessonListView(LessonListMixin):
    model = TextLesson
    serializer_class = TextLessonListSerializer

    def get(self, request, *args, **kwargs):
        """
        Getting list of text lessons
        """
        return super().get(request, *args, **kwargs)


class TextLessonDetailView(LessonDetailMixin):
    model = TextLesson
    serializer_class = TextLessonDetailSerializer

    def get(self, request, *args, **kwargs):
        """
        Getting text lesson by slug
        """
        return super().get(request, *args, **kwargs)


class TextLessonLikeView(LessonLikeMixin):
    model = TextLesson
    like_model = TextLessonLike
    serializer_class = EmptyTextLessonSerializer

    def post(self, request, *args, **kwargs):
        """
        Mark text lesson as liked.
        """
        return super().post(request, *args, **kwargs)


class TextLessonViewView(ListAPIView):
    model = TextLessonView
    serializer_class = TextLessonViewSerializer
    permission_classes = (IsAuthenticated, CanSeeLessons)

    def get_queryset(self):
        lesson = self.kwargs['slug']
        user_level = self.request.user.hierarchy.level
        queryset = self.model.objects\
            .filter(lesson__slug=lesson, user__hierarchy__level__lt=user_level)\
            .distinct('user_id')

        user_id = self.request.user.id
        user = self.model.objects\
            .filter(lesson__slug=lesson, user=user_id)\
            .distinct('user_id')

        return queryset | user

# Video lessons


class VideoLessonMonthListView(MonthListMixin):
    model = VideoLesson

    def get(self, request, *args, **kwargs):
        """
        Getting list of available months of video lessons

        Returning months and count of lessons
        """
        return super().get(request, *args, **kwargs)


class VideoLessonListView(LessonListMixin):
    model = VideoLesson
    serializer_class = VideoLessonListSerializer

    def get(self, request, *args, **kwargs):
        """
        Getting list of video lessons
        """
        return super().get(request, *args, **kwargs)


class VideoLessonDetailView(LessonDetailMixin):
    model = VideoLesson
    serializer_class = VideoLessonDetailSerializer

    def get(self, request, *args, **kwargs):
        """
        Getting video lesson by slug
        """
        return super().get(request, *args, **kwargs)


class VideoLessonLikeView(LessonLikeMixin):
    model = VideoLesson
    like_model = VideoLessonLike
    serializer_class = EmptyVideoLessonSerializer

    def post(self, request, *args, **kwargs):
        """
        Mark video lesson as liked.
        """
        return super().post(request, *args, **kwargs)
