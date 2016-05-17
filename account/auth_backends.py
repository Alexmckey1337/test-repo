# -*- coding: utf-8
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ImproperlyConfigured
from models import CustomUser


class CustomUserModelBackend(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            user = self.user_class.objects.get(username=username)
            if user.check_password(password):
                return user
        except self.user_class.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return self.user_class.objects.get(pk=user_id)
        except self.user_class.DoesNotExist:
            return None

    @property
    def user_class(self):
        if not hasattr(self, '_user_class'):
            self._user_class = CustomUser
            if not self._user_class:
                raise ImproperlyConfigured('Could not get custom user model')
        return self._user_class

