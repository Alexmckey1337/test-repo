from django.core.exceptions import ObjectDoesNotExist
from django.utils.deprecation import MiddlewareMixin

from account.models import CustomUser


class HardAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user and request.user.is_superuser:
            hard_user_id = request.COOKIES.get('hard_user_id', None)
            if hard_user_id is not None:
                try:
                    request.real_user = request.user
                    request.user = CustomUser.objects.get(id=hard_user_id)
                    request.hard_user = request.user
                except ObjectDoesNotExist:
                    pass


class ManagerAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        skin_id = request.COOKIES.get('skin_id', None)
        user = request.user
        if user and user.is_authenticated and skin_id and user.skins.filter(pk=skin_id).exists():
            try:
                request.real_user = request.user
                request.user = CustomUser.objects.get(id=skin_id)
                request.hard_user = request.user
            except ObjectDoesNotExist:
                pass
