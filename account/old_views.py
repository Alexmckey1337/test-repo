import binascii
import os

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.core.mail import EmailMultiAlternatives
from django.template import Context
from django.template.loader import get_template
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from account.models import CustomUser as User
from account.resources import clean_password


def generate_key():
    return binascii.hexlify(os.urandom(20)).decode()


def send_email_for_renewal_password(user):
    user.activation_key = generate_key()
    user.save()
    plaintext = get_template('email/password_reset.txt')
    htmly = get_template('email/password_reset.html')
    d = Context({'user': user, 'site_url': settings.SITE_DOMAIN_URL.rstrip('/')})
    subject, from_email, to = 'Восстановление пароля', settings.DEFAULT_FROM_EMAIL, user.email
    text_content = plaintext.render(d)
    html_content = htmly.render(d)
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


@api_view(['POST'])
def login_view(request):
    """
    Login user via email and password.

    :param request: data{'email': string, 'password': string}
    :return: {'message': string, 'status': boolean}
    """
    response_dict = dict()
    data = request.data
    try:
        user = User.objects.get(email=data['email'])
        user = authenticate(username=user.username, password=data['password'])
        if user is not None:
            if user.is_active:
                login(request, user)
                response_dict['uid'] = user.id
                response_dict['message'] = "Добро пожаловать"
                response_dict['status'] = True
            else:
                response_dict['message'] = "Вы не имеете доступ"
                response_dict['status'] = False
        else:
            response_dict['message'] = "Неверный пароль или email"
            response_dict['status'] = False
    except User.DoesNotExist:
        response_dict['message'] = "Пользователя с таким email не существует"
        response_dict['status'] = False
    return Response(response_dict)


@api_view(['POST'])
def password_forgot(request):
    data = request.data
    email = data.get('email')
    if not email:
        return Response(data={'detail': _('Поле email обязательно')},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response(data={'detail': _('Пользователя с таким email не существует')},
                        status=status.HTTP_400_BAD_REQUEST)
    send_email_for_renewal_password(user)

    return Response(data={
        'detail': _('Вам на почту было отправлено письмо с дальнейшими инструкциями по восстановлению пароля')})


@api_view(['POST'])
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
