# -*- coding: utf-8
import hashlib
import random

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import update_session_auth_hash
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template import Context
from django.template.loader import get_template
from rest_framework import viewsets, filters
from rest_framework.decorators import api_view
from rest_framework.decorators import list_route
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from account.models import CustomUser as User, AdditionalPhoneNumber
from edem.settings import SITE_DOMAIN_URL, DEFAULT_FROM_EMAIL
from hierarchy.models import Hierarchy, Department
from partnership.models import Partnership
from resources import clean_password, clean_old_password
from serializers import UserSerializer, UserShortSerializer
from status.models import Status, Division
from tv_crm.views import sync_unique_user_call


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_active=True).all().order_by('-date_joined')
    serializer_class = UserSerializer
    filter_backends = (filters.DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter,)
    permission_classes = (IsAuthenticated,)
    ordering_fields = ('first_name', 'last_name', 'middle_name',
                       'born_date', 'country', 'region', 'city', 'disrict', 'address', 'skype',
                       'phone_number', 'email', 'hierarchy__level', 'department__title',
                       'facebook', 'vkontakte', 'hierarchy_order', 'master__last_name', )
    search_fields = ('first_name', 'last_name', 'middle_name',
                     'country', 'region', 'city', 'district',
                     'address', 'skype', 'phone_number', 'hierarchy__title', 'department__title',
                     'email', 'master__last_name', )
    filter_fields = ('first_name', 'last_name', 'middle_name',
                     'born_date', 'email', 'department__title',
                     'country', 'region', 'city', 'district', 'address',
                     'skype', 'phone_number', 'hierarchy__level', 'master', 'master__last_name', )

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

    @list_route()
    def disciples(self, request, *args, **kwargs):
        from resources import get_disciples
        q = get_disciples(request.user)
        q = q.order_by('-hierarchy__level')
        queryset = self.filter_queryset(q)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

#    def list(self, request, *args, **kwargs):
#        from resources import get_disciples
#        q = get_disciples(request.user)
#        q = q.order_by('-hierarchy__level')
#        queryset = self.filter_queryset(q)
#        page = self.paginate_queryset(queryset)
#        if page is not None:
#            serializer = self.get_serializer(page, many=True)
#            return self.get_paginated_response(serializer.data)
#        serializer = self.get_serializer(queryset, many=True)
#        return Response(serializer.data)


class UserShortViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserShortSerializer
    pagination_class = None
    permission_classes = (IsAuthenticated,)
    filter_backends = (filters.DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter,)
    filter_fields = ('first_name', 'last_name', 'department', 'hierarchy')
    search_fields = ('first_name', 'last_name')


@api_view(['POST'])
def login_view(request):
    """
    Login user via email and password.

    :param request: data{'email': string, 'password': string}
    :return: {'message': string, 'status': boolean}
    """
    permission_classes = (AllowAny,)
    response_dict = dict()
    data = request.data
    try:
        user = User.objects.get(email=data['email'])
        user = authenticate(username=user.username, password=data['password'])
        if user is not None:
            if user.is_active:
                login(request, user)
                response_dict['uid'] = user.id
                response_dict['message'] = u"Добро пожаловать"
                response_dict['status'] = True
            else:
                response_dict['message'] = u"Вы не имеете доступ"
                response_dict['status'] = False
        else:
            response_dict['message'] = u"Неверный пароль или email"
            response_dict['status'] = False
    except User.DoesNotExist:
        response_dict['message'] = u"Пользователя с таким email не существует"
        response_dict['status'] = False
    return Response(response_dict)


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('entry'))


@api_view(['POST'])
def change_password(request):
    """
    Changes password for request.user

    :param request: data{'password1': string, 'password2': string}
    :return: {'message': string, 'status': boolean}
    """
    response_dict = dict()
    data = request.data
    user = request.user
    if clean_old_password(user, data):
        if clean_password(data):
            user.set_password(clean_password(data))
            user.save()
            update_session_auth_hash(request, user)
            response_dict['message'] = u'Пароль успешно изменен'
            response_dict['status'] = True
        else:
            response_dict['message'] = u'Введенные пароли не совпадают'
            response_dict['status'] = False
    else:
        response_dict['message'] = u'Вы ввели неверный пароль'
        response_dict['status'] = False
    return Response(response_dict)


@api_view(['POST'])
def delete_user(request):
    """
    Deleting a user, selected by id

    :param request: data{'id': int}
    :return: {'message': string, 'status': boolean}
    """
    response_dict = dict()
    data = request.data
    try:
        user = User.objects.get(id=data['id'])
        archons = User.objects.filter(hierarchy__level=7).all()
        if user in archons.all():
            message['message'] = u"Нельзя удалить Архонта"
            message['status'] = False
            message['redirect'] = False
            return Response(message)
        user.delete()
        response_dict['message'] = u"Пользователь был удален успешно"
        response_dict['status'] = True
    except User.DoesNotExist:
        response_dict['message'] = u"Пользователь не существует"
        response_dict['status'] = False
    return Response(response_dict)


def check_recursion(user, master):
    """
    Check recursion when change user's master. Return False when all is right.

    :param user: User object
    :param master: User object
    :return: boolean
    """
    if master == user:
        return True
    if master.master:
        if master.master == user:
            print "Recursion"
            return True
        else:
            return check_recursion(user, master.master)
    else:
        return False


def check_all_recursion():
    users = User.objects.all()
    for user in users:
        if user.master:
            check_recursion(user, user.master)


def edit_user(data, files):
    message = dict()
    try:
        user = User.objects.get(id=data['id'])
        archons = User.objects.filter(hierarchy__level=7).all()
        if user in archons.all():
            message['message'] = u"Нельзя редактировать Архонта"
            message['status'] = False
            message['redirect'] = False
            return message
        if "master" in data.keys():
            try:
                master = User.objects.get(id=data['master'])
                if check_recursion(user, master):
                    message['message'] = u"РЕКУРСИЯ!"
                    message['status'] = False
                    message['redirect'] = False
                    return message
            except User.DoesNotExist:
                master = None
            user.master = master
        for key, value in data.iteritems():
            if key == 'master':
                pass
            elif key == 'additional_phone':
                if value:
                    phone_number = user.additional_phones.first()
                    if phone_number:
                        phone_number.number = value
                        phone_number.save()
                    else:
                        AdditionalPhoneNumber.objects.create(user=user, number=value)
                else:
                    phones = user.additional_phones.all()
                    for phone in phones:
                        phone.delete()
            elif key == 'hierarchy':
                try:
                    hierarchy = Hierarchy.objects.get(id=value)
                    user.hierarchy = hierarchy
                except Hierarchy.DoesNotExist:
                    pass
            elif key == 'department':
                try:
                    department = Department.objects.get(id=value)
                    user.department = department
                except Department.DoesNotExist:
                    pass
            elif key == 'divisions':
                for division in user.divisions.all():
                    user.divisions.remove(division)
                for s in value:
                    try:
                        division = Division.objects.get(id=s)
                        user.divisions.add(division)
                    except Division.DoesNotExist:
                        pass
            elif key == 'born_date':
                if value:
                    user.born_date = value
                else:
                    user.born_date = None
            elif key == 'repentance_date':
                if value:
                    user.repentance_date = value
                else:
                    user.repentance_date = None
            elif key == 'coming_date':
                if value:
                    user.coming_date = value
                else:
                    user.coming_date = None
            elif key == 'first_name':
                if value:
                    user.first_name = value.strip()
            elif key == 'last_name':
                if value:
                    user.last_name = value.strip()
            elif key == 'middle_name':
                if value:
                    user.middle_name = value.strip()
            else:
                setattr(user, key, value)
        if files:
            if 'file' in files.keys():
                if files['file'].name == 'blob':
                    photo = files['file']
                else:
                    import os
                    ext = os.path.splitext(files['file'].name)[1]
                    valid_extensions = ['.jpg', '.png', '.jpeg']
                    if ext in valid_extensions:
                        photo = files['file']
                    else:
                        photo = None
                user.image = photo
            if 'source' in files.keys():
                if files['source'].name == 'blob':
                    photo = files['source']
                else:
                    import os
                    ext = os.path.splitext(files['source'].name)[1]
                    valid_extensions = ['.jpg', '.png', '.jpeg']
                    if ext in valid_extensions:
                        photo = files['source']
                    else:
                        photo = None
                user.image_source = photo
        user.save()
        message['message'] = u"Пользователь успешно отредактирован"
        message['id'] = user.id
        message['redirect'] = True
    except User.DoesNotExist:
        message['message'] = u"Пользователя не существует"
        message['id'] = ''
        message['redirect'] = False
    return message


def add_user(data, files, request):
    message = dict()
    if 'master' in data.keys():
        master = User.objects.get(id=data['master'])
        twink_user = User.objects.filter(first_name=data['first_name'], last_name=data['last_name'], master=master).first()
    else:
        twink_user = None
    if not twink_user:
        if data['email']:
            username = email = data['email']
        else:
            email = ''
            salt = hashlib.sha1(str(random.random())).hexdigest()[:8]
            username = 'user_' + hashlib.sha1(salt).hexdigest()
        user = User.objects.create(username=username,
                                   email=email,
                                   first_name=data['first_name'],
                                   last_name=data['last_name'])
        for key, value in data.iteritems():
            if key == "master":
                master = User.objects.get(id=value)
                user.master = master
                user.save()
            elif key == 'hierarchy':
                hierarchy = Hierarchy.objects.filter(id=value).first()
                user.hierarchy = hierarchy
                user.save()
            elif key == 'additional_phone' and value:
                AdditionalPhoneNumber.objects.create(user=user, number=value)
            elif key == 'department':
                department = Department.objects.filter(id=value).first()
                user.department = department
                user.save()
            elif key == 'statuses':
                for s in value:
                    status = Status.objects.filter(id=s).first()
                    user.statuses.add(status)
                    user.save()
            elif key == 'divisions':
                for s in value:
                    division = Division.objects.filter(id=s).first()
                    user.divisions.add(division)
                    user.save()
            elif key == 'born_date':
                if value:
                    user.born_date = value
                    user.save()
                else:
                    user.born_date = None
                    user.save()
            elif key == 'repentance_date':
                if value:
                    user.repentance_date = value
                    user.save()
                else:
                    user.repentance_date = None
                    user.save()
            elif key == 'coming_date':
                if value:
                    user.coming_date = value
                    user.save()
                else:
                    user.coming_date = None
                    user.save()
            elif key == 'first_name':
                if value:
                    user.first_name = value.strip()
                    user.save()
            elif key == 'last_name':
                if value:
                    user.last_name = value.strip()
                    user.save()
            elif key == 'middle_name':
                if value:
                    user.middle_name = value.strip()
                    user.save()
            else:
                setattr(user, key, value)
        if files:
            if "file" in files.keys():
                if files['file'].name == 'blob':
                    photo = files['file']
                else:
                    import os
                    ext = os.path.splitext(files['file'].name)[1]
                    valid_extensions = ['.jpg', '.png', '.jpeg']
                    if ext in valid_extensions:
                        photo = files['file']
                    else:
                        photo = None
                user.image = photo
            if 'source' in files.keys():
                if files['source'].name == 'blob':
                    photo = files['source']
                else:
                    import os
                    ext = os.path.splitext(files['source'].name)[1]
                    valid_extensions = ['.jpg', '.png', '.jpeg']
                    if ext in valid_extensions:
                        photo = files['source']
                    else:
                        photo = None
                user.image_source = photo
            user.save()
        sync_unique_user_call(user)
        #serializer = UserSerializer(user, context={'request': request})
        #message['response'] = serializer.data
        message['message'] = u"Пользователь успешно создан"
        message['id'] = user.id
        message['redirect'] = True
    else:
        message['message'] = u"Пользователь с таким именем и фамилией уже есть в базе данных"
        message['id'] = twink_user.id
        message['redirect'] = True
    return message


def send_password_func(user_id):
    response_dict = dict()
    user = User.objects.filter(id=user_id).first()
    if user:
        salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
        password = hashlib.sha1(salt + user.email).hexdigest()[:12]
        user.set_password(password)
        user.save()
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
    return response_dict


def create_or_update_partnership(data, user_id=None):
    response_dict = dict()
    if 'id' in data.keys():
        user = User.objects.get(id=data['id'])
        if 'remove_partnership' in data.keys():
            if data['remove_partnership'] == 'true':
                try:
                    Partnership.objects.get(user=user).delete()
                except Partnership.DoesNotExist:
                    pass
        else:
            if 'responsible' in data.keys():
                try:
                    object = Partnership.objects.get(user=user)
                    for key, value in data.iteritems():
                        if key == "id":
                            pass
                        else:
                            if key == "responsible":
                                responsible_partnerhip = Partnership.objects.filter(user__id=value).first()
                                object.responsible = responsible_partnerhip
                            else:
                                setattr(object, key, value)
                    object.save()
                    response_dict['message'] = u"Партнерство успешно изменено."
                    response_dict['status'] = True
                except Partnership.DoesNotExist:
                    if 'responsible' in data.keys():
                        responsible_partnerhip = Partnership.objects.filter(id=data['responsible']).first()
                        Partnership.objects.create(user=user, responsible=responsible_partnerhip, value=data['value'], date=data['date'])
                    else:
                        pass
    else:
        if data['responsible']:
            responsible_partnership_id = data['responsible']
        else:
            responsible_partnership_id = None
        value = data['value']
        date = data['date']
        try:
            user = User.objects.get(id=user_id)
            user_check = Partnership.objects.filter(user=user).first()
            if user_check:
                pass
            else:
                responsible_partnership = Partnership.objects.filter(id=responsible_partnership_id).first()
                if responsible_partnership:
                    object = Partnership.objects.create(user=user, responsible=responsible_partnership, value=value, date=date)
                    if object:
                        response_dict['message'] = u"Партнерство успешно добавлено."
                        response_dict['status'] = True
        except User.DoesNotExist:
            response_dict['data'] = []
            response_dict['message'] = u"Пользователя не существует."
            response_dict['status'] = False
    return response_dict


@api_view(['POST'])
def create_user(request):
    response_dict = dict()
    data = request.data
    files = request.FILES
    if request.user.is_staff:
        if 'id' in data.keys():
            user = User.objects.filter(id=data['id']).first()
            response_dict = edit_user(data, files)
            if 'old_password' in data.keys() and 'password1' in data.keys():
                if len(data['old_password']) > 0 and len(data['password1'])>0:
                    if clean_old_password(user, data):
                        if clean_password(data):
                            user.set_password(clean_password(data))
                            user.save()
                            update_session_auth_hash(request, user)
                            response_dict['special_message'] = u'Пароль успешно изменен'
                        else:
                            response_dict['special_message'] = u'Введенные пароли не совпадают'
                    else:
                        response_dict['special_message'] = u'Вы ввели неверный пароль'
            if 'responsible' in data.keys() or 'remove_partnership' in data.keys():
                create_or_update_partnership(data)
                response_dict['special_message'] = u'Партнерство успешно изменено'
        else:
            response_dict = add_user(data, files, request)
            if data['send_password']:
                send_password_func(response_dict['id'])
            if 'responsible' in data.keys():
                create_or_update_partnership(data, str(response_dict['id']))
                response_dict['special_message'] = u'Партнерство успешно создано'
    else:
        response_dict['message'] = u"Нет полномочий"
        response_dict['redirect'] = False
    return Response(response_dict)


@api_view(['POST'])
def send_password(request):
    response_dict = dict()
    if request.method == 'POST':
        data = request.data
        response_dict = send_password_func(data['id'])
    return Response(response_dict)


@api_view(['POST'])
def download_image(request):
    response_dict = dict()
    data = request.data
    files = request.FILES
    try:
        user = User.objects.get(id=data['id'])
        if files:
            if files['file'].name == 'blob':
                photo = files['file']
            else:
                import os
                ext = os.path.splitext(files['file'].name)[1]
                valid_extensions = ['.jpg', '.png', '.jpeg']
                if ext in valid_extensions:
                    photo = files['file']
                else:
                    photo = None
            user.image = photo
            user.save()
            response_dict['message'] = u"Фото успешно загружено"
            response_dict['redirect'] = False
            response_dict['status'] = True
    except User.DoesNotExist:
        response_dict['message'] = u"Нет такого пользователя"
        response_dict['redirect'] = False
        response_dict['status'] = False
    return Response(response_dict)


@api_view(['POST'])
def password_forgot(request):
    data = request.data
    email = data['email']
    response_dict = dict()
    if len(email) > 0:
        try:
            user = User.objects.get(email=email)
            salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
            user.activation_key = hashlib.sha1(salt+user.email).hexdigest()
            user.save()
            plaintext = get_template('email/password_reset.txt')
            htmly = get_template('email/password_reset.html')
            d = Context({'user': user, 'site_url': SITE_DOMAIN_URL})
            subject, from_email, to = 'Восстановление пароля', DEFAULT_FROM_EMAIL, user.email
            text_content = plaintext.render(d)
            html_content = htmly.render(d)
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            response_dict['message'] = u"Вам на почту было отправлено письмо с дальнейшими инструкциями по восстановлению пароля"
            response_dict['status'] = True
        except User.DoesNotExist:
            response_dict['message'] = u"Пользователя с таким email не существует"
            response_dict['status'] = False
    else:
        response_dict['message'] = u"Поле email обязательно"
        response_dict['status'] = False
    return Response(response_dict)


@api_view(['POST'])
def password_view(request, activation_key=None):
    data = request.data
    response_dict = dict()
    key = data['activation_key']
    try:
        user = User.objects.get(activation_key=key)
        if clean_password(data):
            user.set_password(clean_password(data))
            user.save()
            response_dict['message'] = u"Пароль успешно изменен"
            response_dict['status'] = True
        else:
            response_dict['message'] = u"Пароли не совпадают"
            response_dict['status'] = False
    except User.DoesNotExist:
        response_dict['message'] = u"Ключ активации несуществует или устарел"
        response_dict['status'] = False
    return Response(response_dict)


