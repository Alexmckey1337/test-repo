# -*- coding: utf-8
from __future__ import unicode_literals

import binascii
import os
import warnings

import django_filters
from django.conf import settings
from django.contrib.auth import authenticate, login, logout as django_logout
from django.contrib.auth import update_session_auth_hash
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.db.models import Case, BooleanField
from django.db.models import Value as V
from django.db.models import When
from django.db.models.functions import Concat
from django.http import HttpResponseRedirect
from django.template import Context
from django.template.loader import get_template
from django.utils import six
from django.utils.translation import ugettext_lazy as _
from rest_auth.views import LogoutView as RestAuthLogoutView
from rest_framework import status
from rest_framework import viewsets, filters
from rest_framework.decorators import api_view, detail_route
from rest_framework.decorators import list_route
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from account.models import CustomUser as User, AdditionalPhoneNumber
from account.models import Token
from common.filters import FieldSearchFilter
from hierarchy.models import Hierarchy, Department
from navigation.models import user_table
from partnership.models import Partnership
from status.models import Status, Division
from summit.models import SummitType, SummitLesson, SummitAnketNote, SummitUserConsultant, AnketEmail, SummitAnket
from tv_crm.models import LastCall
from .resources import clean_password, clean_old_password
from .serializers import UserSerializer, UserShortSerializer, UserTableSerializer, NewUserSerializer, \
    UserSingleSerializer

USER_FIELDS = {
    'text_fields': {
        # 'username',
        'email',
        'first_name', 'last_name', 'middle_name', 'phone_number', 'skype', 'country', 'region',
        'city', 'district', 'address', 'facebook', 'vkontakte', 'odnoklassniki', 'description',
        # 'activation_key', 'hierarchy_order',
    },
    'date_fields': {
        'born_date', 'repentance_date', 'coming_date',
    },
    'images': {
        # 'image', 'image_source',
    },
    'fk': {
        'department', 'hierarchy',
        # 'master',
    },
    'm2m': {
        'additional_phone', 'divisions',
    }
}

PARTNER_FIELDS = (
    'responsible', 'date', 'value'
)


def generate_key():
    return binascii.hexlify(os.urandom(20)).decode()


class UserPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'user_table': user_table(self.request.user),
            'results': data
        })


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
                       'facebook', 'vkontakte', 'hierarchy_order', 'master__last_name',)
    search_fields = ('first_name', 'last_name', 'middle_name',
                     'country', 'region', 'city', 'district',
                     'address', 'skype', 'phone_number', 'hierarchy__title', 'department__title',
                     'email', 'master__last_name',)
    filter_fields = ('first_name', 'last_name', 'middle_name',
                     'born_date', 'email', 'department__title',
                     'country', 'region', 'city', 'district', 'address',
                     'skype', 'phone_number', 'hierarchy__level', 'master', 'master__last_name',)

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
        from .resources import get_disciples
        q = get_disciples(request.user)
        q = q.order_by('-hierarchy__level')
        queryset = self.filter_queryset(q)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class UserFilter(django_filters.FilterSet):
    hierarchy = django_filters.ModelChoiceFilter(name='hierarchy', queryset=Hierarchy.objects.all())
    master = django_filters.ModelMultipleChoiceFilter(name="master", queryset=User.objects.all())
    department = django_filters.ModelChoiceFilter(name="department", queryset=Department.objects.all())

    class Meta:
        model = User
        fields = ['master', 'hierarchy', 'department']


class ShortUserFilter(django_filters.FilterSet):
    level_gt = django_filters.NumberFilter(name='hierarchy__level', lookup_expr='gt')
    level_gte = django_filters.NumberFilter(name='hierarchy__level', lookup_expr='gte')
    level_lt = django_filters.NumberFilter(name='hierarchy__level', lookup_expr='lt')
    level_lte = django_filters.NumberFilter(name='hierarchy__level', lookup_expr='lte')

    class Meta:
        model = User
        fields = ['level_gt', 'level_gte', 'level_lt', 'level_lte', 'department']


class NewUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.select_related(
        'hierarchy', 'department', 'master__hierarchy').prefetch_related(
        'divisions'
    ).filter(is_active=True).order_by('last_name', 'first_name', 'middle_name')

    serializer_class = NewUserSerializer
    serializer_list_class = UserTableSerializer
    serializer_single_class = UserSingleSerializer

    pagination_class = UserPagination
    filter_backends = (filters.DjangoFilterBackend,
                       FieldSearchFilter,
                       filters.OrderingFilter,)
    permission_classes = (IsAuthenticated,)
    ordering_fields = ('first_name', 'last_name', 'middle_name',
                       'born_date', 'country', 'region', 'city', 'disrict', 'address', 'skype',
                       'phone_number', 'email', 'hierarchy__level', 'department__title',
                       'facebook', 'vkontakte', 'hierarchy_order', 'master__last_name',)
    field_search_fields = {
        'search_fio': ('last_name', 'first_name', 'middle_name'),
        'search_email': ('email',),
        'search_phone_number': ('phone_number',),
        'search_country': ('country',),
        'search_city': ('city',),
    }
    filter_class = UserFilter

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset
        if not user.hierarchy:
            return self.queryset.none()
        if user.hierarchy.level < 2:
            return user.get_descendants(include_self=True).select_related(
                'hierarchy', 'department', 'master__hierarchy').prefetch_related(
                'divisions'
            ).filter(is_active=True).order_by('last_name', 'first_name', 'middle_name')
        return self.queryset.all()

    def dispatch(self, request, *args, **kwargs):
        if kwargs.get('pk') == 'current' and request.user.is_authenticated():
            kwargs['pk'] = request.user.pk
        return super(NewUserViewSet, self).dispatch(request, *args, **kwargs)

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
        from .resources import get_disciples
        q = get_disciples(request.user)
        q = q.order_by('-hierarchy__level')
        queryset = self.filter_queryset(q)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.action == 'list':
            return self.serializer_list_class
        if self.action == 'retrieve':
            return self.serializer_single_class
        return self.serializer_class

    def perform_update(self, serializer):
        serializer.save()
        user = serializer.instance
        additional_phone = self.request.data.get('additional_phone', None)
        if additional_phone:
            phone_number = user.additional_phones.first()
            if phone_number:
                phone_number.number = additional_phone
                phone_number.save()
            else:
                AdditionalPhoneNumber.objects.create(user=user, number=additional_phone)
        elif additional_phone == '':
            phones = user.additional_phones.all()
            for phone in phones:
                phone.delete()

    @detail_route(methods=['get'])
    def summit_info(self, request, pk=None):
        summit_types = set(SummitType.objects.filter(summits__ankets__user_id=pk))
        lst = []
        for t in summit_types:
            json = {}
            summits = t.summits.filter(ankets__user_id=pk)
            json['name'] = t.title
            json['id'] = t.id
            json['summits'] = [
                {
                    'name': '{} {}'.format(t.title, summit.start_date),
                    'id': summit.id,
                    'description': summit.description,
                    'value': summit.ankets.get(user_id=pk).value,
                    'code': summit.ankets.get(user_id=pk).code,
                    'anket_id': summit.ankets.get(user_id=pk).id,
                    'user_fullname': summit.ankets.get(user_id=pk).user.fullname,
                }
                for summit in summits.all()]
            for s in json['summits']:
                current_user_anket = SummitAnket.objects.filter(
                    user=request.user, summit_id=s['id'], role__gte=SummitAnket.CONSULTANT)
                s['is_consultant'] = (
                    current_user_anket.exists() and SummitUserConsultant.objects.filter(
                        consultant=current_user_anket, user__user_id=pk, summit_id=s['id']).exists())
                lessons = SummitLesson.objects.filter(summit__ankets__user_id=pk, summit_id=s['id'])
                emails = AnketEmail.objects.filter(anket_id=s['anket_id'])
                notes = SummitAnketNote.objects.filter(summit_anket__user_id=pk, summit_anket_id=s['anket_id'])
                notes = notes.annotate(owner_name=Concat(
                    'owner__last_name', V(' '), 'owner__first_name', V(' '), 'owner__middle_name'))
                s['lessons'] = list(lessons.annotate(
                    is_view=Case(
                        When(viewers=s['anket_id'], then=True),
                        default=False,
                        output_field=BooleanField())).values())
                s['notes'] = list(notes.values())
                s['emails'] = list(emails.values('id', 'recipient', 'created_at'))
            lst.append(json)

        return Response(lst)


class UserShortViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserShortSerializer
    pagination_class = None
    permission_classes = (IsAuthenticated,)
    filter_backends = (filters.DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter,)
    # filter_fields = ('first_name', 'last_name', 'department', 'hierarchy')
    filter_class = ShortUserFilter
    search_fields = ('first_name', 'last_name', 'middle_name')


class LogoutView(RestAuthLogoutView):
    def logout(self, request):
        try:
            key = request._request.COOKIES.get('key', '')
            request.user.auth_tokens.filter(key=key).delete()
        except (AttributeError, ObjectDoesNotExist):
            pass

        django_logout(request)

        return Response({"success": _("Successfully logged out.")},
                        status=status.HTTP_200_OK)


# _check_all_recursion, _edit_user, self | create_user (view)
def _check_recursion(user, master):
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
            return True
        else:
            return _check_recursion(user, master.master)
    else:
        return False


# nobody
def _check_all_recursion():
    users = User.objects.all()
    for user in users:
        if user.master:
            _check_recursion(user, user.master)


def _check_user_exist(user_id):
    message = dict()
    user = User.objects.filter(id=user_id)
    if not user.exists():
        message['message'] = "Пользователя не существует"
        message['id'] = ''
        message['redirect'] = False

        return message, None
    return message, user.get()


def _check_user_level(user):
    if user.hierarchy and user.hierarchy.level == 7:
        message = {
            'message': "Нельзя редактировать Архонта",
            'status': False,
            'redirect': False
        }
        return message
    return {}


def _set_user_master(user, master_id):
    if master_id:
        master = User.objects.filter(id=master_id)
        if not master.exists():
            return user, {'message': "Не существует такого ответственного", 'status': False, 'redirect': False}
        master = master.get()
        if _check_recursion(user, master):
            message = {
                'message': "РЕКУРСИЯ!",
                'status': False,
                'redirect': False
            }
            return user, message
        user.master = master
    return user, {}


# create_user (view)
def _edit_user(user_id, data, files):
    message, user = _check_user_exist(user_id)
    if user is None:
        return None, message

    message = _check_user_level(user)
    if message:
        return None, message

    user, message = _set_user_master(user, data.get('master'))
    if message:
        return None, message

    user = _set_for_update_user_attrs(user, data)
    user = _set_user_image(user, files)
    user.save()
    message['message'] = "Пользователь успешно отредактирован"
    message['id'] = user.id
    message['redirect'] = True
    return user, message


def _is_user_exist(data):
    message = dict()
    if 'master' in data.keys():
        master = User.objects.get(id=data['master'])
        twink_user = User.objects.filter(
            first_name=data['first_name'], last_name=data['last_name'], master=master)
        if twink_user.exists():
            message['message'] = "Пользователь с таким именем и фамилией уже есть в базе данных"
            message['id'] = twink_user.get().id
            message['redirect'] = False

            return message, True
    return message, False


def _set_for_update_user_attrs(user, data):
    for key, value in six.iteritems(data):
        # m2m
        if key == 'additional_phone':
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
        elif key == 'divisions':
            for division in user.divisions.all():
                user.divisions.remove(division)
            for s in value:
                try:
                    division = Division.objects.get(id=s)
                    user.divisions.add(division)
                except Division.DoesNotExist:
                    pass

        # fk
        elif key in USER_FIELDS['fk']:
            setattr(user, key + '_id', value)
        elif key in USER_FIELDS['text_fields']:
            setattr(user, key, value)
        elif key in USER_FIELDS['date_fields']:
            setattr(user, key, value or None)
    return user


def _set_for_create_user_attrs(user, data):
    for key, value in six.iteritems(data):
        if key == 'additional_phone' and value:
            AdditionalPhoneNumber.objects.create(user=user, number=value)
        elif key == 'statuses':
            for s in value:
                status = Status.objects.filter(id=s).first()
                user.statuses.add(status)
        elif key == 'divisions':
            for s in value:
                division = Division.objects.filter(id=s).first()
                user.divisions.add(division)

        # fk
        elif key in USER_FIELDS['fk'] or key == 'master':
            setattr(user, key + '_id', value)
        elif key in USER_FIELDS['text_fields']:
            setattr(user, key, value)
        elif key in USER_FIELDS['date_fields']:
            setattr(user, key, value or None)
        else:
            setattr(user, key, value)
    return user


def _set_image_field(files, field_name):
    if files[field_name].name == 'blob':
        return files[field_name]
    else:
        import os
        ext = os.path.splitext(files[field_name].name)[1]
        valid_extensions = ['.jpg', '.png', '.jpeg']
        if ext in valid_extensions:
            return files[field_name]
    return None


def _set_user_image(user, files):
    if files:
        if "file" in files.keys():
            user.image = _set_image_field(files, 'file')
        if 'source' in files.keys():
            user.image_source = _set_image_field(files, 'source')
    return user


# create_user (view)
def _add_user(data, files, request):
    message, user_exist = _is_user_exist(data)
    if user_exist:
        return None, message

    email = data.get('email', '')
    username = email if email else 'user_' + generate_key()
    if User.objects.filter(username=username).exists():
        message = {
            'message': "Пользователь с таким логином (email) уже есть в базе данных",
            'id': User.objects.get(username=username).id,
            'redirect': False,
        }
        return None, message

    user = User(username=username, email=email,
                first_name=data['first_name'], last_name=data['last_name'])
    user = _set_for_create_user_attrs(user, data)
    user = _set_user_image(user, files)
    user.save()

    LastCall.objects.get_or_create(user=user)

    # serializer = UserSerializer(user, context={'request': request})
    # message['response'] = serializer.data
    message['message'] = "Пользователь успешно создан"
    message['id'] = user.id
    message['redirect'] = True
    return user, message


# create_user (view), send_password (view)
def _send_password_func(user_id):
    response_dict = dict()
    user = User.objects.filter(id=user_id).first()
    if user:
        password = generate_key()[:12]
        user.set_password(password)
        user.save()
        plaintext = get_template('email/register_email.txt')
        htmly = get_template('email/register_email.html')
        d = Context({'user': user, 'SITE_DOMAIN_URL': settings.SITE_DOMAIN_URL, 'password': password})
        subject, from_email, to = 'Подтверждение регистрации', settings.DEFAULT_FROM_EMAIL, user.email
        text_content = plaintext.render(d)
        html_content = htmly.render(d)
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        response_dict['message'] = "Пароль успешно отправлен"
    else:
        response_dict['message'] = "Пользователь не существует"
    return response_dict


# create_user (view)
def _create_partnership(data, user):
    data['value'] = data.get('value', 0)
    resp = data.pop('responsible')
    data['responsible_id'] = resp if resp and Partnership.objects.filter(id=resp).exists() else None

    Partnership.objects.create(user=user, **data)

    return {'message': "Партнерство успешно создано.",
            'status': True}


# create_user (view)
def _update_partnership(data, user):
    data['value'] = data.get('value', 0)
    resp = data.pop('responsible')
    data['responsible_id'] = resp if resp and Partnership.objects.filter(id=resp).exists() else None

    _, created = Partnership.objects.update_or_create(user=user, defaults=data)

    if created:
        return {'message': "Партнерство успешно создано.",
                'status': True}
    else:
        return {'message': "Партнерство успешно изменено.",
                'status': True}


# create_user (view)
def _change_password(request, data, response_dict):
    if 'old_password' in data.keys() and 'password1' in data.keys():
        if len(data['old_password']) > 0 and len(data['password1']) > 0:
            user = User.objects.filter(id=data['id']).first()
            if clean_old_password(user, data):
                if clean_password(data):
                    user.set_password(clean_password(data))
                    user.save()
                    update_session_auth_hash(request, user)
                    response_dict['special_message'] = 'Пароль успешно изменен'
                else:
                    response_dict['special_message'] = 'Введенные пароли не совпадают'
            else:
                response_dict['special_message'] = 'Вы ввели неверный пароль'
        return response_dict


def _create_user(request, data, files):
    user_fields = list()
    for k in USER_FIELDS.keys():
        user_fields += list(USER_FIELDS[k])
    user_data = {k: v for k, v in six.iteritems(data) if k in user_fields and v}
    if data.get('master', None):
        user_data['master'] = data['master']
    partner_data = {k: v for k, v in six.iteritems(data) if k in PARTNER_FIELDS}

    user, response_dict = _add_user(user_data, files, request)
    if user is None:
        return response_dict
    # if data['send_password']:
    #     _send_password_func(response_dict['id'])
    if 'responsible' in partner_data.keys():
        _create_partnership(partner_data, user)
        response_dict['special_message'] = 'Партнерство успешно создано'
    return response_dict


def _update_user(request, data, files):
    user_fields = list()
    for k in USER_FIELDS.keys():
        user_fields += list(USER_FIELDS[k])
    user_data = {k: v for k, v in six.iteritems(data) if k in user_fields}
    partner_data = {k: v for k, v in six.iteritems(data) if k in PARTNER_FIELDS}

    user, response_dict = _edit_user(data.get('id'), user_data, files)
    if user is None:
        return response_dict
    # response_dict = _change_password(request, data, response_dict)
    if 'responsible' in partner_data.keys():
        _update_partnership(partner_data, user)
        response_dict['special_message'] = 'Партнерство успешно изменено'
    return response_dict


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


def logout_view(request):
    django_logout(request)
    return HttpResponseRedirect(reverse('entry'))


@api_view(['POST'])
def create_user(request):
    if request.user.is_staff:
        data, files = request.data, request.FILES
        if 'id' in data.keys():
            response_dict = _update_user(request, data, files)
        else:
            response_dict = _create_user(request, data, files)
    else:
        response_dict = {
            'message': "Нет полномочий",
            'redirect': False
        }
    return Response(response_dict)


@api_view(['POST'])
def password_forgot(request):
    data = request.data
    email = data['email']
    response_dict = dict()
    if len(email) > 0:
        try:
            user = User.objects.get(email=email)
            user.activation_key = generate_key()
            user.save()
            plaintext = get_template('email/password_reset.txt')
            htmly = get_template('email/password_reset.html')
            d = Context({'user': user, 'site_url': settings.SITE_DOMAIN_URL[:-1]})
            subject, from_email, to = 'Восстановление пароля', settings.DEFAULT_FROM_EMAIL, user.email
            text_content = plaintext.render(d)
            html_content = htmly.render(d)
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            response_dict[
                'message'] = "Вам на почту было отправлено письмо с дальнейшими инструкциями по восстановлению пароля"
            response_dict['status'] = True
        except User.DoesNotExist:
            response_dict['message'] = "Пользователя с таким email не существует"
            response_dict['status'] = False
    else:
        response_dict['message'] = "Поле email обязательно"
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
            response_dict['message'] = "Пароль успешно изменен"
            response_dict['status'] = True
        else:
            response_dict['message'] = "Пароли не совпадают"
            response_dict['status'] = False
    except User.DoesNotExist:
        response_dict['message'] = "Ключ активации несуществует или устарел"
        response_dict['status'] = False
    return Response(response_dict)


@api_view(['POST'])
def ping_user_key(request):
    data = request.data
    get_object_or_404(Token, key=data['key'])
    return Response({'status': 'ok'})


# TODO delete this
@api_view(['POST'])
def send_password(request):
    response_dict = dict()
    if request.method == 'POST':
        data = request.data
        response_dict = _send_password_func(data['id'])
    return Response(response_dict)


# TODO delete this
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
            response_dict['message'] = "Фото успешно загружено"
            response_dict['redirect'] = False
            response_dict['status'] = True
    except User.DoesNotExist:
        response_dict['message'] = "Нет такого пользователя"
        response_dict['redirect'] = False
        response_dict['status'] = False
    return Response(response_dict)


# TODO delete this
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
            response_dict['message'] = 'Пароль успешно изменен'
            response_dict['status'] = True
        else:
            response_dict['message'] = 'Введенные пароли не совпадают'
            response_dict['status'] = False
    else:
        response_dict['message'] = 'Вы ввели неверный пароль'
        response_dict['status'] = False
    return Response(response_dict)


# TODO delete this
@api_view(['POST'])
def delete_user(request):
    """
    Deleting a user, selected by id

    :param request: data{'id': int}
    :return: {'message': string, 'status': boolean}
    """
    warnings.warn(
        "`delete_user method` is deprecated", None, 2
    )
    response_dict = dict()
    data = request.data
    try:
        user = User.objects.get(id=data['id'])
        archons = User.objects.filter(hierarchy__level=7).all()
        if user in archons.all():
            response_dict['message'] = "Нельзя удалить Архонта"
            response_dict['status'] = False
            response_dict['redirect'] = False
            return Response(response_dict)
        user.delete()
        response_dict['message'] = "Пользователь был удален успешно"
        response_dict['status'] = True
    except User.DoesNotExist:
        response_dict['message'] = "Пользователь не существует"
        response_dict['status'] = False
    return Response(response_dict)
