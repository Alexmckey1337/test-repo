from typing import Union, Type

from django.utils.translation import ugettext_lazy as _

from rest_framework.response import Response
from rest_framework.generics import GenericAPIView

from apps.lesson.models import TextLesson, VideoLesson, TextLessonLike, VideoLessonLike, AbstractLesson
from apps.lesson.api.permissions import CanLikeLessons
from apps.account.api.permissions import HasUserTokenPermission


class LessonObjectMixin(GenericAPIView):
    model: Union[Type[TextLesson], Type[VideoLesson]]
    lesson: AbstractLesson

    def get_queryset(self):
        qs = self.model.published.for_user(self.request.user)
        qs = qs.annotate_count_views_of_user(self.request.user)
        qs = qs.annotate_total_views()
        qs = qs.annotate_total_likes()
        qs = qs.annotate_unique_views()
        qs = qs.annotate_unique_likes()
        qs = qs.annotate_is_liked(self.request.user)
        return qs

    def get_object(self):
        self.lesson = super().get_object()
        return self.lesson


class LessonLikeMixin(LessonObjectMixin):
    lookup_field = 'slug'

    permission_classes = (HasUserTokenPermission, CanLikeLessons)

    like_model: Union[Type[TextLessonLike], Type[VideoLessonLike]]

    def post(self, request, *args, **kwargs):
        """
        Mark a lesson as liked.
        """
        lesson = self.get_object()
        self.like_lesson(lesson, request.user)

        return Response(data={'detail': _('Successful')})

    def like_lesson(self, lesson, user):
        if not self.like_model.objects.filter(lesson=lesson, user=user).exists():
            self.like_model.objects.create(lesson=lesson, user=user)