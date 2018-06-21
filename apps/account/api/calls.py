import time
import json
import requests
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from apps.account.models import CustomUser as User
from rest_framework.response import Response
from rest_framework import status, exceptions
from django.conf import settings
from django.shortcuts import get_object_or_404

from common.performance import func_time


class ServiceUnavailable(exceptions.APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'Asterisk service temporarily unavailable, try again later.'
    default_code = 'service_unavailable'


def request_to_asterisk(data, url):
    # TODO bad code
    # i am sorry -- start
    data = dict(data) if data else {}
    from_duration = data.get('from_duration')
    to_duration = data.get('to_duration')
    from_date = data.get('from_date')
    to_date = data.get('to_date')
    if from_duration is not None:
        data['duration_from'] = from_duration
        del data['from_duration']
    if to_duration is not None:
        data['duration_to'] = to_duration
        del data['to_duration']
    if from_date is not None:
        data['date_from'] = from_date
        del data['from_date']
    if to_date is not None:
        data['date_to'] = to_date
        del data['to_date']
    # i am sorry -- end

    s = time.time()
    try:
        response = requests.get(settings.ASTERISK_SERVICE_ADDRESS + url,
                                params=data, json=data, timeout=5,
                                headers={'Content-Type': 'application/json'})
    except Exception as e:
        print(e)
        raise ServiceUnavailable(
            {'detail': 'Asterisk Service temporarily unavailable, try again later'})
    finally:
        print("[{:.3f}] asterisk time".format(time.time() - s))

    return response


def prepare_calls_data(data):
    try:
        for call in enumerate(data):
            data[call[0]] = {
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

    return data


def prepare_asterisk_users(users):
    for x in enumerate(users):
        try:
            user_id = x[1][1].split('_')[0]
            fullname = User.objects.get(id=user_id).fullname
        except Exception:
            fullname = None
        users[x[0]] = {
            'extension': x[1][0],
            'fullname': fullname,
        }

    return users


def get_response_data(response):
    if response.status_code == status.HTTP_400_BAD_REQUEST:
        raise exceptions.ValidationError({'message': response.text})
    try:
        calls_data = response.json().get('result')
    except Exception as e:
        print(e)
        raise ServiceUnavailable(
            {'detail': 'Can"t parse Asterisk Service response'})

    return calls_data


@func_time
@api_view(['GET'])
def calls_to_user(request):
    data = dict()
    try:
        user_id = int(request.query_params.get('user_id'))
    except (ValueError, TypeError):
        raise exceptions.ValidationError(
            {'message': 'Parameter {user_id} required and must be integer.'})
    user = get_object_or_404(User, id=user_id)

    try:
        phone_number = user.phone_number[-10:]
    except Exception:
        raise exceptions.ValidationError(
                {'message': 'This user not have a {phone_number}.'})

    data['phone_number'] = phone_number
    data['range'] = request.query_params.get('range')
    data['month_date'] = request.query_params.get('month_date') or timezone.now().date().strftime('%Y-%m')
    data['query_type'] = 'user'

    response = request_to_asterisk(data, url='/calls')
    calls_data = get_response_data(response)
    calls_data = prepare_calls_data(calls_data)

    result = {'result': calls_data}

    return Response(result, status=status.HTTP_200_OK)


@api_view(['GET'])
@func_time
@permission_classes((IsAdminUser,))
def all_calls(request):
    data = request.query_params

    response = request_to_asterisk(data, url='/calls')

    calls_data = get_response_data(response)

    calls_data = prepare_calls_data(calls_data)

    pages_count = (len(calls_data) // 30) + 1
    page = int(request.query_params.get('page') or 1)
    page_from = 30 * (page - 1)
    page_to = page_from + 30

    result = {
        'pages': pages_count,
        'result': calls_data[page_from:page_to],
        'count': len(calls_data)
    }

    return Response(result, status=status.HTTP_200_OK)


@api_view(['GET'])
@func_time
def asterisk_users(request):
    response = request_to_asterisk(data=None, url='/users')
    try:
        users = response.json().get('result')
    except Exception as e:
        print(e)
        raise ServiceUnavailable(
            {'detail': 'Can"t parse Asterisk Service response'})

    users = prepare_asterisk_users(users)
    result = {'result': users}

    return Response(result, status=status.HTTP_200_OK)


@api_view(['POST'])
@func_time
def change_asterisk_user(request):
    data = {}
    try:
        user_id = int(request.data.get('user_id'))
    except (ValueError, TypeError):
        raise exceptions.ValidationError(
            {'message': 'Parameter {user_id} required and must be integer'})
    user = get_object_or_404(User, pk=user_id)

    data['extension'] = request.data.get('extension')  # {"user_id": 15287, "extension": "9002"}
    data['fullname'] = '%s_%s' % (user_id, user.fullname)

    try:
        response = requests.put(settings.ASTERISK_SERVICE_ADDRESS + '/change_user',
                                data=json.dumps(data), timeout=5,
                                headers={'Content-Type': 'application/json'})
    except Exception as e:
        print(e)
        raise ServiceUnavailable(
            {'detail': 'Asterisk Service temporarily unavailable, try again later'})

    result = get_response_data(response)
    result = {'result': result}

    return Response(result, status=status.HTTP_200_OK)
