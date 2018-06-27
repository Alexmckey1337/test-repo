import requests
from django.conf import settings
from rest_framework import exceptions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.summit.api.permissions import HasSummitEntryPerm

perm_classes = (IsAuthenticated, HasSummitEntryPerm)


class ServiceUnavailable(exceptions.APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'Service temporarily unavailable, try again later.'
    default_code = 'service_unavailable'


def response_to_entry_service(url):
    host = settings.ENTRY_SERVICE_HOST
    print(f'http://{host}{url}')
    try:
        response = requests.post(
            f'http://{host}{url}', timeout=5,
            headers={'Content-Type': 'application/json', 'Crm-Token': settings.PALACE_TOKEN})
    except Exception as e:
        print(e)
        raise ServiceUnavailable(
            {'detail': 'Service temporarily unavailable, try again later'})
    if response.status_code == 200:
        return response.json()
    else:
        raise ServiceUnavailable(
            {'detail': 'Service temporarily unavailable, try again later'})


class EntryMixin(APIView):
    permission_classes = (IsAuthenticated, HasSummitEntryPerm)
    url = ''

    def post(self, request, *args, **kwargs):
        result = response_to_entry_service(self.url.format(code=kwargs.get('code')))
        return Response(result)


class ResetEntryView(EntryMixin):
    url = '/user/{code}/reset_entry'
    # def post(self, request, *args, **kwargs):
    #     code = kwargs.get('code')
    #     result = response_to_entry_service(f'/user/{code}/reset_entry')
    #     return Response(result)


class ResetAllEntriesView(EntryMixin):
    url = '/entries/reset'


class ResetAllCodesView(EntryMixin):
    url = '/reset'


class FinishLessonView(EntryMixin):
    url = '/lesson/finish'


class StartLessonView(EntryMixin):
    url = '/lesson/start'


class BlockUserView(EntryMixin):
    url = '/user/{code}/block'


class UnblockUserView(EntryMixin):
    url = '/user/{code}/unblock'



@permission_classes(perm_classes)
@api_view(['POST'])
def reset_entry(request, code=''):
    result = response_to_entry_service(f'/user/{code}/reset_entry')
    return Response(result)


@permission_classes(perm_classes)
@api_view(['POST'])
def reset_all_entries(request):
    result = response_to_entry_service('/entries/reset')
    return Response(result)


@permission_classes(perm_classes)
@api_view(['POST'])
def reset_all_codes(request):
    result = response_to_entry_service('/reset')
    return Response(result)


@permission_classes(perm_classes)
@api_view(['POST'])
def multi_entry(request):
    result = response_to_entry_service('/lesson/finish')
    return Response(result)


@permission_classes(perm_classes)
@api_view(['POST'])
def one_entry(request):
    result = response_to_entry_service('/lesson/start')
    return Response(result)


@permission_classes(perm_classes)
@api_view(['POST'])
def block_user(request, code=''):
    result = response_to_entry_service(f'/user/{code}/block')
    return Response(result)


@permission_classes(perm_classes)
@api_view(['POST'])
def unblock_user(request, code=''):
    result = response_to_entry_service(f'/user/{code}/unblock')
    return Response(result)
