from django.core.exceptions import ObjectDoesNotExist
from django.utils.deprecation import MiddlewareMixin
from rest_framework import exceptions

from apps.account.auth_backends import CustomUserTokenAuthentication
from apps.account.models import CustomUser


class RestAuthMiddlewareMixin:
    def get_user(self, request):
        user = request.user
        return user if not user.is_anonymous else self.auth_by_key(request) or user

    def auth_by_key(self, request):
        key = request.META.get('HTTP_AUTHORIZATION', '').replace('Token ', '')
        if not key:
            return None
        try:
            return CustomUserTokenAuthentication().authenticate_credentials(key=key)[0]
        except exceptions.AuthenticationFailed:
            return None


class HardAuthenticationMiddleware(MiddlewareMixin, RestAuthMiddlewareMixin):
    def process_request(self, request):
        user = self.get_user(request)

        if user and user.is_superuser:
            hard_user_id = request.COOKIES.get('hard_user_id', None)
            if hard_user_id is not None:
                try:
                    request.real_user = user
                    request.user = CustomUser.objects.get(id=hard_user_id)
                    request.hard_user = request.user
                except ObjectDoesNotExist:
                    pass


class ManagerAuthenticationMiddleware(MiddlewareMixin, RestAuthMiddlewareMixin):
    def process_request(self, request):
        user = self.get_user(request)

        skin_id = request.META.get('HTTP_SKIN_ID', request.COOKIES.get('skin_id', None))
        if user and user.is_authenticated and skin_id and user.skins.filter(pk=skin_id).exists():
            try:
                request.real_user = request.user
                request.user = CustomUser.objects.get(id=skin_id)
                request.hard_user = request.user
            except ObjectDoesNotExist:
                pass
