from django.utils.translation import ugettext_lazy as _
from rest_framework import mixins
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.lesson.api.filters import FilterLessonsByMonth, FilterLessonsByViews, FilterLessonsByLikes
from apps.lesson.api.permissions import CanSeeLessonMonths, CanSeeLessons, CanLikeLessons
from common import filters


class MonthListMixin(GenericAPIView):
    permission_classes = (IsAuthenticated, CanSeeLessonMonths)
    pagination_class = None
    model = None

    def get(self, request, *args, **kwargs):
        return Response(data=self.model.objects.count_by_months(request.user))


class LessonObjectMixin(GenericAPIView):
    model = None
    lesson = None

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


class LessonDetailMixin(mixins.RetrieveModelMixin, LessonObjectMixin):
    lookup_field = 'slug'

    permission_classes = (IsAuthenticated, CanSeeLessons)

    def get(self, request, *args, **kwargs):
        responsible = self.retrieve(request, *args, **kwargs)
        self.model.views.through.objects.create(lesson=self.lesson, user=request.user)
        return responsible


class LessonLikeMixin(LessonObjectMixin):
    lookup_field = 'slug'

    permission_classes = (IsAuthenticated, CanLikeLessons)

    like_model = None

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


class LessonListMixin(mixins.ListModelMixin, GenericAPIView):
    model = None

    permission_classes = (IsAuthenticated, CanSeeLessons)

    filter_backends = (
        filters.FieldSearchFilter,
        FilterLessonsByMonth,
        FilterLessonsByViews,
        FilterLessonsByLikes,
    )
    field_search_fields = {
        'search_title': ('title',),
    }

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        qs = self.model.published.for_user(self.request.user)
        qs = qs.annotate_count_views_of_user(self.request.user)
        qs = qs.annotate_total_views()
        qs = qs.annotate_total_likes()
        qs = qs.annotate_unique_views()
        qs = qs.annotate_unique_likes()
        qs = qs.annotate_is_liked(self.request.user)
        return qs

    def paginate_queryset(self, queryset):
        if self.request.query_params.get('without_pagination', None) is not None:
            return None
        return super().paginate_queryset(queryset)