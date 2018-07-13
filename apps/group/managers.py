from django.db import models


class ChurchQuerySet(models.query.QuerySet):
    def base_queryset(self):
        return self

    def for_user(self, user, extra_perms=True):
        if not user.is_authenticated:
            return self.none()
        if extra_perms and (user.is_staff or user.has_operator_perm):
            return self
        return self.filter(pastor__in=user.__class__.get_tree(user))

    def has_location(self):
        return self.filter(latitude__isnull=False, longitude__isnull=False)


class ChurchManager(models.Manager):
    def get_queryset(self):
        return ChurchQuerySet(self.model, using=self._db)

    def base_queryset(self):
        return self.get_queryset().base_queryset()

    def for_user(self, user, extra_perms=True):
        return self.get_queryset().for_user(user=user, extra_perms=extra_perms)

    def has_location(self):
        return self.get_queryset().has_location()


class HomeGroupQuerySet(models.query.QuerySet):
    def base_queryset(self):
        return self

    def for_user(self, user, extra_perms=True):
        if not user.is_authenticated:
            return self.none()
        if extra_perms and (user.is_staff or user.has_operator_perm):
            return self
        return self.filter(leader__in=user.__class__.get_tree(user))

    def has_location(self):
        return self.filter(latitude__isnull=False, longitude__isnull=False)


class HomeGroupManager(models.Manager):
    def get_queryset(self):
        return HomeGroupQuerySet(self.model, using=self._db)

    def base_queryset(self):
        return self.get_queryset().base_queryset()

    def for_user(self, user, extra_perms=True):
        return self.get_queryset().for_user(user=user, extra_perms=extra_perms)

    def has_location(self):
        return self.get_queryset().has_location()
