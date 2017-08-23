from django.contrib.auth.models import UserManager
from rest_framework.compat import is_authenticated
from treebeard.mp_tree import MP_NodeQuerySet


class CustomUserQuerySet(MP_NodeQuerySet):
    def base_queryset(self):
        return self

    def for_user(self, user):
        if not is_authenticated(user):
            return self.none()
        if user.is_staff:
            return self
        if not user.hierarchy:
            return self.none()
        return user.__class__.get_tree(user).select_related(
            'hierarchy', 'master__hierarchy').prefetch_related(
            'divisions', 'departments'
        ).filter(is_active=True)

    def for_user_update(self, user):
        if not is_authenticated(user):
            return self.none()
        if user.is_staff:
            return self
        if not user.hierarchy:
            return self.none()
        return self


class CustomUserManager(UserManager):
    use_in_migrations = False

    def get_queryset(self):
        return CustomUserQuerySet(self.model, using=self._db).order_by('path')

    def base_queryset(self):
        return self.get_queryset().base_queryset()

    def for_user(self, user):
        return self.get_queryset().for_user(user=user)

    def for_user_update(self, user):
        return self.get_queryset().for_user(user=user)
