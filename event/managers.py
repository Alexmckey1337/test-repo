from django.db import models
from rest_framework.compat import is_authenticated


class MeetingQuerySet(models.query.QuerySet):
    def base_queryset(self):
        return self

    def for_user(self, user):
        if not is_authenticated(user):
            return self.none()
        return self.filter(owner__in=user.get_descendants(include_self=True))


class MeetingManager(models.Manager):
    def get_queryset(self):
        return MeetingQuerySet(self.model, using=self._db)

    def base_queryset(self):
        return self.get_queryset().base_queryset()

    def for_user(self, user):
        return self.get_queryset().for_user(user=user)


class ChurchReportQuerySet(models.query.QuerySet):
    def base_queryset(self):
        return self

    def for_user(self, user):
        if not is_authenticated(user):
            return self.none()
        return self.filter(pastor__in=user.get_descendants(include_self=True))


class ChurchReportManager(models.Manager):
    def get_queryset(self):
        return ChurchReportQuerySet(self.model, using=self._db)

    def base_queryset(self):
        return self.get_queryset().base_queryset()

    def for_user(self, user):
        return self.get_queryset().for_user(user=user)
