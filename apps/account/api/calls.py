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


class ServiceUnavailable(exceptions.APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'Service temporarily unavailable, try again later.'
    default_code = 'service_unavailable'


def request_to_asterisk(data):
    try:
        user_calls = requests.get(settings.ASTERISK_SERVICE_ADDRESS + '/calls', data=json.dumps(data),
                                  headers={'Content-Type': 'application/json'})
    except Exception:
        raise ServiceUnavailable({'detail': 'Asterisk Service temporarily unavailable, try again later'})

    try:
        user_calls = user_calls.json()
    except Exception:
        raise ServiceUnavailable({"message": "Can't parse Asterisk Service response"})

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
    except Exception:
        return ServiceUnavailable(
            {"detail": "Can't prepare data to response. Most likely this conversation has no record."}
        )

    return user_calls


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

    user_calls = request_to_asterisk(data)

    calls_data = prepare_calls_data(user_calls)

    return Response(calls_data, status=status.HTTP_200_OK)


@api_view(['GET'])
def all_calls(request):
    data = request.query_params

    users_calls = request_to_asterisk(data)

    calls_data = prepare_calls_data(users_calls)

    return Response(calls_data)


@api_view(['GET'])
def users_without_calls(request):
    pass
