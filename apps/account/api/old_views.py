import binascii
import os

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.core.exceptions import MultipleObjectsReturned
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.account.models import CustomUser as User
from apps.account.resources import clean_password


def generate_key():
    return binascii.hexlify(os.urandom(20)).decode()


def send_email_for_renewal_password(user):
    user.activation_key = generate_key()
    user.save()
    plaintext = get_template('email/password_reset.txt')
    htmly = get_template('email/password_reset.html')
    d = {'user': user, 'site_url': settings.SITE_DOMAIN_URL.rstrip('/')}
    subject, from_email, to = 'Восстановление пароля', settings.DEFAULT_FROM_EMAIL, user.email
    text_content = plaintext.render(d)
    html_content = htmly.render(d)
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


@api_view(['POST'])
@permission_classes((AllowAny,))
def login_view(request):
    """
    Login user via email and password.

    :param request: data{'email': string, 'password': string} or data{'user_id': int, 'password': string}
    :return: {'detail': string, 'status': boolean}
    """
    response_dict = dict()
    data = request.data
    if 'password' not in data.keys() or not ({'email', 'user_id', 'email_or_id'} & set(data.keys())):
        response_dict['detail'] = "Неверные данные для входа"
        response_dict['status'] = False
        return Response(response_dict)
    if 'user_id' in data or data.get('email_or_id', '').isdigit():
        user_id = data.get('user_id', data.get('email_or_id'))
        user = authenticate(user_id=user_id, password=data['password'])
    elif 'email' in data.keys() or 'email_or_id' in data.keys():
        email = data.get('email', data.get('email_or_id'))
        if '@' not in email:
            user = authenticate(username=email, password=data['password'])
        else:
            try:
                user = User.objects.get(email__iexact=email, can_login=True)
            except User.DoesNotExist:
                if User.objects.filter(email__iexact=email).exists():
                    response_dict['detail'] = _('Вы не имеете право для входа на сайт.')
                    response_dict['status'] = False
                    return Response(response_dict)
                response_dict['detail'] = "Пользователя с таким email не существует"
                response_dict['status'] = False
                return Response(response_dict)
            except MultipleObjectsReturned:
                response_dict['detail'] = "Есть несколько пользователей с таким email"
                response_dict['status'] = False
                return Response(response_dict)
            user = authenticate(username=user.username, password=data['password'])
    else:
        user = None
    if user is not None:
        login(request, user)
        response_dict['uid'] = user.id
        response_dict['detail'] = "Добро пожаловать"
        response_dict['status'] = True
    else:
        response_dict['detail'] = "Неверные данные для входа"
        response_dict['status'] = False
    return Response(response_dict)


@api_view(['POST'])
@permission_classes((AllowAny,))
def password_forgot(request):
    data = request.data
    email = data.get('email')
    if not email:
        return Response(data={'detail': _('Поле email обязательно')},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.get(email=email, can_login=True)
    except User.DoesNotExist:
        if User.objects.filter(email=email).exists():
            return Response(data={'detail': _('Вы не имеете право для входа на сайт.')},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(data={'detail': _('Пользователя с таким email не существует')},
                        status=status.HTTP_400_BAD_REQUEST)
    except MultipleObjectsReturned:
        return Response(data={'detail': _("Есть несколько пользователей с таким email")},
                        status=status.HTTP_400_BAD_REQUEST)
    send_email_for_renewal_password(user)

    return Response(data={
        'detail': _('Вам на почту было отправлено письмо с дальнейшими инструкциями по восстановлению пароля')})


@api_view(['POST'])
@permission_classes((AllowAny,))
def password_view(request):
    data = request.data
    key = data['activation_key']
    try:
        user = User.objects.get(activation_key=key)
    except User.DoesNotExist:
        return Response(data={'detail': _('Ключ активации несуществует или устарел')},
                        status=status.HTTP_400_BAD_REQUEST)
    new_password = clean_password(data)
    if new_password:
        user.set_password(new_password)
        user.activation_key = ''
        user.save()
        return Response(data={'detail': _('Пароль успешно изменен')})
    return Response(data={'detail': _('Пароли не совпадают')}, status=status.HTTP_400_BAD_REQUEST)
