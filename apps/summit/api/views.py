import collections
import logging
from collections import defaultdict
from datetime import datetime, time, date
from typing import NamedTuple, List

import pytz
from celery.result import AsyncResult
from django.conf import settings
from django.db import transaction, IntegrityError, connection
from django.db.models import (
    Case, When, BooleanField, F, Subquery, OuterRef, CharField,
    Func, Q, Exists, IntegerField)
from django.db.models import Value as V
from django.db.models.functions import Concat, Coalesce
from django.http import HttpResponse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _, ugettext
from django_filters import rest_framework
from rest_framework import exceptions, viewsets, filters, status, mixins
from rest_framework.decorators import action, api_view
from rest_framework.generics import get_object_or_404, GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.viewsets import GenericViewSet

from apps.account.models import CustomUser
from apps.account.signals import obj_add, obj_delete
from apps.analytics.utils import model_to_dict
from apps.notification.backend import RedisBackend
from apps.payment.api.serializers import PaymentShowWithUrlSerializer
from apps.payment.api.views_mixins import CreatePaymentMixin, ListPaymentMixin
from apps.summit.api.filters import (
    FilterByClub, SummitUnregisterFilter, ProfileFilter,
    HasPhoto, FilterBySummitAttend,
    FilterBySummitAttendByDate, FilterByElecTicketStatus, FilterByTime, FilterByDepartment,
    FilterByMasterTree, FilterByHasEmail, FilterIsPartner, FilterHasAchievement, FilterProfileAuthorTree, AuthorFilter,
    FilterByTicketMultipleStatus, ProfileFilterByPaymentStatus, FilterByRegCode)
from apps.summit.api.pagination import (
    SummitPagination, SummitTicketPagination, SummitStatisticsPagination, SummitSearchPagination)
from apps.summit.api.permissions import HasAPIAccess, CanSeeSummitProfiles, can_download_summit_participant_report, \
    can_see_report_by_bishop_or_high
from apps.summit.api.serializers import (
    SummitSerializer, SummitUnregisterUserSerializer, SummitAnketSerializer,
    SummitAnketNoteSerializer, SummitLessonSerializer,
    SummitAnketForSelectSerializer,
    SummitShortSerializer, SummitAnketShortSerializer, SummitLessonShortSerializer, SummitTicketSerializer,
    SummitAnketForTicketSerializer, SummitAnketCodeSerializer,
    SummitAnketStatisticsSerializer,
    MasterSerializer, SummitProfileUpdateSerializer, SummitProfileCreateSerializer, ProfileTableSerializer)
from apps.summit.models import (
    Summit, SummitAnket, SummitLesson, SummitUserConsultant, SummitTicket, SummitAttend, AnketEmail)
from apps.summit.resources import SummitAnketResource, SummitStatisticsResource
from apps.summit.tasks import generate_tickets, send_email_with_code, send_email_with_schedule
from apps.summit.utils import get_report_by_bishop_or_high, \
    FullSummitParticipantReport, SummitTicketPDF
from common.filters import FieldSearchFilter, OrderingFilterWithPk
from common.test_helpers.utils import get_real_user
from common.views_mixins import ModelWithoutDeleteViewSet, ExportViewSetMixin, TableViewMixin

logger = logging.getLogger(__name__)


class Attend(NamedTuple):
    date: date
    time: time
    created_at: datetime


sent_pulse_emails = {
    9: {34816, 32770, 32784, 32788, 32791, 32792, 32800, 32804, 32810, 32814, 32823, 32828, 32830, 32837, 32838, 32839,
        32843, 32846, 32848, 32852, 32856, 32863, 32868, 32873, 32876, 32880, 32884, 32885, 32902, 32906, 32915, 32916,
        32919, 32925, 32933, 32958, 32961, 32970, 32980, 32984, 32986, 32991, 32998, 33007, 33011, 33024, 33025, 33028,
        33032, 33039, 33041, 33046, 33047, 33050, 33060, 33061, 33062, 33063, 33065, 33069, 33071, 33073, 33075, 33076,
        33077, 33082, 33092, 33095, 33096, 33098, 33099, 33105, 33111, 33114, 33118, 33119, 33123, 33132, 33133, 33137,
        33139, 33144, 33148, 33159, 33160, 33164, 33170, 33171, 33175, 33176, 33178, 33188, 33193, 33198, 31167, 33218,
        33219, 33221, 33226, 33227, 33228, 33240, 31194, 31197, 33246, 33254, 33255, 33256, 31213, 33264, 33267, 33270,
        33273, 33275, 33276, 31227, 33289, 33290, 33297, 31251, 33313, 33317, 33318, 33325, 33328, 33331, 33342, 33343,
        33360, 33362, 33366, 33368, 33373, 33376, 33380, 33385, 33388, 33389, 33399, 33405, 33411, 33429, 33438, 33439,
        33445, 33458, 31416, 33464, 33466, 33469, 33470, 33471, 33474, 33477, 33480, 33489, 33491, 31444, 31445, 33496,
        31454, 33508, 33511, 33517, 33520, 31490, 33559, 31516, 31517, 31521, 31524, 31528, 31530, 31532, 31538, 31540,
        33591, 33592, 31547, 33597, 31549, 31552, 31553, 31557, 33611, 33612, 31570, 31574, 31576, 31577, 31579, 31584,
        31588, 31589, 31591, 31594, 31598, 33646, 31601, 31606, 31609, 31610, 31611, 31620, 31622, 31628, 31630, 31635,
        31638, 31639, 33693, 33696, 33702, 31659, 33714, 31667, 31683, 33732, 31685, 33741, 31696, 31698, 31704, 31706,
        31708, 31710, 31712, 31716, 33764, 31718, 31719, 31720, 31722, 31723, 31727, 31734, 33786, 31740, 31743, 31746,
        31749, 31750, 31751, 33797, 31755, 31758, 31760, 31761, 33811, 31766, 31768, 31770, 31771, 31774, 31780, 31784,
        31788, 33838, 33841, 31795, 31796, 31798, 31800, 31801, 31809, 31818, 31819, 31824, 31828, 31829, 31830, 31832,
        31837, 31839, 31840, 31843, 31845, 31846, 31850, 31851, 33898, 31856, 31859, 31861, 31862, 31863, 31864, 31868,
        31871, 31873, 31875, 31881, 31886, 31889, 31898, 31903, 33952, 31910, 31911, 31913, 31914, 31919, 33968, 31927,
        31929, 33989, 33991, 31951, 31960, 31964, 31967, 31968, 31971, 31976, 31978, 31980, 31983, 31992, 32006, 34058,
        34074, 32029, 32030, 32033, 32035, 32038, 34087, 32045, 32049, 32052, 32056, 32058, 32059, 32061, 32062, 34112,
        32065, 32064, 32068, 34120, 32073, 34122, 32075, 32079, 34132, 32087, 32088, 32097, 34156, 34157, 32122, 32126,
        34176, 32133, 34184, 32136, 34189, 34190, 34197, 32150, 34199, 32152, 32156, 32163, 32166, 34214, 32173, 34222,
        32174, 34223, 34226, 34231, 32185, 32186, 32187, 34235, 32189, 32190, 34243, 32196, 34244, 32199, 32201, 34252,
        32206, 34256, 34259, 32214, 32216, 32218, 32220, 34273, 32226, 32228, 34280, 32239, 32240, 32242, 32247, 34295,
        34298, 34302, 34303, 34304, 32257, 34305, 32259, 32260, 32261, 34313, 32265, 32268, 32269, 32270, 32273, 32274,
        32283, 32284, 32285, 34331, 34336, 32289, 32290, 34337, 32295, 32298, 34350, 34351, 34353, 32311, 32312, 32322,
        32323, 32324, 34374, 34380, 32337, 32338, 32339, 34392, 32346, 34395, 32349, 32350, 34397, 34398, 34401, 32354,
        34405, 32358, 32359, 32360, 34408, 34409, 32365, 34418, 34421, 32373, 34428, 34429, 34430, 32387, 32388, 34439,
        32393, 32394, 32401, 34450, 34451, 32408, 32410, 34458, 32417, 32418, 34469, 32424, 34474, 32427, 32429, 34478,
        34480, 32433, 34483, 34484, 32436, 32437, 32449, 34499, 34500, 34508, 34509, 32463, 32464, 32470, 32472, 32473,
        32476, 34524, 32480, 34531, 34532, 32485, 32487, 32492, 34542, 34545, 34546, 32501, 34551, 32504, 32506, 32508,
        34562, 32515, 32517, 32519, 34571, 32525, 32526, 32528, 32534, 32535, 34583, 34584, 34586, 34587, 32541, 32543,
        34592, 34593, 32550, 32553, 32555, 34606, 34607, 32560, 32561, 34610, 32563, 34611, 34613, 32568, 32572, 32576,
        32578, 32587, 32588, 32590, 32592, 32594, 32598, 32599, 32600, 32609, 32613, 32621, 32622, 32626, 32630, 32637,
        32640, 32644, 32650, 32655, 32660, 32676, 34736, 34737, 34738, 34742, 32703, 32707, 34760, 32712, 32713, 32723,
        32726, 32732, 34783, 34787, 32739, 34789, 32742, 32745, 32748, 34797, 34798, 34802, 34804, 32759, 34809, 32762,
        32764, 32766, 34815}}


def get_success_headers(data):
    try:
        return {'Location': data[api_settings.URL_FIELD_NAME]}
    except (TypeError, KeyError):
        return {}


class SummitAuthorListView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    filter_backends = (
        rest_framework.DjangoFilterBackend,
        FieldSearchFilter,
        FilterProfileAuthorTree,
    )
    field_search_fields = {
        'search_fio': ('last_name', 'first_name', 'middle_name', 'search_name'),
    }
    filter_class = AuthorFilter
    pagination_class = None

    summit = None

    def get(self, request, *args, **kwargs):
        """
        First 100 bishops+ of summit
        """
        self.summit = get_object_or_404(Summit, pk=kwargs.get('pk'))
        authors = self.filter_queryset(self.get_queryset().order_by('last_name', 'first_name', 'middle_name', 'pk'))
        authors = [{'id': p[0], 'title': p[1]} for p in authors.values_list('user_id', 'full_name')[:100]]
        return Response(data=authors)

    def get_queryset(self):
        return self.summit.ankets.filter(
            hierarchy__level__gte=4  # bishop+
        ).order_by('last_name', 'first_name', 'middle_name', 'pk').annotate_full_name()


class SummitProfileListMixin(mixins.ListModelMixin, GenericAPIView):
    summit = None

    def dispatch(self, request, *args, **kwargs):
        self.summit = get_object_or_404(Summit, pk=kwargs.get('pk', None))
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def check_permissions(self, request):
        super().check_permissions(request)
        # ``summit`` consultant or high
        if not CanSeeSummitProfiles().has_object_permission(request, self, self.summit):
            self.permission_denied(
                request, message=getattr(CanSeeSummitProfiles, 'message', None)
            )


class SummitProfileListView(TableViewMixin, SummitProfileListMixin):
    table_name = 'summit'
    serializer_class = ProfileTableSerializer
    pagination_class = SummitPagination
    permission_classes = (IsAuthenticated,)

    filter_class = ProfileFilter
    ordering_fields = (
        'first_name', 'last_name', 'responsible', 'author__last_name',
        'spiritual_level', 'divisions_title', 'department', 'user__facebook', 'country', 'city',
        'code', 'value', 'description',
        'middle_name', 'user__born_date', 'country',
        'user__region', 'city', 'user__district',
        'user__address', 'user__phone_number',
        'user__email', 'hierarchy__level', 'ticket_status', 'status__reg_code_requested', 'has_email'
    )
    filter_backends = (
        rest_framework.DjangoFilterBackend,
        OrderingFilterWithPk,
        FieldSearchFilter,
        FilterProfileAuthorTree,
        FilterByClub,
        HasPhoto,
        FilterByRegCode,
        FilterByHasEmail,
        FilterIsPartner,
        FilterHasAchievement,
        FilterBySummitAttend,
        FilterByElecTicketStatus,
        FilterByTicketMultipleStatus,
        ProfileFilterByPaymentStatus,
    )

    field_search_fields = {
        'search_fio': ('last_name', 'first_name', 'middle_name', 'search_name', 'code'),
        'search_email': ('user__email',),
        'search_phone_number': ('user__phone_number',),
        'search_country': ('country',),
        'search_city': ('city',),
    }

    def get(self, request, *args, **kwargs):
        """
        Getting list of summit profiles for table


        By default ordering by ``last_name``, ``first_name``, ``middle_name``.
        Pagination by 30 profiles per page.
        """
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        select_related = {'user'}
        qs = self.summit.ankets.order_by(
            'user__last_name', 'user__first_name', 'user__middle_name', 'pk')
        other_summits = SummitAnket.objects.filter(
            user_id=OuterRef('user_id'),
            summit__type_id=self.summit.type_id,
            summit__status=Summit.CLOSE
        ).only('id')
        qs = qs.annotate(has_achievement=Exists(other_summits))
        qs = qs.annotate_full_name()

        if 'has_email' in [k for k, v in self.columns.items() if v['active']]:
            emails = AnketEmail.objects.filter(anket=OuterRef('pk'), is_success=True).only('id')
            qs = qs.annotate(has_email=Exists(emails))
        if ('total_sum' in [k for k, v in self.columns.items() if v['active']] or
                'payment_status' in self.request.query_params):
            qs = qs.annotate_total_sum()
        if 'e_ticket' in [k for k, v in self.columns.items() if v['active']]:
            select_related.add('status')
        if 'author' in [k for k, v in self.columns.items() if v['active']]:
            select_related.add('author')
        if 'payment_status' in self.request.query_params:
            qs = qs.annotate(
                payment_status=Case(
                    When(Q(total_sum__lt=self.summit.full_cost) & Q(total_sum__gt=0), then=1),
                    When(total_sum__gte=self.summit.full_cost, then=2),
                    default=0, output_field=IntegerField())
            )
        if select_related:
            qs = qs.select_related(*select_related)
        return qs.for_user(self.request.user)


class SummitBishopHighMasterListView(SummitProfileListMixin):
    serializer_class = MasterSerializer
    permission_classes = (IsAuthenticated,)
    queryset = CustomUser.objects.all()
    pagination_class = None

    def get_queryset(self):
        subqs = self.summit.ankets.all()
        return self.queryset.filter(pk__in=Subquery(subqs.values('user_id')), hierarchy__level__gte=4).annotate(
            full_name=Concat('last_name', V(' '), 'first_name', V(' '), 'middle_name'))


class SummitProfileListExportView(SummitProfileListView, ExportViewSetMixin):
    resource_class = SummitAnketResource
    queryset = SummitAnket.objects.all()

    def post(self, request, *args, **kwargs):
        return self._export(request, *args, **kwargs)

    def get_queryset(self):
        return super().get_queryset().exclude(status__active=False)
        # return super().get_queryset().annotate_full_name().exclude(status__active=False)


class ToChar(Func):
    function = 'to_char'
    template = "%(function)s(%(expressions)s, '%(time_format)s')"


class SummitStatisticsView(SummitProfileListView):
    serializer_class = SummitAnketStatisticsSerializer
    pagination_class = SummitStatisticsPagination

    ordering_fields = (
        'last_name', 'first_name', 'middle_name',
        'responsible', 'author__last_name',
        'department',
        'code',
        'user__phone_number',
        'attended',
    )

    filter_backends = (
        rest_framework.DjangoFilterBackend,
        OrderingFilterWithPk,
        FieldSearchFilter,
        FilterProfileAuthorTree,
        HasPhoto,
        FilterBySummitAttendByDate,
        FilterByTime,
    )

    filter_date = None

    def get(self, request, *args, **kwargs):
        """
        Getting list of summit profiles for table with statistics by attended


        By default ordering by ``last_name``, ``first_name``, ``middle_name``.
        Pagination by 30 profiles per page.
        """
        filter_date = request.GET.get('date')
        if not filter_date:
            self.filter_date = timezone.now()
        else:
            try:
                self.filter_date = pytz.utc.localize(datetime.strptime(filter_date, '%Y-%m-%d'))
            except ValueError:
                raise exceptions.ValidationError({'detail': _('Invalid date.')})
        return super().get(request, *args, **kwargs)

    def annotate_queryset(self, qs):
        subqs = SummitAttend.objects.filter(date=self.filter_date, anket=OuterRef('pk')).annotate(
            first_time=Coalesce(
                ToChar(F('created_at'), function='to_char', time_format='YYYY-MM-DD HH24:MI:SSZ',
                       output_field=CharField()),
                V('true'),
                output_field=CharField()))
        qs = qs.select_related('user', 'status').annotate(
            attended=Subquery(subqs.values('first_time')[:1], output_field=CharField())).annotate_full_name().order_by(
            'user__last_name', 'user__first_name', 'user__middle_name', 'pk')
        return qs

    def get_queryset(self):
        qs = self.annotate_queryset(self.summit.ankets)
        return qs.for_user(self.request.user)


class SummitStatisticsExportView(SummitStatisticsView, ExportViewSetMixin):
    resource_class = SummitStatisticsResource
    queryset = SummitAnket.objects.all()

    def post(self, request, *args, **kwargs):
        return self._export(request, *args, **kwargs)


class SummitProfileViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.RetrieveModelMixin,
                           mixins.DestroyModelMixin, GenericViewSet,
                           CreatePaymentMixin, ListPaymentMixin):
    queryset = SummitAnket.objects.base_queryset().annotate_total_sum().annotate_full_name()
    serializer_class = SummitAnketSerializer
    serializer_update_class = SummitProfileUpdateSerializer
    serializer_create_class = SummitProfileCreateSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        if self.action != 'retrieve':
            return self.queryset
        emails = AnketEmail.objects.filter(anket=OuterRef('pk'))
        other_summits = SummitAnket.objects.filter(
            user_id=OuterRef('user_id'),
            summit__type_id=get_object_or_404(SummitAnket, pk=self.kwargs.get('pk')).summit.type_id,
            summit__status=Summit.CLOSE
        )
        qs = self.queryset.annotate(
            has_email=Exists(emails), has_achievement=Exists(other_summits)).select_related('status') \
            .order_by(
            'user__last_name', 'user__first_name', 'user__middle_name', 'pk')
        return qs.for_user(self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return self.serializer_create_class
        if self.action in ('update', 'partial_update'):
            return self.serializer_update_class
        return self.serializer_class

    def perform_create(self, serializer):
        profile = serializer.save()
        profile.creator = self.request.user if self.request.user.is_authenticated else None
        profile.code = '0{}'.format(4 * 1000 * 1000 + profile.id)
        profile.save()

        new_dict = model_to_dict(profile, fields=('summit',))
        obj_add.send(
            sender=self.__class__,
            obj=profile.user,
            obj_dict=new_dict,
            editor=get_real_user(self.request),
            reason={
                'text': ugettext('Added to the summit'),
            }
        )

    def perform_destroy(self, profile):
        if profile.payments.exists():
            payments = PaymentShowWithUrlSerializer(
                profile.payments.all(), many=True, context={'request': self.request}).data
            raise exceptions.ValidationError({
                'detail': _('Summit profile has payments. Please, remove them before deleting profile.'),
                'payments': payments,
            })
        deletion_dict = model_to_dict(profile, fields=('summit',))
        obj_delete.send(
            sender=self.__class__,
            obj=profile.user,
            obj_dict=deletion_dict,
            editor=get_real_user(self.request),
            reason={
                'text': ugettext('Deleted from the summit'),
            }
        )
        profile.delete()

    @action(detail=True, methods=['get'], )
    def predelete(self, request, pk=None):
        profile = self.get_object()
        lessons = profile.all_lessons.all()
        consultant_on = Summit.objects.filter(id__in=profile.consultees.values_list('summit_id', flat=True))
        consultees = SummitAnket.objects.filter(id__in=profile.consultees.values_list('user_id', flat=True))
        consultants = SummitAnket.objects.filter(id__in=profile.consultants.values_list('consultant_id', flat=True))
        notes = profile.notes.all()

        return Response({
            'notes': SummitAnketNoteSerializer(notes, many=True).data,
            'lessons': SummitLessonShortSerializer(lessons, many=True).data,
            'summits': SummitShortSerializer(consultant_on, many=True).data,
            'users': SummitAnketShortSerializer(consultees, many=True).data,
            'consultants': SummitAnketShortSerializer(consultants, many=True).data,
        })

    @action(detail=True, methods=['get'])
    def notes(self, request, pk=None):
        serializer = SummitAnketNoteSerializer
        anket = self.get_object()
        queryset = anket.notes

        serializer = serializer(queryset, many=True)

        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def create_note(self, request, pk=None):
        text = request.data['text']
        data = {
            'text': text,
            'summit_anket': pk
        }
        serializer = SummitAnketNoteSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=request.user.customuser)
        headers = get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['GET'], permission_classes=(HasAPIAccess,), pagination_class=SummitTicketPagination)
    def codes(self, request):
        serializer = SummitAnketCodeSerializer
        summit_id = request.query_params.get('summit_id')
        ankets = SummitAnket.objects.filter(summit=summit_id)

        page = self.paginate_queryset(ankets)
        ankets = serializer(page, many=True)

        return self.get_paginated_response(ankets.data)

    @action(detail=True, methods=['post'])
    def set_ticket_status(self, request, pk=None):
        profile = self.get_object()
        new_status = request.data.get('new_status', settings.NEW_TICKET_STATUS.get(profile.ticket_status, None))

        if new_status not in map(lambda s: s[0], SummitAnket.TICKET_STATUSES):
            raise exceptions.ValidationError({
                'new_status': _('Incorrect status code.'),
                'correct_statuses': ['none', 'download', 'print', 'given']
            })

        profile.ticket_status = new_status
        profile.save()

        return Response({'new_status': new_status, 'text': profile.get_ticket_status_display()})


class SummitLessonViewSet(viewsets.ModelViewSet):
    queryset = SummitLesson.objects.all()
    serializer_class = SummitLessonSerializer

    @action(detail=True, methods=['post'])
    def add_viewer(self, request, pk=None):
        anket_id = request.data['anket_id']
        lesson = self.get_object()
        anket = get_object_or_404(SummitAnket, pk=anket_id)

        current_user_anket = SummitAnket.objects.filter(
            user=request.user, summit=anket.summit, role__gte=SummitAnket.CONSULTANT)
        is_consultant = SummitUserConsultant.objects.filter(
            consultant=current_user_anket, user_id=anket_id, summit=anket.summit).exists()
        if not is_consultant:
            return Response({'detail': 'Только консультант может отмечать уроки.',
                             'lesson_id': pk,
                             'checked': False},
                            status=status.HTTP_400_BAD_REQUEST)

        lesson.viewers.add(anket)

        return Response({'lesson': lesson.name, 'lesson_id': pk, 'anket_id': anket_id, 'checked': True})

    @action(detail=True, methods=['post'])
    def del_viewer(self, request, pk=None):
        anket_id = request.data['anket_id']
        lesson = self.get_object()
        anket = get_object_or_404(SummitAnket, pk=anket_id)

        current_user_anket = SummitAnket.objects.filter(
            user=request.user, summit=anket.summit, role__gte=SummitAnket.CONSULTANT)
        is_consultant = SummitUserConsultant.objects.filter(
            consultant=current_user_anket, user_id=anket_id, summit=anket.summit).exists()
        if not is_consultant:
            return Response({'detail': 'Только консультант может отмечать уроки.',
                             'lesson_id': pk,
                             'checked': True},
                            status=status.HTTP_400_BAD_REQUEST)

        lesson.viewers.remove(anket)

        return Response({'lesson': lesson.name, 'lesson_id': pk, 'anket_id': anket_id, 'checked': False})


class SummitUnregisterUserViewSet(ModelWithoutDeleteViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = SummitUnregisterUserSerializer
    filter_backends = (filters.SearchFilter,
                       rest_framework.DjangoFilterBackend,)
    permission_classes = (IsAuthenticated,)
    filter_class = SummitUnregisterFilter
    search_fields = ('first_name', 'last_name', 'middle_name',)
    pagination_class = SummitSearchPagination


class SummitTicketMakePrintedView(GenericAPIView):
    serializer_class = SummitTicketSerializer

    def post(self, request, *args, **kwargs):
        ticket_id = kwargs.get('ticket', None)
        ticket = get_object_or_404(SummitTicket, pk=ticket_id)
        try:
            with transaction.atomic():
                ticket.is_printed = True
                ticket.save()
                ticket.users.exclude(ticket_status=SummitAnket.GIVEN).update(ticket_status=SummitAnket.PRINTED)
        except IntegrityError as err:
            data = {'detail': _('При сохранении возникла ошибка. Попробуйте еще раз.')}
            logger.error(err)
            return Response(data, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response({'detail': _('Билеты отмечены напечатаными.')})


# UNUSED


class SummitViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Summit.objects.prefetch_related('lessons').order_by('-start_date', 'pk')
    serializer_class = SummitSerializer
    filter_backends = (rest_framework.DjangoFilterBackend,)
    filter_fields = ('type',)
    permission_classes = (IsAuthenticated,)

    @action(detail=True, methods=['get'])
    def lessons(self, request, pk=None):
        serializer = SummitLessonSerializer
        summit = self.get_object()
        queryset = summit.lessons

        serializer = serializer(queryset, many=True)

        return Response(serializer.data)

    @action(detail=True, methods=['post'], )
    def add_lesson(self, request, pk=None):
        name = request.data['name']
        data = dict()
        data['name'] = name
        data['summit'] = pk
        serializer = SummitLessonSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['get'])
    def consultants(self, request, pk=None):
        serializer = SummitAnketForSelectSerializer
        summit = self.get_object()
        queryset = summit.consultants.order_by('-id')

        serializer = serializer(queryset, many=True)

        return Response(serializer.data)

    @action(detail=True, methods=['post'], )
    def add_consultant(self, request, pk=None):
        summit = self.get_object()

        if not request.user.is_summit_supervisor_or_high(summit):
            return Response({'result': 'У вас нет прав для добавления консультантов.'},
                            status=status.HTTP_403_FORBIDDEN)

        anket_id = request.data['anket_id']
        anket = get_object_or_404(SummitAnket, pk=anket_id)
        if anket.summit != summit:
            return Response({'result': 'Выбранная анкета не соответствует данному саммиту.'},
                            status=status.HTTP_400_BAD_REQUEST)
        anket.role = SummitAnket.CONSULTANT
        anket.save()
        data = {'summit_id': int(pk), 'consultant_id': anket_id, 'action': 'added'}

        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], )
    def del_consultant(self, request, pk=None):
        summit = self.get_object()

        if not request.user.is_summit_supervisor_or_high(summit):
            return Response({'result': 'У вас нет прав для удаления консультантов.'},
                            status=status.HTTP_403_FORBIDDEN)

        anket_id = request.data['anket_id']
        anket = get_object_or_404(SummitAnket, pk=anket_id)
        if anket.summit != summit:
            return Response({'result': 'Выбранная анкета не соответствует данному саммиту.'},
                            status=status.HTTP_400_BAD_REQUEST)
        anket.role = SummitAnket.VISITOR
        anket.save()
        data = {'summit_id': int(pk), 'consultant_id': anket_id, 'action': 'removed'}

        return Response(data, status=status.HTTP_204_NO_CONTENT)


class SummitTicketViewSet(viewsets.GenericViewSet):
    queryset = SummitTicket.objects.all()
    serializer_class = SummitTicketSerializer
    permission_classes = (IsAuthenticated,)

    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        code = request.query_params.get('code')
        ticket = self.get_object()
        users = ticket.users.order_by('code').select_related('user').annotate(
            is_active=Case(
                When(code=code, then=True),
                default=False,
                output_field=BooleanField(),
            ),
        )
        summit_profiles = SummitAnketForTicketSerializer(users, many=True)

        return Response(summit_profiles.data)


@api_view(['GET'])
def generate_code(request, filename=''):
    code = request.query_params.get('code', '00000000')

    profile = get_object_or_404(SummitAnket, code=code)
    pdf = SummitTicketPDF([profile.pk]).generate_pdf()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment;'

    response.write(pdf)

    return response


@api_view(['GET'])
def summit_report_by_participant(request, summit_id, master_id):
    can_download = can_download_summit_participant_report(request.user, summit_id)
    if not can_download:
        raise exceptions.PermissionDenied(_('You do not have permission to download report. '))
    master = get_object_or_404(CustomUser, pk=master_id)
    report_date = request.query_params.get('date', '')
    short = request.query_params.get('short', None)
    attended = request.query_params.get('attended', None)

    pdf = FullSummitParticipantReport(summit_id, master, report_date, short, attended).generate_pdf()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment;'

    response.write(pdf)

    return response


@api_view(['GET'])
def summit_report_by_bishops(request, summit_id):
    can_see_report = can_see_report_by_bishop_or_high(request.user, summit_id)
    if not can_see_report:
        raise exceptions.PermissionDenied(_('You do not have permission to see report by bishops. '))
    department = request.query_params.get('department', None)
    fio = request.query_params.get('search_fio', '')
    hierarchy = request.query_params.get('hierarchy', None)
    report_date = request.query_params.get('date', timezone.now().strftime('%Y-%m-%d'))
    try:
        report_date = pytz.utc.localize(datetime.strptime(report_date, '%Y-%m-%d'))
    except ValueError:
        report_date = timezone.now()

    bishops = get_report_by_bishop_or_high(summit_id, report_date, department, fio, hierarchy)

    return Response(bishops)


@api_view(['GET'])
def generate_summit_tickets(request, summit_id):
    max_limit = 20
    limit = min(int(request.query_params.get('limit', max_limit)), max_limit)

    profiles = list(SummitAnket.objects.order_by('id').filter(
        summit_id=summit_id, tickets__isnull=True)[:limit].values_list('id', 'code'))
    if len(profiles) == 0:
        return Response(data={'detail': _('All tickets is already generated.')}, status=status.HTTP_400_BAD_REQUEST)

    profile_ids, profile_codes = list(), list()
    for p in profiles:
        profile_ids.append(p[0])
        profile_codes.append(p[1])
    ticket = SummitTicket.objects.create(
        summit_id=summit_id,
        owner=request.user,
        title='{}-{}'.format(min(profile_codes), max(profile_codes))
    )
    logger.info('New ticket: {}'.format(ticket.id))
    ticket.users.set(profile_ids)

    result = generate_tickets.apply_async(args=[summit_id, profile_ids, profile_codes, ticket.id])
    logger.info('generate_ticket: {}'.format(result))

    downloaded_profiles = SummitAnket.objects.filter(id__in=profile_ids).update(ticket_status=SummitAnket.DOWNLOADED)
    logger.info('Update profiles ticket_status: {}'.format(downloaded_profiles))

    return Response(data={'ticket_id': ticket.id})


@api_view(['GET'])
def send_code(request, profile_id):
    profile = get_object_or_404(SummitAnket, pk=profile_id)
    send_method = request.query_params.get('method')
    if not send_method:
        return exceptions.ValidationError({'message': 'Parameter {method} must be passed'})

    if send_method == 'email':
        if not profile.summit.zmail_template:
            return Response(data={'detail': 'Template for summit does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        if not profile.user.email:
            return Response(data={'detail': 'Empty email.'}, status=status.HTTP_400_BAD_REQUEST)
        task = send_email_with_code.apply_async(args=[profile_id, request.user.id])
        try:
            r = RedisBackend()
            r.sadd('summit:email:wait:{}:{}'.format(profile.summit_id, profile_id), task.id)
            r.expire('summit:email:wait:{}:{}'.format(profile.summit_id, profile), 30 * 24 * 60 * 60)
        except Exception as err:
            print(err)

    return Response(data={'profile_id': profile_id})


def get_status_ids(summit_id):
    r = RedisBackend()
    ids = set()
    for profile_id in r.scan_iter('summit:email:wait:{}:*'.format(summit_id)):
        ids.add(int(profile_id.decode('utf8').rsplit(':', 1)[-1]))
    return ids


def get_fail_ids(summit_id):
    r = RedisBackend()
    ids = set()
    for profile_id in r.scan_iter('summit:email:sending:{}:*'.format(summit_id)):
        tasks = r.smembers(profile_id)
        fail = True
        for task_id in tasks:
            result = AsyncResult(task_id)
            if result.successful() or not result.ready():
                fail = False
                break
        if fail:
            ids.add(int(profile_id.decode('utf8').rsplit(':', 1)[-1]))
    return ids


@api_view(['GET'])
def send_unsent_codes(request, summit_id):
    delay = 5
    limit = -1
    summit = get_object_or_404(Summit, pk=summit_id)
    current_user = request.user
    if not current_user.is_summit_supervisor_or_high(summit):
        raise exceptions.PermissionDenied()

    sent_count = 0
    unsent_count = 0
    tasks = dict()
    if not summit.zmail_template:
        return Response(data={'detail': 'Template for summit does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

    exist_ids = get_status_ids(summit_id)
    fail_ids = get_fail_ids(summit_id)
    countdown = 0
    emails = AnketEmail.objects.filter(anket=OuterRef('pk'), is_success=True)
    profiles = summit.ankets.annotate(has_email=Exists(emails)).filter(has_email=False).exclude(
        Q(user__email='') | Q(pk__in=(exist_ids - fail_ids))).select_related('user')
    if limit > 0:
        profiles = profiles[:limit]
    for profile in profiles:
        if not profile.user.email:
            unsent_count += 1
            continue
        task = send_email_with_code.apply_async(args=[profile.id, current_user.id, countdown])
        countdown += delay
        tasks[profile.id] = task.id
        sent_count += 1

    try:
        r = RedisBackend()
        for profile, task_id in tasks.items():
            r.sadd('summit:email:wait:{}:{}'.format(summit_id, profile), task_id)
            r.expire('summit:email:wait:{}:{}'.format(summit_id, profile), 30 * 24 * 60 * 60)
    except Exception as err:
        print(err)
    users_without_emails = summit.ankets.filter(user__email='').annotate(full_name=Concat(
        'user__last_name', V(' '),
        'user__first_name', V(' '),
        'user__middle_name'))
    return Response(data={
        'sent_count': sent_count,
        'users_without_emails_count': users_without_emails.count(),
        'users_without_emails': list(users_without_emails.values('user_id', 'full_name', 'user__email')),
    }, status=status.HTTP_202_ACCEPTED)


def get_status_schedule_ids(summit_id):
    r = RedisBackend()
    ids = set()
    for profile_id in r.scan_iter('summit:schedule:wait:{}:*'.format(summit_id)):
        ids.add(int(profile_id.decode('utf8').rsplit(':', 1)[-1]))
    return ids


def get_fail_schedule_ids(summit_id):
    r = RedisBackend()
    ids = set()
    for profile_id in r.scan_iter('summit:schedule:sending:{}:*'.format(summit_id)):
        tasks = r.smembers(profile_id)
        fail = True
        for task_id in tasks:
            result = AsyncResult(task_id)
            if result.successful() or not result.ready():
                fail = False
                break
        if fail:
            ids.add(int(profile_id.decode('utf8').rsplit(':', 1)[-1]))
    return ids


@api_view(['GET'])
def send_unsent_schedules(request, summit_id):
    delay = 15
    limit = -1
    summit = get_object_or_404(Summit, pk=summit_id)
    current_user = request.user
    if not current_user.is_summit_supervisor_or_high(summit):
        raise exceptions.PermissionDenied()

    sent_count = 0
    tasks = dict()

    exist_ids = get_status_schedule_ids(summit_id) | sent_pulse_emails.get(summit_id, set())
    fail_ids = get_fail_schedule_ids(summit_id) - sent_pulse_emails.get(summit_id, set())
    countdown = 0
    profiles = summit.ankets.exclude(
        Q(user__email='') | Q(pk__in=(exist_ids - fail_ids))).select_related('user')
    if limit > 0:
        profiles = profiles[:limit]
    for profile in profiles:
        task = send_email_with_schedule.apply_async(
            args=[profile.id, current_user.id, 'raspisanie-sammita-2017', countdown])
        countdown += delay
        tasks[profile.id] = task.id
        sent_count += 1

    try:
        r = RedisBackend()
        for profile, task_id in tasks.items():
            r.sadd('summit:schedule:wait:{}:{}'.format(summit_id, profile), task_id)
            r.expire('summit:schedule:wait:{}:{}'.format(summit_id, profile), 30 * 24 * 60 * 60)
    except Exception as err:
        print(err)
    users_without_emails = summit.ankets.filter(user__email='').annotate(full_name=Concat(
        'user__last_name', V(' '),
        'user__first_name', V(' '),
        'user__middle_name'))
    return Response(data={
        'sent_count': sent_count,
        'users_without_emails_count': users_without_emails.count(),
        'users_without_emails': list(users_without_emails.values('user_id', 'full_name', 'user__email')),
    }, status=status.HTTP_202_ACCEPTED)


class HistorySummitStatsMixin(GenericAPIView):
    queryset = SummitAnket.objects.all()

    pagination_class = None
    permission_classes = (IsAuthenticated,)

    filter_backends = (
        FilterByDepartment,
        FilterByMasterTree,
    )

    summit = None
    _profiles = None
    _profiles_dates = None

    def dispatch(self, request, *args, **kwargs):
        self.summit = get_object_or_404(Summit, pk=kwargs.get('summit_id'))
        return super().dispatch(request, *args, **kwargs)

    @property
    def attends_query(self):
        # if self.request.query_params.get('master_tree') is not None:
        query = """
            SELECT date, time, created_at
            FROM summit_summitattend WHERE anket_id IN (
                WITH RECURSIVE t AS (
                  SELECT
                    a.id aid,
                    a.user_id
                  FROM summit_summitanket a
                  {department_join}
                  WHERE summit_id = {summit_id} {master_tree_filter}
                      {department_filter}
                  UNION
                  SELECT
                    a.id aid,
                    a.user_id
                  FROM summit_summitanket a
                    JOIN t ON a.author_id = t.user_id
                    {department_join}
                  WHERE summit_id = {summit_id}
                      {department_filter}
                )
                SELECT aid FROM t
            ) AND date BETWEEN '{start}' AND '{end}';
        """
        return query

    def check_permissions(self, request):
        super().check_permissions(request)
        # ``summit`` supervisor or high
        if not request.user.can_see_summit_history_stats(self.summit):
            self.permission_denied(
                request, message=_('You do not have permission to see statistics.')
            )

    def _get_master_tree_filter(self) -> str:
        master_tree = self.request.query_params.get('master_tree', '')
        master_tree_filter = f'and a.user_id = {master_tree}' if master_tree else ''
        return master_tree_filter

    def _get_department_filter(self) -> (str, str):
        department = self.request.query_params.get('department', '')
        department_filter = f'and d.id = {department}' if department else ''
        department_join = """
            JOIN summit_summitanket_departments ad ON a.id = ad.summitanket_id
            JOIN hierarchy_department d ON ad.department_id = d.id
        """ if department else ''
        return department_filter, department_join

    def _get_filter_attends(self) -> List[Attend]:
        master_tree_filter = self._get_master_tree_filter()
        department_filter, department_join = self._get_department_filter()

        query = self.attends_query.format(
            summit_id=self.summit.id,
            department_join=department_join,
            department_filter=department_filter,
            master_tree_filter=master_tree_filter,
            start=self.summit.start_date.strftime('%Y-%m-%d'),
            end=self.summit.end_date.strftime('%Y-%m-%d')
        )

        attends: List[Attend] = list()
        with connection.cursor() as connect:
            connect.execute(query)
            for attend in connect.fetchall():
                attends.append(Attend(*attend))
        return attends

    def _get_all_attends(self) -> List[Attend]:
        query = f"""
            SELECT at.date, at.time, at.created_at
            FROM summit_summitattend at
              JOIN summit_summitanket a ON at.anket_id = a.id
            WHERE a.summit_id = {self.summit.id} AND at.date BETWEEN
                '{self.summit.start_date.strftime('%Y-%m-%d')}' AND
                '{self.summit.end_date.strftime('%Y-%m-%d')}'
            ;
        """
        attends: List[Attend] = list()
        with connection.cursor() as connect:
            connect.execute(query)
            for attend in connect.fetchall():
                attends.append(Attend(*attend))
        return attends

    def _get_profiles_dates(self):
        master_tree_filter = self._get_master_tree_filter()
        department_filter, department_join = self._get_department_filter()

        query = f"""
            WITH RECURSIVE t as (
                SELECT
                  a.date,
                  a.user_id
                FROM summit_summitanket a
                  {department_join}
                WHERE summit_id = {self.summit.id} {master_tree_filter}
                  {department_filter}
              UNION
                SELECT
                  a.date,
                  a.user_id
                FROM summit_summitanket a
                  JOIN t on a.author_id = t.user_id
                    {department_join}
                WHERE summit_id = {self.summit.id}
                  {department_filter}
            )
            SELECT date from t;
        """
        dates = list()
        with connection.cursor() as connect:
            connect.execute(query)
            for d, in connect.fetchall():
                dates.append(d)
        return dates

    @property
    def profiles_dates(self):
        if self._profiles_dates is None:
            self._profiles_dates = self._get_profiles_dates()
        return self._profiles_dates

    def _count_profiles_by_date(self, date):
        return len(list(filter(lambda d: d <= date, self.profiles_dates)))

    def get_attends(self):
        fa = self._get_filter_attends()
        a = self._get_all_attends()
        return fa, a


class HistorySummitAttendStatsView(HistorySummitStatsMixin):
    """
    Getting statistics for attends
    """

    def get(self, request, *args, **kwargs):
        filter_attends, attends = self.get_attends()

        all_attends_by_date = collections.Counter([a.date for a in attends])
        attends_by_date = collections.Counter([a.date for a in filter_attends])
        for d in all_attends_by_date.keys():
            attends_by_date[d] = (attends_by_date.get(d, 0), self._count_profiles_by_date(d))
        return Response([
            (datetime(d.year, d.month, d.day, tzinfo=pytz.utc).timestamp(), attends_by_date[d]) for d in
            sorted(attends_by_date.keys())
        ])


class HistorySummitLatecomerStatsView(HistorySummitStatsMixin):
    """
    Getting statistics on latecomers
    """
    start_time = time(11, 30)

    def get(self, request, *args, **kwargs):
        filter_attends, attends = self.get_attends()

        all_attends_by_date = collections.Counter([a.date for a in attends])
        # filter_attends = [(a.date, a.time, a.created_at) for a in filter_attends]
        attends_by_date = defaultdict(list)
        for a in filter_attends:
            attends_by_date[a.date].append(a.time or (a.created_at.time() if a.created_at else None))
        for d in all_attends_by_date.keys():
            late_count = len(list(filter(lambda t: t and t > self.start_time, attends_by_date[d])))
            attend_count = len(attends_by_date[d])
            attends_by_date[d] = [late_count, attend_count - late_count]
        return Response([
            (datetime(d.year, d.month, d.day, tzinfo=pytz.utc).timestamp(), attends_by_date[d]) for d in
            sorted(attends_by_date.keys())
        ])


class HistorySummitStatByMasterDisciplesView(GenericAPIView):
    """
    Getting statistics by disciples of master

    Returns counts of the disciples of master.disciples.
    """
    queryset = SummitAnket.objects.order_by('last_name', 'first_name', 'middle_name', 'pk')

    permission_classes = (IsAuthenticated,)
    pagination_class = None

    summit = None
    author = None

    def dispatch(self, request, *args, **kwargs):
        self.summit = get_object_or_404(Summit, pk=kwargs.get('summit_id'))
        self.author = get_object_or_404(CustomUser, pk=kwargs.get('master_id'))
        return super().dispatch(request, *args, **kwargs)

    def get_profiles(self):
        query = f"""
            WITH RECURSIVE t as (
              SELECT
                a.user_id,
                concat(u.last_name, ' ', u.first_name, ' ', cu.middle_name) full_name,
                ARRAY[]::INTEGER[] as tree
              FROM summit_summitanket a
                JOIN account_customuser cu ON a.user_id = cu.user_ptr_id
                JOIN auth_user u ON cu.user_ptr_id = u.id
              WHERE summit_id = {self.summit.id} and a.user_id = {self.author.id}
              UNION
              SELECT
                a.user_id,
                concat(u.last_name, ' ', u.first_name, ' ', cu.middle_name) full_name,
                array_cat(t.tree, ARRAY[a.user_id]) as tree
              FROM summit_summitanket a
                JOIN t on a.author_id = t.user_id
                JOIN account_customuser cu ON a.user_id = cu.user_ptr_id
                JOIN auth_user u ON cu.user_ptr_id = u.id
              WHERE summit_id = {self.summit.id}
            )
            SELECT user_id, full_name, tree from t ORDER BY tree OFFSET 1;
        """
        profiles = defaultdict(dict)
        with connection.cursor() as connect:
            connect.execute(query)
            for user_id, name, tree in connect.fetchall():
                root = tree[0]
                if user_id == root:
                    profiles[user_id] = {'full_name': name, 'count': 0}
                profiles[root]['count'] += 1
        author_count = 0
        for user_id, profile in profiles.copy().items():
            if profile['count'] < 2:
                author_count += 1
                del profiles[user_id]
        if author_count:
            profiles[self.author.pk] = {'full_name': f'({self.author.fullname})', 'count': author_count}
        return profiles

    def get(self, request, *args, **kwargs):
        profiles = self.get_profiles()

        data = [[m['full_name'], [m['count']]] for m in profiles.values()]
        return Response(data)

    def check_permissions(self, request):
        super().check_permissions(request)
        # ``summit`` supervisor or high
        if not request.user.can_see_summit_history_stats(self.summit):
            self.permission_denied(
                request, message=_('You do not have permission to see statistics.')
            )
