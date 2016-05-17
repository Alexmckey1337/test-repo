# -*- coding: utf-8
from account.models import CustomUser as User
from account.models import VERBOSE_FIELDS as verbose_fields
from status.models import Status
from hierarchy.models import Hierarchy, Department
from rest_framework.parsers import FileUploadParser
from serializers import UserSerializer
from rest_framework.decorators import list_route
from rest_framework.decorators import api_view
from rest_framework import viewsets, filters
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.contrib.auth import update_session_auth_hash
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.template.loader import get_template
from django.template import Context
from django.core.mail import EmailMultiAlternatives
from resources import clean_password, clean_old_password
from rest_framework.permissions import AllowAny
import hashlib
import random
import json
from rest_framework.parsers import MultiPartParser, FileUploadParser
from rest_framework.decorators import parser_classes
from rest_framework.views import APIView
from edem.settings import SITE_DOMAIN_URL, DEFAULT_FROM_EMAIL
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from event.views import sync_user
from account.models import VERBOSE_FIELDS

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    filter_backends = (filters.DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter,)
    t = tuple(verbose_fields.values())
    #ordering_fields = 
    #search_fields = ()
    filter_list = list(VERBOSE_FIELDS.values())
    #filter_fields = ['first_name', 'last_name', 'middle_name',
    #                 'born_date', 'address', 'skype',
    #                 'phone_number', 'email', 'master', 'hierarchy', 'hierarchy__level', 'department', ]
    filter_list.append('hierarchy__level')
    filter_list.append('master')
    filter_fields = filter_list
    def dispatch(self, request, *args, **kwargs):
        if kwargs.get('pk') == 'current' and request.user.is_authenticated():
            kwargs['pk'] = request.user.pk

        return super(UserViewSet, self).dispatch(request, *args, **kwargs)

    @list_route()
    def all(self, request):
        users = User.objects.filter(is_staff=False).all()

        page = self.paginate_queryset(users)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)


@api_view(['POST'])
def login_view(request):
    permission_classes = (AllowAny,)
    response_dict = dict()
    if request.method == 'POST':
        data = request.data
        user_check = User.objects.filter(email=data['email']).first()
        if user_check:
            user = authenticate(username=user_check.username, password=data['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    response_dict['message'] = 'Добро пожаловать'
                    response_dict['status'] = True
                else:
                    response_dict['message'] = 'Вы не имеете доступ'
                    response_dict['status'] = False
                if not data['remember_me']:
                    request.session.set_expiry(0)
            else:
                response_dict['message'] = 'Пользователя с таким username и паролем не существует'
                response_dict['status'] = False
        else:
            response_dict['message'] = 'Пользователя с таким username и паролем не существует'
            response_dict['status'] = False
    return Response(response_dict)

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('entry'))

@api_view(['POST'])
def change_password(request):
    response_dict = dict()
    if request.method == 'POST':
        data = request.data
        user = request.user
        if clean_old_password(user, data):
            if clean_password(data):
                user.set_password(clean_password(data))
                user.save()
                update_session_auth_hash(request, user)
                response_dict['message'] = 'Пароль успешно изменен'
            else:
                response_dict['message'] = 'Введенные пароли не совпадают'
        else:
            response_dict['message'] = 'Вы ввели неверный пароль'
    return Response(response_dict)


@api_view(['POST'])
def delete_user(request):
    response_dict = dict()
    if request.method == 'POST':
        data = request.data
        user = User.objects.filter(id=data['id']).first()
        if user:
            user.delete()
            response_dict['message'] = "Пользователь был удален успешно"
        else:
            response_dict['message'] = "Пользователь не существует"
    return Response(response_dict)


@api_view(['POST'])
def create_user(request):
    response_dict = dict()

    data = request.data
    if 'id' in data.keys():
        user = User.objects.filter(id=data['id']).first()
        if not user:
            response_dict['message'] = u"Пользователя не существует"
        else:
            for key, value in data.iteritems():
                if key == "master":
                    master = User.objects.get(id=value)
                    user.master = master
                    #level = master.hierarchy.level - 1
                    #hierarchy = Hierarchy.objects.filter(level=level).first()
                    #user.hierarchy = hierarchy
                    #user.department = master.department
                elif key == 'hierarchy':
                    hierarchy = Hierarchy.objects.filter(id=value).first()
                    user.hierarchy = hierarchy
                elif key == 'department':
                    department = Department.objects.filter(id=value).first()
                    user.department = department
                elif key == 'statuses':
                    for status in user.statuses.all():
                        user.statuses.remove(status)
                    for s in value:
                        status = Status.objects.filter(id=s).first()
                        user.statuses.add(status)
                elif key == 'born_date':
                    if value:
                        user.born_date = value
                        user.save()
                    else:
                        user.born_date = None
                        user.save()
                
                else:
                    setattr(user, key, value)
            user.save()
            sync_user(user)
            #response_dict['message'] = data.items()
            response_dict['message'] = u"Пользователь успешно отредактирован"
            response_dict['id'] = user.id
            response_dict['redirect'] = True
    else:
        if data['email']:
            try:
                validate_email(data['email'])
            except ValidationError as e:
                response_dict['message'] = u'Неверный формат почты'
            else:
                if User.objects.filter(username=data['email']).first()\
                        or User.objects.filter(email=data['email']).first()\
                        or User.objects.filter(first_name=data['first_name'], last_name=data['last_name'], middle_name=['middle_name']).first():
                    response_dict['message'] = u"Пользователь с таким именем или почтой уже есть в базе данных"
                else:
                    user = User.objects.create(username=data['email'],
                                               email=data['email'],
                                               )
                    for key, value in data.iteritems():
                        if key == "master":
                            master = User.objects.get(id=value)
                            user.master = master
                            user.save()
                        elif key == 'hierarchy':
                            hierarchy = Hierarchy.objects.filter(id=value).first()
                            user.hierarchy = hierarchy
                            user.save()
                        elif key == 'department':
                            department = Department.objects.filter(id=value).first()
                            user.department = department
                            user.save()
                        elif key == 'statuses':
                            for s in value:
                                status = Status.objects.filter(id=s).first()
                                user.statuses.add(status)
                                user.save()
                        elif key == 'born_date':
                            if value:
                                user.born_date = value
                                user.save()
                            else:
                                user.born_date = None
                                user.save()
                        else:
                            setattr(user, key, value)
                    user.save()
                    sync_user(user)
                    #salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
                    #password = hashlib.sha1(salt+user.email).hexdigest()
                    #user.set_password(password)
                    #user.description += password
                    #plaintext = get_template('email/register_email.txt')
                    #htmly = get_template('email/register_email.html')
                    #d = Context({'user': user, 'SITE_DOMAIN_URL': SITE_DOMAIN_URL, 'password': password})
                    #subject, from_email, to = 'Подтверждение регистрации', DEFAULT_FROM_EMAIL, user.email
                    #text_content = plaintext.render(d)
                    #html_content = htmly.render(d)
                    #msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                    #msg.attach_alternative(html_content, "text/html")
                    #msg.send()
                    response_dict['message'] = u"Пользователь успешно создан"
                    #response_dict['message'] = data
                    response_dict['id'] = user.id
                    response_dict['redirect'] = True
        else:
            salt = hashlib.sha1(str(random.random())).hexdigest()[:8]
            username = 'user' + hashlib.sha1(salt).hexdigest()
            user = User.objects.create(username=username)
            for key, value in data.iteritems():
                if key == "master":
                    master = User.objects.get(id=value)
                    user.master = master
                    user.save()
                elif key == 'hierarchy':
                    hierarchy = Hierarchy.objects.filter(id=value).first()
                    user.hierarchy = hierarchy
                    user.save()
                elif key == 'department':
                    department = Department.objects.filter(id=value).first()
                    user.department = department
                    user.save()
                elif key == 'statuses':
                    for s in value:
                        status = Status.objects.filter(id=s).first()
                        user.statuses.add(status)
                        user.save()
                elif key == 'born_date':
                        if value:
                            user.born_date = value
                            user.save()
                        else:
                            user.born_date = None
                            user.save()
                else:
                    setattr(user, key, value)
                    user.save()

            sync_user(user)
            response_dict['message'] = u"Пользователь успешно создан"

            response_dict['id'] = user.id
            response_dict['redirect'] = True
    return Response(response_dict)


@api_view(['POST'])
def send_password(request):
    response_dict = dict()
    if request.method == 'POST':
        data = request.data
        user = User.objects.filter(id=data['id']).first()
        if user:
            salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
            password = hashlib.sha1(salt+user.email).hexdigest()[:12]
            user.set_password(password)
            user.save()
            #user.description += password
            plaintext = get_template('email/register_email.txt')
            htmly = get_template('email/register_email.html')
            d = Context({'user': user, 'SITE_DOMAIN_URL': SITE_DOMAIN_URL, 'password': password})
            subject, from_email, to = 'Подтверждение регистрации', DEFAULT_FROM_EMAIL, user.email
            text_content = plaintext.render(d)
            html_content = htmly.render(d)
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            response_dict['message'] = u"Пароль успешно отправлен"
        else:
            response_dict['message'] = "Пользователь не существует"
    return Response(response_dict)

