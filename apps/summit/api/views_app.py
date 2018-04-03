import json
import logging
from datetime import datetime, timedelta

import pytz
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, ExpressionWrapper, F, IntegerField, Q
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django_filters import rest_framework
from rest_framework import mixins, viewsets, exceptions, status
from rest_framework.decorators import list_route, api_view, detail_route
from rest_framework.generics import get_object_or_404, GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.account.models import CustomUser
from apps.account.api.permissions import IsSuperUser
from common.exception import InvalidRegCode
from common.filters import FieldSearchFilter
from common.test_helpers.utils import get_real_user
from common.views_mixins import ModelWithoutDeleteViewSet
from apps.notification.backend import RedisBackend
from apps.summit.regcode import decode_reg_code
from apps.summit.models import (
    SummitType, SummitAnket, AnketStatus, Summit, SummitVisitorLocation, SummitAttend, SummitEventTable,
    AnketPasses, TelegramPayment)
from apps.summit.api.permissions import HasAPIAccess
from apps.summit.api.serializers import (
    SummitTypeForAppSerializer, SummitAnketForAppSerializer, SummitProfileTreeForAppSerializer,
    SummitVisitorLocationSerializer, SummitAnketCodeSerializer, SummitAttendSerializer,
    SummitAcceptMobileCodeSerializer, AnketActiveStatusSerializer, SummitEventTableSerializer,
    SummitAnketDrawForAppSerializer, SummitNameAnketCodeSerializer, OpenSummitsForAppSerializer,
    TelegramPaymentSerializer)
from apps.partnership.models import TelegramGroup

logger = logging.getLogger(__name__)


class SummitTypeForAppViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = SummitType.objects.prefetch_related('summits')
    serializer_class = SummitTypeForAppSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class SummitProfileWithLess10AbsentForAppViewSet(mixins.ListModelMixin,
                                                 mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = SummitAnket.objects.select_related('user', 'master__hierarchy', 'status').order_by('id')
    serializer_class = SummitAnketDrawForAppSerializer
    filter_backends = (rest_framework.DjangoFilterBackend,)
    permission_classes = (HasAPIAccess,)
    pagination_class = None
    filter_fields = ('summit',)

    def get_queryset(self):
        return super().get_queryset().annotate(c=Count('attends')).filter(c__gte=10)


class SummitProfileForAppViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = SummitAnket.objects.select_related('user', 'master__hierarchy', 'status').order_by('id')
    serializer_class = SummitAnketForAppSerializer
    filter_backends = (rest_framework.DjangoFilterBackend,)
    permission_classes = (HasAPIAccess,)
    pagination_class = None
    filter_fields = ('summit',)

    @list_route(methods=['GET'])
    def by_reg_code(self, request):
        reg_code = request.query_params.get('reg_code', '').lower().strip()
        code_error_message = {
            'detail': _('Невозможно получить объект. Передан некорректный регистрационный код'),
            'error': 1
        }

        try:
            visitor_id = decode_reg_code(reg_code)
            visitor = SummitAnket.objects.get(pk=visitor_id)
        except (ValueError, TypeError):
            return Response(data=code_error_message, status=status.HTTP_400_BAD_REQUEST)
        except InvalidRegCode:
            return Response(data=code_error_message, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response(data=code_error_message, status=status.HTTP_400_BAD_REQUEST)

        device_id = request.META.get(settings.APP_DEVICE_ID_FIELD)
        r = RedisBackend()
        exist_device_id = r.get(reg_code)

        if not exist_device_id:
            r.set(reg_code, device_id)
            r.expire(reg_code, settings.APP_DEVICE_ID_EXPIRE)
        elif device_id != exist_device_id.decode('utf8'):
            return Response(data={
                'detail': _('Этот регистрационный код уже был использован на другом устройстве.'),
                'error': 2
            }, status=status.HTTP_400_BAD_REQUEST)

        if visitor.reg_code != reg_code:
            return Response(data=code_error_message, status=status.HTTP_400_BAD_REQUEST)

        AnketStatus.objects.get_or_create(
            anket=visitor, defaults={'reg_code_requested': True,
                                     'reg_code_requested_date': timezone.now()})
        # visitor.ticket_status = SummitAnket.GIVEN
        # visitor.save()

        visitor = self.get_serializer(visitor)
        return Response(visitor.data, status=status.HTTP_200_OK)

    @detail_route(methods=['POST'], permission_classes=(IsSuperUser,))
    def reset_device_id(self, request, pk):
        profile = self.get_object()
        r = RedisBackend()
        r.delete(profile.reg_code)
        return Response(data={'detail': profile.reg_code})

    @list_route(methods=['GET'])
    def by_reg_date(self, request):
        from_date = request.query_params.get('from_date', timezone.now().date() - timedelta(days=1))
        to_date = request.query_params.get('to_date', timezone.now().date() - timedelta(days=1))
        if isinstance(from_date, str):
            from_date = pytz.utc.localize(datetime.strptime(from_date, '%Y-%m-%d')).date()
        if isinstance(to_date, str):
            to_date = pytz.utc.localize(datetime.strptime(to_date, '%Y-%m-%d')).date()

        if from_date > to_date:
            raise exceptions.ValidationError('Некорректно заданный временной интвервал. ')

        profiles = SummitAnket.objects.filter(
            status__reg_code_requested_date__date__range=[from_date, to_date]).order_by(
            'status__reg_code_requested_date')
        profiles = self.serializer_class(profiles, many=True)
        return Response(profiles.data, status=status.HTTP_200_OK)

    @list_route(methods=['GET'], serializer_class=SummitNameAnketCodeSerializer,
                permission_classes=(IsAuthenticated,))
    def get_tickets(self, request):
        user_id = request.query_params.get('user_id')
        user = get_object_or_404(CustomUser, pk=user_id)
        # anket = SummitAnket.objects.filter(user=user).order_by('-summit__start_date').first()
        # anket = self.serializer_class(anket)
        ankets = SummitAnket.objects.filter(user=user).filter(summit__status=Summit.OPEN)
        ankets = self.serializer_class(ankets, many=True)

        return Response(ankets.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def app_request_count(request, summit_id):
    profiles = SummitAnket.objects.filter(summit_id=summit_id).values_list(
        'status__reg_code_requested', flat=True)
    total = len(profiles)
    requested = len(list(filter(lambda p: p, profiles)))
    return Response({'total': total, 'requested': requested})


class SummitProfileTreeForAppListView(mixins.ListModelMixin, GenericAPIView):
    serializer_class = SummitProfileTreeForAppSerializer
    pagination_class = None
    permission_classes = (IsAuthenticated,)

    filter_backends = (
        FieldSearchFilter,
    )

    field_search_fields = {
        'search_fio': ('last_name', 'first_name', 'middle_name', 'search_name'),
    }

    summit = None
    master_id = None

    def get(self, request, *args, **kwargs):
        self.summit = get_object_or_404(Summit, pk=kwargs.get('summit_id', None))
        self.master_id = kwargs.get('master_id', None)
        return self.list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(queryset, many=True)
        profiles = serializer.data

        locations = self.get_locations({p['id'] for p in profiles})
        self._set_profile_visitor_locations(profiles, locations)

        return Response({
            'profiles': profiles,
        })

    @staticmethod
    def annotate_queryset(qs):
        return qs.select_related('status').base_queryset().annotate_full_name().annotate(
            numchild=ExpressionWrapper(F('user__numchild'), output_field=IntegerField()),
        ).order_by(
            '-hierarchy__level', 'last_name', 'first_name', 'middle_name')

    def get_queryset(self):
        is_consultant_or_high = self.request.user.is_summit_consultant_or_high(self.summit)
        if self.master_id is not None:
            if is_consultant_or_high:
                return self.annotate_queryset(self.summit.ankets.filter(user__master_id=self.master_id))
            return self.annotate_queryset(self.summit.ankets.filter(
                user__master_id=self.master_id
            ))
        elif is_consultant_or_high:
            return self.annotate_queryset(self.summit.ankets.filter(user__depth=1))
        else:
            return self.annotate_queryset(self.summit.ankets.filter(user__master_id=self.request.user.id))

    def get_locations(self, ids):
        start_date, end_date = self._get_start_and_end_date()
        locations = SummitVisitorLocation.objects.filter(visitor__in=ids, date_time__range=(start_date, end_date))
        return locations.values('visitor_id', 'date_time', 'longitude', 'latitude', 'type')

    def _get_start_and_end_date(self):
        """
        If:
            http://example.com/?date_time=2000-02-24T11:33:55+0000&interval=7
        Then returns:
            start_date == datetime(2000, 2, 24, 11, 26, 55, tzinfo=pytz.utc)
            end_date == datetime(2000, 2, 24, 11, 40, 55, tzinfo=pytz.utc)

        Defaults:
            interval == 5 min
            start_date == NOW - 2 * `interval`
            end_date == NOW

        :return: datetime of start_date, end_date
        """
        date_time = self.request.query_params.get('date_time', '')
        interval = int(self.request.query_params.get('interval', 5))
        try:
            date_time = datetime.strptime(date_time.replace('T', ' '), '%Y-%m-%d %H:%M:%S%z')
        except ValueError as err:
            end_date = timezone.now()
            start_date = end_date - timedelta(minutes=2 * interval)
        else:
            start_date = date_time - timedelta(minutes=interval)
            end_date = date_time + timedelta(minutes=interval)

        return start_date, end_date

    @staticmethod
    def _set_profile_visitor_locations(profiles, locations):
        """
        If profile['id'] == location['visitor_id'], then:
        ========================================================
        FROM
            profiles = [
                {
                    'id': 124,
                    'other_field': 'something',
                },
            ]
            locations = [
                {
                    'visitor_id': 124,
                    'location_field': 'my_location',
                },
            ]
        TO
            profiles = [
                {
                    'id': 124,
                    'other_field': 'something',
                    'visitor_locations': {  # ADDED
                        'visitor_id': 124,
                        'location_field': 'my_location',
                    },
                },
            ]
        ========================================================
        :param profiles: list of profiles (dicts)
        :param locations: list of locations (dicts)
        :return:
        """
        for p in profiles:
            p['visitor_locations'] = None
            for l in locations:
                if l['visitor_id'] == p['id']:
                    p['visitor_locations'] = l
                    break


class SummitVisitorLocationViewSet(viewsets.ModelViewSet):
    serializer_class = SummitVisitorLocationSerializer
    queryset = SummitVisitorLocation.objects.all().prefetch_related('visitor')
    pagination_class = None
    permission_classes = (HasAPIAccess,)

    @list_route(methods=['POST'])
    def post(self, request):
        if not request.data.get('data'):
            user = get_real_user(request)
            logger.warning({
                'user': user.id if user else None,
                'message': _('Невозможно создать запись, поле {data} не переданно')
            })
            raise exceptions.ValidationError(_('Невозможно создать запись, поле {data} не переданно'))
        data = request.data.get('data')
        visitor = get_object_or_404(SummitAnket, pk=request.data.get('visitor_id'))

        for chunk in data:
            SummitVisitorLocation.objects.get_or_create(
                visitor=visitor,
                date_time=chunk.get('date_time', timezone.now()),
                defaults={
                    'longitude': chunk.get('longitude', 0),
                    'latitude': chunk.get('latitude', 0),
                    'type': chunk.get('type', 1)
                })

        return Response({'message': 'Successful created'}, status=status.HTTP_201_CREATED)

    @list_route(methods=['GET'])
    def get_location(self, request):
        anket_id = request.query_params.get('visitor_id')
        date_time = request.query_params.get('date_time')
        visitor_location = self.queryset.filter(visitor_id=anket_id, date_time__gte=date_time).order_by(
            'date_time').first()
        visitor_location = self.serializer_class(visitor_location)

        return Response(visitor_location.data, status=status.HTTP_200_OK)

    @list_route(methods=['GET'])
    def location_by_interval(self, request):
        date_time = request.query_params.get('date_time')
        date_format = '%Y-%m-%d %H:%M:%S%z'
        try:
            date_time = pytz.utc.localize(datetime.strptime(date_time.replace('T', ' '), date_format))
        except ValueError:
            raise exceptions.ValidationError(
                'Не верный формат даты. Передайте дату в формате date %s' % date_format)

        interval = int(request.query_params.get('interval', 0))
        start_date = date_time - timedelta(minutes=interval)
        end_date = date_time + timedelta(minutes=interval)

        locations = self.queryset.filter(date_time__range=(start_date, end_date))
        locations = self.serializer_class(locations, many=True)

        return Response(locations.data, status=status.HTTP_200_OK)

    @list_route(methods=['GET'])
    def location_by_date(self, request):
        anket_id = request.query_params.get('visitor_id')
        date = request.query_params.get('date')
        visitor_locations = self.queryset.filter(visitor_id=anket_id, date_time__date=date)
        visitor_locations = self.serializer_class(visitor_locations, many=True)

        return Response(visitor_locations.data, status=status.HTTP_200_OK)


class SummitAttendViewSet(ModelWithoutDeleteViewSet):
    queryset = SummitAttend.objects.prefetch_related('anket')
    serializer_class = SummitAnketCodeSerializer
    serializer_list_class = SummitAttendSerializer
    permission_classes = (HasAPIAccess,)

    def get_serializer_class(self):
        if self.action == 'list':
            return self.serializer_list_class
        return self.serializer_class

    @list_route(methods=['POST', 'GET'])
    def confirm_attend(self, request):
        code = request.data.get('code')
        date = request.data.get('date')
        anket = get_object_or_404(SummitAnket, code=code)
        self.validate_data(request.data)
        SummitAttend.objects.create(anket=anket, date=date)

        return Response({'message': 'Attend have been successful confirmed'}, status=status.HTTP_201_CREATED)

    @staticmethod
    def validate_data(data):
        anket = get_object_or_404(SummitAnket, code=data.get('code'))
        date_today = timezone.now().date()
        if SummitAttend.objects.filter(anket_id=anket.id, date=date_today).exists():
            raise exceptions.ValidationError(
                _('Запись о присутствии этой анкеты за сегоднящней день уже существует'))

    @list_route(methods=['GET'], serializer_class=SummitAcceptMobileCodeSerializer)
    def accept_mobile_code(self, request):
        code = request.query_params.get('code', '')
        summit_id = request.query_params.get('summit_id')
        if not (code and summit_id):
            raise exceptions.ValidationError(
                {'message': 'Params {code} and {summit_id} must be passed'}
            )

        anket = get_object_or_404(SummitAnket, code=code, summit_id=summit_id)
        AnketStatus.objects.get_or_create(
            anket=anket, defaults={'reg_code_requested': True,
                                   'reg_code_requested_date': timezone.now()})

        if anket.status.active:
            SummitAttend.objects.get_or_create(anket=anket, date=timezone.now().date())
            AnketPasses.objects.create(anket=anket)

        anket = self.serializer_class(anket)
        return Response(anket.data)

    @list_route(methods=['POST'], serializer_class=AnketActiveStatusSerializer,
                permission_classes=(IsAuthenticated,))
    def anket_active_status(self, request):
        active = request.data.get('active', 1)
        anket_id = request.data.get('anket_id', None)
        anket = get_object_or_404(SummitAnket, pk=anket_id)
        AnketStatus.objects.get_or_create(anket=anket)

        if active:
            anket.status.active = True
        if not active:
            anket.status.active = False
        anket.status.save()

        return Response({'message': _('Статус анкеты пользователя {%s} успешно изменен.') % anket.fullname,
                         'active': '%s' % anket.status.active}, status=status.HTTP_200_OK)

    @list_route(methods=['GET'], permission_classes=(HasAPIAccess,))
    def add_to_telegram_group(self, request):
        phone_number = request.query_params.get('phone_number')
        if not phone_number or len(phone_number) < 10:
            raise exceptions.ValidationError({'message': 'Parameter {phone_number} must be passed'})

        phone_number = phone_number[-10:]
        data = {'join_url': None}

        visitor = CustomUser.objects.filter(hierarchy__level__gte=1).filter(Q(
            phone_number__contains=phone_number) | Q(
            extra_phone_numbers__contains=[phone_number])).first()

        if visitor:
            telegram_group = TelegramGroup.objects.get(title='Leaders')
            data['join_url'] = telegram_group.join_url

        return Response(data, status=status.HTTP_200_OK)


class SummitEventTableViewSet(viewsets.ModelViewSet):
    queryset = SummitEventTable.objects.all()
    serializer_class = SummitEventTableSerializer
    permission_classes = (HasAPIAccess,)
    filter_backends = (rest_framework.DjangoFilterBackend,)
    filter_fields = ('summit',)
    pagination_class = None


class OpenSummitsForAppViewSet(viewsets.ModelViewSet):
    queryset = Summit.objects.all()
    serializer_class = OpenSummitsForAppSerializer
    permission_classes = (HasAPIAccess,)
    filter_backends = (rest_framework.DjangoFilterBackend,)
    pagination_class = None

    def get_queryset(self):
        return self.queryset.filter(status=Summit.OPEN)


class TelegramPaymentsViewSet(viewsets.ModelViewSet):
    queryset = TelegramPayment.objects.all()
    serializer_class = TelegramPaymentSerializer
    permission_classes = (IsAuthenticated,)
