import coreapi
import coreschema
from rest_framework import filters


class FilterLessonsByMonth(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        month = request.query_params.get('month', '')
        if month:
            queryset = queryset.extra(where=["to_char(published_date, 'YYYY-MM') = %s"], params=(month,))
        return queryset

    def get_schema_fields(self, view):
        return [
            coreapi.Field(
                name="month",
                required=False,
                location='query',
                schema=coreschema.String(
                    title='Month of lesson',
                    description="Month of the lesson in format 'YYYY-MM'",
                    pattern=r'^\d{4}-(0[1-9]|10|11|12)$'
                )
            )
        ]


class FilterLessonsByViews(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        is_viewed = request.query_params.get('is_viewed', '')
        if is_viewed.upper() in ('TRUE', 'T', 'YES', 'Y', 'ON', '1'):
            queryset = queryset.extra(
                where=[f"(select count(id) from {view.model._meta.db_table}_view "
                       f"where lesson_id = {view.model._meta.db_table}.id and user_id = %s) > 0"],
                params=(request.user.pk,))
        if is_viewed.upper() in ('FALSE', 'F', 'NO', 'N', 'OFF', '0'):
            queryset = queryset.extra(
                where=[f"(select count(id) from {view.model._meta.db_table}_view "
                       f"where lesson_id = {view.model._meta.db_table}.id and user_id = %s) = 0"],
                params=(request.user.pk,))
        return queryset

    def get_schema_fields(self, view):
        return [
            coreapi.Field(
                name="is_viewed",
                required=False,
                location='query',
                schema=coreschema.Boolean(
                    title='Viewed of lesson',
                    description="The user has seen the lesson or not"
                )
            )
        ]


class FilterLessonsByLikes(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        is_liked = request.query_params.get('is_liked', '')
        if is_liked.upper() in ('TRUE', 'T', 'YES', 'Y', 'ON', '1'):
            queryset = queryset.extra(
                where=[f"exists(select id from {view.model._meta.db_table}_like "
                       f"where lesson_id = {view.model._meta.db_table}.id and user_id = %s)"],
                params=(request.user.pk,))
        if is_liked.upper() in ('FALSE', 'F', 'NO', 'N', 'OFF', '0'):
            queryset = queryset.extra(
                where=[f"not exists(select id from {view.model._meta.db_table}_like "
                       f"where lesson_id = {view.model._meta.db_table}.id and user_id = %s)"],
                params=(request.user.pk,))
        return queryset

    def get_schema_fields(self, view):
        return [
            coreapi.Field(
                name="is_liked",
                required=False,
                location='query',
                schema=coreschema.Boolean(
                    title='Liked of lesson',
                    description="Liked the user lesson or not"
                )
            )
        ]
