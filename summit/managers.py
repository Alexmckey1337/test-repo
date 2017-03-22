from django.conf import settings
from django.db import models
from rest_framework.compat import is_authenticated


class AnketQuerySet(models.query.QuerySet):
    def base_queryset(self):
        return self.select_related(
            'user', 'user__hierarchy', 'user__master', 'summit', 'summit__type'). \
            prefetch_related('user__divisions', 'user__departments', 'emails')

    def for_user(self, user):
        if not is_authenticated(user) or not hasattr(user, 'partnership'):
            return self.none()
        summit_ids = set(user.summit_ankets.filter(
            role__gte=settings.SUMMIT_ANKET_ROLES['consultant']).values_list('summit_id', flat=True))
        return self.filter(summit__in=summit_ids)


class AnketManager(models.Manager):
    def get_queryset(self):
        return AnketQuerySet(self.model, using=self._db)

    def base_queryset(self):
        return self.get_queryset().base_queryset()

    def for_user(self, user):
        return self.get_queryset().for_user(user=user)
