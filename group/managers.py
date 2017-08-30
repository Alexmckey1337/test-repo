from django.db import models
from rest_framework.compat import is_authenticated


class ChurchQuerySet(models.query.QuerySet):
    def base_queryset(self):
        return self

    def for_user(self, user):
        if not is_authenticated(user):
            return self.none()
        if user.is_staff:
            return self
        return self.filter(pastor__in=user.__class__.get_tree(user))


class ChurchManager(models.Manager):
    def get_queryset(self):
        return ChurchQuerySet(self.model, using=self._db)

    def base_queryset(self):
        return self.get_queryset().base_queryset()

    def for_user(self, user):
        return self.get_queryset().for_user(user=user)


class HomeGroupQuerySet(models.query.QuerySet):
    def base_queryset(self):
        return self

    def for_user(self, user):
        if not is_authenticated(user):
            return self.none()
        if user.is_staff:
            return self
        return self.filter(leader__in=user.__class__.get_tree(user))


class HomeGroupManager(models.Manager):
    def get_queryset(self):
        return HomeGroupQuerySet(self.model, using=self._db)

    def base_queryset(self):
        return self.get_queryset().base_queryset()

    def for_user(self, user):
        return self.get_queryset().for_user(user=user)
