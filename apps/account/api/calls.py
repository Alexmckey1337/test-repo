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

    if _range == 'last_3':
        q = [
                {
                     "call_date": "‎2017-10-29",
                     "src": "1117",
                     "type": "out",
                     "lastapp": "Dial",
                     "dst": "‎0687774566",
                     "record": "out-0687774566-1117-20171029-184437-1509295476.928.wav",
                     "disposition": "ANSWERED",
                     "billsec": 93
                 },
                 {
                     "call_date": "‎2017-10-28",
                     "src": "1101",
                     "type": "out",
                     "lastapp": "Dial",
                     "dst": "‎0687774566",
                     "record": "out-0687774566-1101-20171028-142304-1509189784.239.wav",
                     "disposition": "ANSWERED",
                     "billsec": 22
                 },
                 {
                     "call_date": "‎2017-10-23",
                     "src": "1119",
                     "type": "out",
                     "lastapp": "Dial",
                     "dst": "‎0687774566",
                     "record": "out-0687774566-1119-20171023-133344-1508754824.286.wav",
                     "disposition": "ANSWERED",
                     "billsec": 53
                 },
        ]

    if _range == 'month':
        q = [
                {
                    "disposition": "NO ANSWER",
                    "type": "out",
                    "lastapp": "Dial",
                    "billsec": 0,
                    "dst": "‎0687774566",
                    "call_date": "‎2017-11-11",
                    "record": "out-0687774566-1117-20171111-185323-1510419203.6906.wav",
                    "src": "1117"
                },
                {
                    "disposition": "NO ANSWER",
                    "type": "out",
                    "lastapp": "Dial",
                    "billsec": 0,
                    "dst": "‎0687774566",
                    "call_date": "‎2017-11-11",
                    "record": "out-0687774566-1117-20171111-185253-1510419173.6903.wav",
                    "src": "1117"
                },
                {
                    "disposition": "NO ANSWER",
                    "type": "out",
                    "lastapp": "Dial",
                    "billsec": 0,
                    "dst": "‎0687774566",
                    "call_date": "‎2017-11-11",
                    "record": "out-0687774566-1117-20171111-172233-1510413753.6664.wav",
                    "src": "1117"
                },
                {
                    "disposition": "ANSWERED",
                    "type": "out",
                    "lastapp": "Dial",
                    "billsec": 44,
                    "dst": "‎+380687774566",
                    "call_date": "‎2017-11-06",
                    "record": "out-+380687774566-1105-20171106-161347-1509977627.1053.wav",
                    "src": "1105"
                },
                {
                    "disposition": "ANSWERED",
                    "type": "out",
                    "lastapp": "Dial",
                    "billsec": 30,
                    "dst": "‎+380687774566",
                    "call_date": "‎2017-11-06",
                    "record": "out-+380687774566-1105-20171106-160601-1509977161.1051.wav",
                    "src": "1105"
                },
                {
                    "disposition": "ANSWERED",
                    "type": "out",
                    "lastapp": "Dial",
                    "billsec": 61,
                    "dst": "‎+380687774566",
                    "call_date": "‎2017-11-06",
                    "record": "out-+380687774566-1105-20171106-155701-1509976621.1049.wav",
                    "src": "1105"
                },
                {
                    "disposition": "BUSY",
                    "type": "out",
                    "lastapp": "Busy",
                    "billsec": 0,
                    "dst": "‎+380687774566",
                    "call_date": "‎2017-11-06",
                    "record": "out-+380687774566-1105-20171106-155609-1509976569.1046.wav",
                    "src": "1105"
                },
                {
                    "disposition": "ANSWERED",
                    "type": "out",
                    "lastapp": "Dial",
                    "billsec": 11,
                    "dst": "‎0687774566",
                    "call_date": "‎2017-11-02",
                    "record": "out-0687774566-1117-20171102-132417-1509621857.7619.wav",
                    "src": "1117"
                },
                {
                    "disposition": "ANSWERED",
                    "type": "out",
                    "lastapp": "Dial",
                    "billsec": 2,
                    "dst": "‎0687774566",
                    "call_date": "‎2017-11-02",
                    "record": "out-0687774566-1117-20171102-132314-1509621794.7604.wav",
                    "src": "1117"
                }
            ]

    return Response(q)

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
