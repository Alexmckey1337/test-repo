# -*- coding: utf-8
from rest_framework.decorators import api_view
from django.core.exceptions import ObjectDoesNotExist
from apps.account.models import CustomUser as User
from datetime import datetime
import json
import requests
from rest_framework.response import Response
from rest_framework import status, exceptions
from django.conf import settings
from django.shortcuts import get_object_or_404


class ServiceUnavailable(exceptions.APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'Service temporarily unavailable, try again later.'
    default_code = 'service_unavailable'


def request_to_asterisk(data, url):
    try:
        user_calls = requests.get(settings.ASTERISK_SERVICE_ADDRESS + url, data=json.dumps(data),
                                  headers={'Content-Type': 'application/json'})
    except Exception as e:
        print(e)
        raise ServiceUnavailable({'detail': 'Asterisk Service temporarily unavailable, try again later'})

    try:
        user_calls = user_calls.json()
    except Exception as e:
        print(e)
        raise ServiceUnavailable({"detail": "Can't parse Asterisk Service response"})

    return user_calls


def prepare_calls_data(user_calls):
    try:
        for call in enumerate(user_calls):
            user_calls[call[0]] = {
                'call_date': call[1][0],
                'src': call[1][4].split('-')[2],
                'dst': call[1][4].split('-')[1],
                'lastapp': call[1][1],
                'billsec': call[1][2],
                'disposition': call[1][3],
                'record': call[1][4],
                'type': call[1][4].split('-')[0]
            }
    except Exception as e:
        print(e)
        raise ServiceUnavailable(
            {"detail": "Can't prepare data to response."}
        )

    return user_calls


def prepare_asterisk_users(users):
    for x in enumerate(users):
        users[x[0]] = {
            'user': x[1]
        }
    return users


@api_view(['GET'])
def calls_to_user(request):
    data = dict()
    try:
        user = User.objects.get(id=request.query_params.get('user_id'))
    except ObjectDoesNotExist:
        raise exceptions.ValidationError({'message': 'Parameter {user_id} must be passed'})

    phone_number = user.phone_number[-10:]
    if not phone_number:
        raise exceptions.ValidationError({'message': 'This user not have a {phone_number}'})

    _range = request.query_params.get('range')
    if not _range or (_range not in ['last_3', 'month']):
        raise exceptions.ValidationError(
            {'message': 'Invalid {range} parameter or parameter not passed.'})

    month_date = request.query_params.get('month_date', datetime.now().date().strftime('%Y-%m'))
    if _range == 'month' and not month_date:
        raise exceptions.ValidationError({'message': 'Parameter {month_date} must be passed'})

    data['phone_number'] = phone_number
    data['range'] = _range
    data['month_date'] = month_date
    data['query_type'] = 'user'

    user_calls = request_to_asterisk(data, url='/calls')

    calls_data = prepare_calls_data(user_calls)

    return Response(calls_data, status=status.HTTP_200_OK)


@api_view(['GET'])
def all_calls(request):
    data = request.query_params

    users_calls = request_to_asterisk(data, url='/calls')

    calls_data = prepare_calls_data(users_calls)

    pages_count = (len(calls_data) // 30) + 1
    page = int(request.query_params.get('page') or 1)
    page_from = 30 * (page - 1)
    page_to = page_from + 30

    result = {
        'pages': pages_count,
        'calls_data': calls_data[page_from:page_to]
    }

    return Response(result, status=status.HTTP_200_OK)


@api_view(['GET'])
def asterisk_users(request):
    users = request_to_asterisk(data=None, url='/users')
    users = prepare_asterisk_users(users)

    return Response(users, status=status.HTTP_200_OK)


@api_view(['POST'])
def asterisk_name_change(request):
    data = {}
    extension = request.data.get('internal_number')
    user = get_object_or_404(User, pk=request.data.get('id'))
    fullname = user.fullname

    data['extension'] = exception

    try:
        user_calls = requests.post(settings.ASTERISK_SERVICE_ADDRESS + '/change_user', data=json.dumps(data),
                                  headers={'Content-Type': 'application/json'})
    except Exception as e:
        print(e)
        raise ServiceUnavailable({'detail': 'Asterisk Service temporarily unavailable, try again later'})


@api_view(['GET'])
def users_without_calls(request):
    pass
