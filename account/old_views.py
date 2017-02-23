import binascii
import os

from django.conf import settings
from django.contrib.auth import update_session_auth_hash, authenticate, login
from django.core.mail import EmailMultiAlternatives
from django.template import Context
from django.template.loader import get_template
from django.utils import six
from rest_framework import viewsets, filters
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from account.models import CustomUser as User
from account.resources import clean_old_password, clean_password
from account.serializers import UserSerializer
from partnership.models import Partnership
from status.models import Division, Status


USER_FIELDS = {
    'text_fields': {
        # 'username',
        'email',
        'search_name',
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
        'master',
    },
    'm2m': {
        'divisions',
    }
}
PARTNER_FIELDS = (
    'responsible', 'date', 'value'
)


def generate_key():
    return binascii.hexlify(os.urandom(20)).decode()


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
        if key == 'divisions':
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
        if key == 'statuses':
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

    # serializer = UserSerializer(user, context={'request': request})
    # message['response'] = serializer.data
    message['message'] = "Пользователь успешно создан"
    message['id'] = user.id
    message['redirect'] = True
    return user, message


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


def _create_partnership(data, user):
    data['value'] = data.get('value', 0)
    resp = data.pop('responsible')
    data['responsible_id'] = resp if resp and Partnership.objects.filter(id=resp).exists() else None

    Partnership.objects.create(user=user, **data)

    return {'message': "Партнерство успешно создано.",
            'status': True}


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