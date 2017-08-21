from django.contrib.auth.models import UserManager
from mptt.managers import TreeManager
from mptt.querysets import TreeQuerySet
from rest_framework.compat import is_authenticated


class CustomUserQuerySet(TreeQuerySet):
    def base_queryset(self):
        return self

    def for_user(self, user):
        if not is_authenticated(user):
            return self.none()
        if user.is_staff:
            return self
        if not user.hierarchy:
            return self.none()
        return user.get_descendants(include_self=True).select_related(
            'hierarchy', 'master__hierarchy').prefetch_related(
            'divisions', 'departments'
        ).filter(is_active=True)


class CustomUserManager(TreeManager, UserManager):
    use_in_migrations = False

    def get_queryset(self):
        return CustomUserQuerySet(self.model, using=self._db)

    def base_queryset(self):
        return self.get_queryset().base_queryset()

    def for_user(self, user):
        return self.get_queryset().for_user(user=user)