# -*- coding: utf-8
from __future__ import unicode_literals

import logging
from datetime import datetime

from django.conf import settings
from django.db import transaction, IntegrityError
from django.db.models import (
    Case, When, BooleanField, F, Subquery, OuterRef, CharField,
    Func)
from django.db.models import Value as V
from django.db.models.functions import Concat, Coalesce
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _, ugettext
from rest_framework import exceptions, viewsets, filters, status, mixins
from rest_framework.decorators import list_route, detail_route, api_view
from rest_framework.generics import get_object_or_404, GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.viewsets import GenericViewSet

from account.models import CustomUser
from account.signals import obj_add, obj_delete
from analytics.utils import model_to_dict
from common.filters import FieldSearchFilter
from common.views_mixins import ModelWithoutDeleteViewSet, ExportViewSetMixin
from payment.serializers import PaymentShowWithUrlSerializer
from payment.views_mixins import CreatePaymentMixin, ListPaymentMixin
from summit.filters import (FilterByClub, SummitUnregisterFilter, ProfileFilter,
                            FilterProfileMasterTreeWithSelf, HasPhoto, FilterBySummitAttend,
                            FilterBySummitAttendByDate, FilterByElecTicketStatus, FilterByTime)
from summit.pagination import SummitPagination, SummitTicketPagination, SummitStatisticsPagination
from summit.permissions import HasAPIAccess, CanSeeSummitProfiles, can_download_summit_participant_report, \
    can_see_report_by_bishop_or_high
from summit.resources import SummitAnketResource, SummitStatisticsResource
from summit.utils import generate_ticket, SummitParticipantReport, get_report_by_bishop_or_high
from .models import (Summit, SummitAnket, SummitLesson, SummitUserConsultant,
                     SummitTicket, SummitAttend)
from .serializers import (
    SummitSerializer, SummitUnregisterUserSerializer, SummitAnketSerializer,
    SummitAnketNoteSerializer, SummitLessonSerializer,
    SummitAnketForSelectSerializer,
    SummitShortSerializer, SummitAnketShortSerializer, SummitLessonShortSerializer, SummitTicketSerializer,
    SummitAnketForTicketSerializer, SummitAnketCodeSerializer,
    SummitAnketStatisticsSerializer,
    MasterSerializer, SummitProfileUpdateSerializer, SummitProfileCreateSerializer)
from .tasks import generate_tickets

logger = logging.getLogger(__name__)


def get_success_headers(data):
    try:
        return {'Location': data[api_settings.URL_FIELD_NAME]}
    except (TypeError, KeyError):
        return {}


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


class SummitProfileListView(SummitProfileListMixin):
    serializer_class = SummitAnketSerializer
    pagination_class = SummitPagination
    permission_classes = (IsAuthenticated,)

    filter_class = ProfileFilter
    ordering_fields = (
        'first_name', 'last_name', 'responsible',
        'spiritual_level', 'divisions_title', 'department', 'user__facebook', 'country', 'city',
        'code', 'value', 'description',
        'middle_name', 'user__born_date', 'country',
        'user__region', 'city', 'user__district',
        'user__address', 'user__phone_number',
        'user__email', 'hierarchy__level', 'ticket_status', 'status__reg_code_requested'
    )
    filter_backends = (
        filters.DjangoFilterBackend,
        filters.OrderingFilter,
        FieldSearchFilter,
        FilterProfileMasterTreeWithSelf,
        FilterByClub,
        HasPhoto,
        FilterBySummitAttend,
        FilterByElecTicketStatus,
    )

    field_search_fields = {
        'search_fio': ('last_name', 'first_name', 'middle_name', 'search_name'),
        'search_email': ('user__email',),
        'search_phone_number': ('user__phone_number',),
        'search_country': ('country',),
        'search_city': ('city',),
    }

    def get_queryset(self):
        qs = self.summit.ankets.select_related('status') \
            .base_queryset().annotate_total_sum().annotate_full_name().order_by(
            'user__last_name', 'user__first_name', 'user__middle_name')
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


class ToChar(Func):
    function = 'to_char'
    template = "%(function)s(%(expressions)s, '%(time_format)s')"


class SummitStatisticsView(SummitProfileListView):
    serializer_class = SummitAnketStatisticsSerializer
    pagination_class = SummitStatisticsPagination

    filter_date = None

    ordering_fields = (
        'last_name', 'first_name', 'middle_name',
        'responsible',
        'department',
        'code',
        'user__phone_number',
        'attended',
    )

    filter_backends = (
        filters.DjangoFilterBackend,
        filters.OrderingFilter,
        FieldSearchFilter,
        FilterProfileMasterTreeWithSelf,
        HasPhoto,
        FilterBySummitAttendByDate,
        FilterByTime,
    )

    def get(self, request, *args, **kwargs):
        filter_date = request.GET.get('date')
        if not filter_date:
            self.filter_date = datetime.now()
        else:
            try:
                self.filter_date = datetime.strptime(filter_date, '%Y-%m-%d')
            except ValueError:
                raise exceptions.ValidationError({'detail': _('Invalid date.')})
        return super(SummitStatisticsView, self).get(request, *args, **kwargs)

    def annotate_queryset(self, qs):
        subqs = SummitAttend.objects.filter(date=self.filter_date, anket=OuterRef('pk')).annotate(
            first_time=Coalesce(
                ToChar(F('time'), function='to_char', time_format='HH24:MI:SS', output_field=CharField()),
                ToChar(F('created_at'), function='to_char', time_format='HH24:MI:SS el', output_field=CharField()),
                V('true'),
                output_field=CharField()))
        qs = qs.select_related('user', 'status').annotate(
            attended=Subquery(subqs.values('first_time')[:1], output_field=CharField())).annotate_full_name().order_by(
            'user__last_name', 'user__first_name', 'user__middle_name')
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

    def get_serializer_class(self):
        if self.action == 'create':
            return self.serializer_create_class
        if self.action in ('update', 'partial_update'):
            return self.serializer_update_class
        return self.serializer_class

    def perform_create(self, serializer):
        profile = serializer.save()
        profile.creator = self.request.user if self.request.user.is_authenticated else None
        profile.code = '0{}'.format(4*1000*1000 + profile.id)
        profile.save()

        new_dict = model_to_dict(profile, fields=('summit',))
        obj_add.send(
            sender=self.__class__,
            obj=profile.user,
            obj_dict=new_dict,
            editor=getattr(self.request, 'real_user', self.request.user),
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
            editor=getattr(self.request, 'real_user', self.request.user),
            reason={
                'text': ugettext('Deleted from the summit'),
            }
        )
        profile.delete()

    @detail_route(methods=['get'], )
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

    @detail_route(methods=['get'])
    def notes(self, request, pk=None):
        serializer = SummitAnketNoteSerializer
        anket = self.get_object()
        queryset = anket.notes

        serializer = serializer(queryset, many=True)

        return Response(serializer.data)

    @detail_route(methods=['post'])
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

    @list_route(methods=['GET'], permission_classes=(HasAPIAccess,), pagination_class=SummitTicketPagination)
    def codes(self, request):
        serializer = SummitAnketCodeSerializer
        summit_id = request.query_params.get('summit_id')
        ankets = SummitAnket.objects.filter(summit=summit_id)

        page = self.paginate_queryset(ankets)
        ankets = serializer(page, many=True)

        return self.get_paginated_response(ankets.data)

    @detail_route(methods=['post'])
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

    @detail_route(methods=['post'])
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

    @detail_route(methods=['post'])
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
                       filters.DjangoFilterBackend,)
    permission_classes = (IsAuthenticated,)
    filter_class = SummitUnregisterFilter
    search_fields = ('first_name', 'last_name', 'middle_name',)


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
    queryset = Summit.objects.prefetch_related('lessons').order_by('-start_date')
    serializer_class = SummitSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('type',)
    permission_classes = (IsAuthenticated,)

    @detail_route(methods=['get'])
    def lessons(self, request, pk=None):
        serializer = SummitLessonSerializer
        summit = self.get_object()
        queryset = summit.lessons

        serializer = serializer(queryset, many=True)

        return Response(serializer.data)

    @detail_route(methods=['post'], )
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

    @detail_route(methods=['get'])
    def consultants(self, request, pk=None):
        serializer = SummitAnketForSelectSerializer
        summit = self.get_object()
        queryset = summit.consultants.order_by('-id')

        serializer = serializer(queryset, many=True)

        return Response(serializer.data)

    @detail_route(methods=['post'], )
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

    @detail_route(methods=['post'], )
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

    @detail_route(['get'])
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
def generate_code(request):
    code = request.query_params.get('code', '00000000')

    pdf = generate_ticket(code)

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

    pdf = SummitParticipantReport(summit_id, master, report_date, short, attended).generate_pdf()

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
    report_date = request.query_params.get('date', datetime.now().strftime('%Y-%m-%d'))
    try:
        report_date = datetime.strptime(report_date, '%Y-%m-%d')
    except ValueError:
        report_date = datetime.now()

    bishops = get_report_by_bishop_or_high(summit_id, report_date, department, fio, hierarchy)

    return Response(bishops)


@api_view(['GET'])
def generate_summit_tickets(request, summit_id):
    limit = 2000

    ankets = list(SummitAnket.objects.order_by('id').filter(
        summit_id=summit_id, tickets__isnull=True).exclude(user__image='')[:limit].values_list('id', 'code'))
    if len(ankets) == 0:
        return Response(data={'detail': _('All tickets is already generated.')}, status=status.HTTP_400_BAD_REQUEST)
    ticket = SummitTicket.objects.create(
        summit_id=summit_id, owner=request.user, title='{}-{}'.format(
            min(ankets, key=lambda a: int(a[1]))[1], max(ankets, key=lambda a: int(a[1]))[1]))
    logger.info('New ticket: {}'.format(ticket.id))
    ticket.users.set([a[0] for a in ankets])

    result = generate_tickets.apply_async(args=[summit_id, ankets, ticket.id])
    logger.info('generate_ticket: {}'.format(result))

    result = SummitAnket.objects.filter(id__in=[a[0] for a in ankets]).update(ticket_status=SummitAnket.DOWNLOADED)
    logger.info('Update profiles ticket_status: {}'.format(result))

    return Response(data={'ticket_id': ticket.id})
