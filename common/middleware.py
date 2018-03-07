import logging
from time import time

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from elasticsearch import Elasticsearch
from rest_framework import exceptions

from apps.account.auth_backends import CustomUserTokenAuthentication
from apps.account.models import CustomUser

logger = logging.getLogger('middleware')


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
        request.user = user

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
        request.user = user

        skin_id = request.META.get('HTTP_SKIN_ID', request.COOKIES.get('skin_id', None))
        if user and user.is_authenticated and skin_id and user.skins.filter(pk=skin_id).exists():
            try:
                request.real_user = request.user
                request.user = CustomUser.objects.get(id=skin_id)
                request.hard_user = request.user
            except ObjectDoesNotExist:
                pass


class AnalyticsMiddleware(MiddlewareMixin):
    start_time = 0
    content = ''

    def process_request(self, request):
        request.start_time = time()

    def get_content(self, request, response):
        content = {
            'duration': round(time() - request.start_time, 3),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'host': request.META.get('HTTP_HOST', ''),
            'referer': request.META.get('HTTP_REFERER', ''),
            'path': request.META.get('PATH_INFO', ''),
            'method': request.META.get('REQUEST_METHOD', ''),
            'query_params': dict(list(request.GET.lists())),
            'query_string': request.META.get('QUERY_STRING', ''),
            'status_code': response.status_code,
            'user': {'id': request.user.id, 'name': request.user.fullname},
            'timestamp': timezone.now(),
        }
        real_user = getattr(request, 'real_user', None)
        if real_user is not None:
            content['real_user'] = {'id': real_user.id, 'name': real_user.fullname}
        else:
            content['real_user'] = content['user'].copy()
        if hasattr(request, '_post'):
            content['post_params'] = dict(request._post)
        return content

    def process_response(self, request, response):
        try:
            self.content = self.get_content(request, response)
            t = time()
            es = Elasticsearch(['es'])
            es.index(index='request', doc_type='doc', body=self.content)
            logger.debug(f'{time() - t:.3f}')
            logger.debug(self.content)
        except Exception as err:
            logger.error(err)
        return response
