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
        q = {'result': [
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
        ]}

    if _range == 'month':
        q = {'result' : [
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
            ]}

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

    q = {
    "pages": 4,
    "result": [
        {
            "call_date": "2017-12-13",
            "dst": "0936235312",
            "src": "1104",
            "billsec": 680,
            "disposition": "ANSWERED",
            "lastapp": "Dial",
            "record": "out-0936235312-1104-20171213-124409-1513161849.259.wav",
            "type": "out"
        },
        {
            "call_date": "2017-12-12",
            "dst": "380936327738",
            "src": "1104",
            "billsec": 2,
            "disposition": "ANSWERED",
            "lastapp": "Dial",
            "record": "out-380936327738-1104-20171212-202705-1513103225.2534.wav",
            "type": "out"
        },
        {
            "call_date": "2017-12-12",
            "dst": "0930553037",
            "src": "1104",
            "billsec": 126,
            "disposition": "ANSWERED",
            "lastapp": "Dial",
            "record": "out-0930553037-1104-20171212-194908-1513100948.2320.wav",
            "type": "out"
        },
        {
            "call_date": "2017-12-12",
            "dst": "380936021562",
            "src": "1104",
            "billsec": 186,
            "disposition": "ANSWERED",
            "lastapp": "Dial",
            "record": "out-380936021562-1104-20171212-193135-1513099895.2266.wav",
            "type": "out"
        },
        {
            "call_date": "2017-12-12",
            "dst": "0937004966",
            "src": "1104",
            "billsec": 233,
            "disposition": "ANSWERED",
            "lastapp": "Dial",
            "record": "out-0937004966-1104-20171212-132718-1513078038.1314.wav",
            "type": "out"
        },
        {
            "call_date": "2017-12-11",
            "dst": "380932562713",
            "src": "1104",
            "billsec": 483,
            "disposition": "ANSWERED",
            "lastapp": "Dial",
            "record": "out-380932562713-1104-20171211-193755-1513013875.701.wav",
            "type": "out"
        },
        {
            "call_date": "2017-12-11",
            "dst": "+380934098574",
            "src": "1104",
            "billsec": 189,
            "disposition": "ANSWERED",
            "lastapp": "Dial",
            "record": "out-+380934098574-1104-20171211-150648-1512997608.464.wav",
            "type": "out"
        },
        {
            "call_date": "2017-12-02",
            "dst": "0936235312",
            "src": "1104",
            "billsec": 110,
            "disposition": "ANSWERED",
            "lastapp": "Dial",
            "record": "out-0936235312-1104-20171202-174333-1512229413.5646.wav",
            "type": "out"
        },
        {
            "call_date": "2017-12-01",
            "dst": "380933265117",
            "src": "1104",
            "billsec": 563,
            "disposition": "ANSWERED",
            "lastapp": "Dial",
            "record": "out-380933265117-1104-20171201-163419-1512138859.3690.wav",
            "type": "out"
        },
        {
            "call_date": "2017-11-30",
            "dst": "380937307339",
            "src": "1104",
            "billsec": 711,
            "disposition": "ANSWERED",
            "lastapp": "Dial",
            "record": "out-380937307339-1104-20171130-173411-1512056051.1708.wav",
            "type": "out"
        },
        {
            "call_date": "2017-11-30",
            "dst": "380933654043",
            "src": "1104",
            "billsec": 5,
            "disposition": "ANSWERED",
            "lastapp": "Dial",
            "record": "out-380933654043-1104-20171130-142820-1512044900.747.wav",
            "type": "out"
        },
        {
            "call_date": "2017-11-30",
            "dst": "380931957041",
            "src": "1104",
            "billsec": 249,
            "disposition": "ANSWERED",
            "lastapp": "Dial",
            "record": "out-380931957041-1104-20171130-142337-1512044617.723.wav",
            "type": "out"
        },
        {
            "call_date": "2017-11-29",
            "dst": "0936235312",
            "src": "1104",
            "billsec": 9,
            "disposition": "ANSWERED",
            "lastapp": "Dial",
            "record": "out-0936235312-1104-20171129-125448-1511952888.29475.wav",
            "type": "out"
        },
        {
            "call_date": "2017-11-25",
            "dst": "0930962130",
            "src": "1104",
            "billsec": 2,
            "disposition": "ANSWERED",
            "lastapp": "Dial",
            "record": "out-0930962130-1104-20171125-184459-1511628299.24405.wav",
            "type": "out"
        },
        {
            "call_date": "2017-11-25",
            "dst": "+380930532453",
            "src": "1104",
            "billsec": 89,
            "disposition": "ANSWERED",
            "lastapp": "Dial",
            "record": "out-+380930532453-1104-20171125-142234-1511612554.23368.wav",
            "type": "out"
        },
        {
            "call_date": "2017-11-24",
            "dst": "380934098574",
            "src": "1104",
            "billsec": 40,
            "disposition": "ANSWERED",
            "lastapp": "Dial",
            "record": "out-380934098574-1104-20171124-182730-1511540850.22956.wav",
            "type": "out"
        },
        {
            "call_date": "2017-11-24",
            "dst": "380932232337",
            "src": "1104",
            "billsec": 367,
            "disposition": "ANSWERED",
            "lastapp": "Dial",
            "record": "out-380932232337-1104-20171124-121558-1511518558.21084.wav",
            "type": "out"
        },
        {
            "call_date": "2017-11-17",
            "dst": "0936235312",
            "src": "1104",
            "billsec": 92,
            "disposition": "ANSWERED",
            "lastapp": "Dial",
            "record": "out-0936235312-1104-20171117-143135-1510921895.12327.wav",
            "type": "out"
        },
        {
            "call_date": "2017-11-13",
            "dst": "380984093019",
            "src": "1104",
            "billsec": 5,
            "disposition": "ANSWERED",
            "lastapp": "Dial",
            "record": "out-380984093019-1104-20171113-205527-1510599327.9238.wav",
            "type": "out"
        },
        {
            "call_date": "2017-11-13",
            "dst": "380934893295",
            "src": "1104",
            "billsec": 44,
            "disposition": "ANSWERED",
            "lastapp": "Dial",
            "record": "out-380934893295-1104-20171113-202204-1510597324.9106.wav",
            "type": "out"
        },
        {
            "call_date": "2017-11-13",
            "dst": "0932562713",
            "src": "1104",
            "billsec": 349,
            "disposition": "ANSWERED",
            "lastapp": "Dial",
            "record": "out-0932562713-1104-20171113-193328-1510594408.8970.wav",
            "type": "out"
        },
        {
            "call_date": "2017-11-13",
            "dst": "380937454545",
            "src": "1104",
            "billsec": 296,
            "disposition": "ANSWERED",
            "lastapp": "Dial",
            "record": "out-380937454545-1104-20171113-171441-1510586081.8389.wav",
            "type": "out"
        },
        {
            "call_date": "2017-11-13",
            "dst": "+380939083078",
            "src": "1104",
            "billsec": 62,
            "disposition": "ANSWERED",
            "lastapp": "Dial",
            "record": "out-+380939083078-1104-20171113-164726-1510584446.8246.wav",
            "type": "out"
        },
        {
            "call_date": "2017-11-13",
            "dst": "+380938422872",
            "src": "1104",
            "billsec": 117,
            "disposition": "ANSWERED",
            "lastapp": "Dial",
            "record": "out-+380938422872-1104-20171113-132445-1510572285.7641.wav",
            "type": "out"
        },
        {
            "call_date": "2017-11-13",
            "dst": "0938422872",
            "src": "1104",
            "billsec": 329,
            "disposition": "ANSWERED",
            "lastapp": "Dial",
            "record": "out-0938422872-1104-20171113-131653-1510571813.7588.wav",
            "type": "out"
        },
        {
            "call_date": "2017-11-13",
            "dst": "+380939406685",
            "src": "1104",
            "billsec": 313,
            "disposition": "ANSWERED",
            "lastapp": "Dial",
            "record": "out-+380939406685-1104-20171113-130850-1510571330.7553.wav",
            "type": "out"
        },
        {
            "call_date": "2017-11-13",
            "dst": "0933786818",
            "src": "1104",
            "billsec": 238,
            "disposition": "ANSWERED",
            "lastapp": "Dial",
            "record": "out-0933786818-1104-20171113-113534-1510565734.7237.wav",
            "type": "out"
        },
        {
            "call_date": "2017-11-11",
            "dst": "380930376692",
            "src": "1104",
            "billsec": 129,
            "disposition": "ANSWERED",
            "lastapp": "Dial",
            "record": "out-380930376692-1104-20171111-205758-1510426678.7105.wav",
            "type": "out"
        },
        {
            "call_date": "2017-11-11",
            "dst": "380939037106",
            "src": "1104",
            "billsec": 129,
            "disposition": "ANSWERED",
            "lastapp": "Dial",
            "record": "out-380939037106-1104-20171111-203745-1510425465.7079.wav",
            "type": "out"
        },
        {
            "call_date": "2017-11-11",
            "dst": "+380934173662",
            "src": "1104",
            "billsec": 2,
            "disposition": "ANSWERED",
            "lastapp": "Dial",
            "record": "out-+380934173662-1104-20171111-195918-1510423158.7055.wav",
            "type": "out"
        }
    ]
}


    return Response(q)

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
    q = [
            {
                "fullname": None,
                "extension": "1101"
            },
            {
                "fullname": None,
                "extension": "1201"
            },
            {
                "fullname": None,
                "extension": "1205"
            },
            {
                "fullname": None,
                "extension": "4001"
            },
            {
                "fullname": None,
                "extension": "4002"
            },
            {
                "fullname": None,
                "extension": "4003"
            },
            {
                "fullname": None,
                "extension": "1206"
            },
            {
                "fullname": None,
                "extension": "1124"
            },
            {
                "fullname": None,
                "extension": "1106"
            },
            {
                "fullname": None,
                "extension": "1112"
            },
            {
                "fullname": None,
                "extension": "9001"
            },
            {
                "fullname": None,
                "extension": "1210"
            },
            {
                "fullname": "Пионтковский Ростислав ",
                "extension": "4010"
            },
            {
                "fullname": None,
                "extension": "4011"
            },
            {
                "fullname": "Пионтковский Ростислав ",
                "extension": "2001"
            },
            {
                "fullname": None,
                "extension": "1104"
            },
            {
                "fullname": None,
                "extension": "1111"
            },
            {
                "fullname": None,
                "extension": "1125"
            },
            {
                "fullname": None,
                "extension": "9000"
            },
            {
                "fullname": "Пионтковский Ростислав ",
                "extension": "9002"
            },
            {
                "fullname": None,
                "extension": "2568"
            },

        ]
    return Response(q)
    users = request_to_asterisk(data=None, url='/users')
    users = prepare_asterisk_users(users)

    result = {'result': users}

    return Response(result, status=status.HTTP_200_OK)


@api_view(['POST'])
def change_asterisk_user(request):
    data = {}
    return Response({'message': 'GOOD JOB!', 'data': '%s' % request.data })
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
