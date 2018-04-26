from rest_framework import mixins
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.lesson.api.filters import FilterLessonsByMonth, FilterLessonsByViews, FilterLessonsByLikes
from apps.lesson.api.permissions import CanSeeLessonMonths, CanSeeLessons
from apps.lesson.api.serializers import TextLessonListSerializer, VideoLessonListSerializer, \
    VideoLessonDetailSerializer, TextLessonDetailSerializer
from apps.lesson.models import TextLesson, VideoLesson
from common import filters


class MonthListMixin(GenericAPIView):
    permission_classes = (IsAuthenticated, CanSeeLessonMonths)
    pagination_class = None
    model = None

    def get(self, request, *args, **kwargs):
        return Response(data=self.model.objects.count_by_months())


class LessonDetailMixin(mixins.RetrieveModelMixin, GenericAPIView):
    model = None
    obj = None
    lookup_field = 'slug'

    permission_classes = (IsAuthenticated, CanSeeLessons)

    def get(self, request, *args, **kwargs):
        responsible = self.retrieve(request, *args, **kwargs)
        self.model.views.through.objects.create(lesson=self.obj, user=request.user)
        return responsible

    def get_queryset(self):
        qs = self.model.published.all()
        qs = qs.annotate_count_views_of_user(self.request.user)
        qs = qs.annotate_total_views()
        qs = qs.annotate_total_likes()
        qs = qs.annotate_unique_views()
        qs = qs.annotate_unique_likes()
        qs = qs.annotate_is_liked(self.request.user)
        return qs

    def get_object(self):
        self.obj = super().get_object()
        return self.obj


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
        qs = self.model.published.all()
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
