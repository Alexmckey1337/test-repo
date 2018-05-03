from collections import OrderedDict

from django.db import connection
from django.db import models
from django.utils import timezone

from common.utils import encode_month, decode_month


class LessonQuerySet(models.query.QuerySet):
    def base_queryset(self):
        return self

    def for_user(self, user, extra_perms=True):
        if not user.is_authenticated:
            return self.none()
        if extra_perms and user.is_staff:
            return self
        if not user.hierarchy:
            return self.none()
        return self.filter(access_level__gte=user.hierarchy.level)

    def annotate_count_views_of_user(self, user, alias="count_view"):
        db_table = self.model._meta.db_table
        qs = self
        qs = qs.extra(
            select={
                alias: f"(select count(id) from {db_table}_view "
                       f"where lesson_id = {db_table}.id and user_id = %s)",
            },
            select_params=(user.pk,))
        return qs

    def annotate_total_views(self, alias="total_views"):
        db_table = self.model._meta.db_table
        qs = self
        qs = qs.extra(
            select={
                alias: f"(select count(id) from {db_table}_view "
                       f"where lesson_id = {db_table}.id)",
            })
        return qs

    def annotate_total_likes(self, alias="total_likes"):
        db_table = self.model._meta.db_table
        qs = self
        qs = qs.extra(
            select={
                alias: f"(select count(id) from {db_table}_like "
                       f"where lesson_id = {db_table}.id)",
            })
        return qs

    def annotate_unique_views(self, alias="unique_views"):
        db_table = self.model._meta.db_table
        qs = self
        qs = qs.extra(
            select={
                alias: f"(select count(distinct user_id) from {db_table}_view "
                       f"where lesson_id = {db_table}.id)",
            })
        return qs

    def annotate_unique_likes(self, alias="unique_likes"):
        db_table = self.model._meta.db_table
        qs = self
        qs = qs.extra(
            select={
                alias: f"(select count(distinct user_id) from {db_table}_like "
                       f"where lesson_id = {db_table}.id)",
            })
        return qs

    def annotate_is_liked(self, user, alias="is_liked"):
        db_table = self.model._meta.db_table
        qs = self
        qs = qs.extra(
            select={
                alias: f"exists(select id from {db_table}_like "
                       f"where lesson_id = {db_table}.id and user_id = %s)",
            },
            select_params=(user.pk,))
        return qs


class LessonManager(models.Manager):
    def get_queryset(self):
        return LessonQuerySet(self.model, using=self._db)

    def base_queryset(self):
        return self.get_queryset().base_queryset()

    def for_user(self, user, extra_perms=True):
        return self.get_queryset().for_user(user=user, extra_perms=extra_perms)

    def count_by_months(self, user):
        now = timezone.now()
        result = OrderedDict()
        if not user.is_authenticated or not user.hierarchy:
            return result
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT
                  date_part('year', published_date) y,
                  date_part('month', published_date) m,
                  count(*) count
                FROM {self.model._meta.db_table}
                WHERE (published_date <= now() AND status = 'published') and access_level <= {user.hierarchy.level}
                  group by date_part('year', published_date), date_part('month', published_date)
                order by date_part('year', published_date), date_part('month', published_date);
            """)
            tmp = list()
            for row in cursor.fetchall():
                tmp.append(((int(row[0]), int(row[1])), row[2]))
        if not tmp:
            return result
        min_month = encode_month(*tmp[0][0])
        max_month = encode_month(now.year, now.month)

        tmp = dict(tmp)
        for m in range(min_month, max_month + 1):
            month = decode_month(m)
            result[f'{month[0]}-{month[1]}'] = tmp.get(month, 0)

        return result

    def annotate_count_views_of_user(self, user, alias="count_view"):
        return self.get_queryset().annotate_count_views_of_user(user, alias=alias)

    def annotate_total_views(self, alias="total_views"):
        return self.get_queryset().annotate_total_views(alias=alias)

    def annotate_total_likes(self, alias="total_likes"):
        return self.get_queryset().annotate_total_likes(alias=alias)

    def annotate_unique_views(self, alias="unique_views"):
        return self.get_queryset().annotate_unique_views(alias=alias)

    def annotate_unique_likes(self, alias="unique_likes"):
        return self.get_queryset().annotate_unique_likes(alias=alias)

    def annotate_is_liked(self, user, alias="is_liked"):
        return self.get_queryset().annotate_is_liked(user, alias=alias)


class PublishedLessonManager(LessonManager):
    def get_queryset(self):
        from apps.lesson.models import AbstractLesson
        return super().get_queryset().filter(status=AbstractLesson.PUBLISHED, published_date__lte=timezone.now())
