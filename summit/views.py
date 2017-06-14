# -*- coding: utf-8
from __future__ import unicode_literals

import logging
from datetime import datetime, timedelta

from dbmail import send_db_mail
from django.db import transaction, IntegrityError
from django.conf import settings
from django.db.models import Case, When, BooleanField, F, ExpressionWrapper, IntegerField, Subquery, OuterRef, Exists
from django.db.models.functions import Concat
from django.db.models import Value as V
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions, viewsets, filters, status, mixins, serializers
from rest_framework.decorators import list_route, detail_route, api_view
from rest_framework.generics import get_object_or_404, GenericAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.viewsets import GenericViewSet

from account.models import CustomUser
from common.filters import FieldSearchFilter
from common.views_mixins import ModelWithoutDeleteViewSet, ExportViewSetMixin
from payment.serializers import PaymentShowWithUrlSerializer
from payment.views_mixins import CreatePaymentMixin, ListPaymentMixin
from summit.filters import FilterByClub, SummitUnregisterFilter, ProfileFilter, \
    FilterProfileMasterTreeWithSelf, HasPhoto, FilterBySummitAttend, FilterBySummitAttendByDate
from summit.pagination import SummitPagination, SummitTicketPagination, SummitStatisticsPagination
from summit.permissions import HasAPIAccess, CanSeeSummitProfiles, can_download_summit_participant_report, \
    can_see_report_by_bishop_or_high
from summit.resources import SummitAnketResource
from summit.utils import generate_ticket, SummitParticipantReport, get_report_by_bishop_or_high
from .models import (Summit, SummitAnket, SummitType, SummitLesson, SummitUserConsultant,
                     SummitTicket, SummitVisitorLocation, SummitEventTable, SummitAttend, AnketStatus)
from .serializers import (
    SummitSerializer, SummitTypeSerializer, SummitUnregisterUserSerializer, SummitAnketSerializer,
    SummitAnketNoteSerializer, SummitAnketWithNotesSerializer, SummitLessonSerializer,
    SummitAnketForSelectSerializer, SummitTypeForAppSerializer, SummitAnketForAppSerializer,
    SummitShortSerializer, SummitAnketShortSerializer, SummitLessonShortSerializer, SummitTicketSerializer,
    SummitAnketForTicketSerializer, SummitVisitorLocationSerializer, SummitEventTableSerializer,
    SummitProfileTreeForAppSerializer, SummitAnketCodeSerializer, AnketActiveStatusSerializer,
    SummitAnketStatisticsSerializer, SummitAcceptMobileCodeSerializer, SummitAttendSerializer
)
from .tasks import generate_tickets

logger = logging.getLogger(__name__)


def get_success_headers(data):
    try:
        return {'Location': data[api_settings.URL_FIELD_NAME]}
    except (TypeError, KeyError):
        return {}


class SummitProfileListView(mixins.ListModelMixin, GenericAPIView):
    serializer_class = SummitAnketSerializer
    pagination_class = SummitPagination
    permission_classes = (IsAuthenticated,)
    summit = None

    filter_class = ProfileFilter
    ordering_fields = (
        'first_name', 'last_name', 'responsible',
        'spiritual_level', 'divisions_title', 'department', 'user__facebook', 'country', 'city',
        'code', 'value', 'description',
        'middle_name', 'user__born_date', 'country',
        'user__region', 'city', 'user__district',
        'user__address', 'user__phone_number',
        'user__email', 'hierarchy__level', 'ticket_status',
    )
    filter_backends = (
        filters.DjangoFilterBackend,
        filters.OrderingFilter,
        FieldSearchFilter,
        FilterProfileMasterTreeWithSelf,
        FilterByClub,
        HasPhoto,
        FilterBySummitAttend,
    )

    field_search_fields = {
        'search_fio': ('last_name', 'first_name', 'middle_name', 'search_name'),
        'search_email': ('user__email',),
        'search_phone_number': ('user__phone_number',),
        'search_country': ('country',),
        'search_city': ('city',),
    }

    def dispatch(self, request, *args, **kwargs):
        self.summit = get_object_or_404(Summit, pk=kwargs.get('pk', None))
        return super(SummitProfileListView, self).dispatch(request, *args, **kwargs)

    def check_permissions(self, request):
        super(SummitProfileListView, self).check_permissions(request)
        # ``summit`` consultant or high
        if not CanSeeSummitProfiles().has_object_permission(request, self, self.summit):
            self.permission_denied(
                request, message=getattr(CanSeeSummitProfiles, 'message', None)
            )

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        qs = self.summit.ankets.base_queryset().annotate_total_sum().annotate_full_name().order_by(
            'user__last_name', 'user__first_name', 'user__middle_name')
        return qs.for_user(self.request.user)


class MasterSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField()

    class Meta:
        model = CustomUser
        fields = ('id', 'full_name')


class SummitBishopHighMasterListView(mixins.ListModelMixin, GenericAPIView):
    serializer_class = MasterSerializer
    permission_classes = (IsAuthenticated,)
    queryset = CustomUser.objects.all()
    summit = None
    pagination_class = None

    def dispatch(self, request, *args, **kwargs):
        self.summit = get_object_or_404(Summit, pk=kwargs.get('pk', None))
        return super(SummitBishopHighMasterListView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def check_permissions(self, request):
        super(SummitBishopHighMasterListView, self).check_permissions(request)
        if not CanSeeSummitProfiles().has_object_permission(request, self, self.summit):
            self.permission_denied(
                request, message=getattr(CanSeeSummitProfiles, 'message', None)
            )

    def get_queryset(self):
        subqs = self.summit.ankets.all()
        return self.queryset.filter(pk__in=Subquery(subqs.values('user_id')), hierarchy__level__gte=4).annotate(
            full_name=Concat('last_name', V(' '), 'first_name', V(' '), 'middle_name'))


class SummitProfileListExportView(SummitProfileListView, ExportViewSetMixin):
    resource_class = SummitAnketResource
    queryset = SummitAnket.objects.all()

    def post(self, request, *args, **kwargs):
        return self._export(request, *args, **kwargs)


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
    )

    def dispatch(self, request, *args, **kwargs):
        filter_date = request.GET.get('date')
        if not filter_date:
            self.filter_date = datetime.now()
        else:
            try:
                self.filter_date = datetime.strptime(filter_date, '%Y-%m-%d')
            except ValueError:
                raise exceptions.ValidationError(_('Invalid date.'))
        return super(SummitStatisticsView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        subqs = SummitAttend.objects.filter(date=self.filter_date, anket=OuterRef('pk'))
        qs = self.summit.ankets.select_related('user').annotate(attended=Exists(subqs)).annotate_full_name().order_by(
            'user__last_name', 'user__first_name', 'user__middle_name')
        return qs.for_user(self.request.user)


class SummitProfileViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                           mixins.DestroyModelMixin, GenericViewSet,
                           CreatePaymentMixin, ListPaymentMixin):
    queryset = SummitAnket.objects.base_queryset().annotate_total_sum().annotate_full_name()
    serializer_class = SummitAnketSerializer
    permission_classes = (IsAuthenticated,)

    def perform_destroy(self, anket):
        if anket.payments.exists():
            payments = PaymentShowWithUrlSerializer(
                anket.payments.all(), many=True, context={'request': self.request}).data
            raise exceptions.ValidationError({
                'detail': _('Summit profile has payments. Please, remove them before deleting profile.'),
                'payments': payments,
            })
        anket.delete()

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

    @list_route(methods=['post'], )
    def post_anket(self, request):
        keys = request.data.keys()
        if not ('user_id' in keys and 'summit_id' in keys):
            return Response({"message": "Некоректные данные", 'status': False})

        user = CustomUser.objects.filter(id=request.data['user_id']).first()
        if not user:
            return Response({"message": "Такого пользователя не существует", 'status': False})

        summit = Summit.objects.filter(id=request.data['summit_id']).first()
        if not summit:
            return Response({"message": "Такой саммит отсутствует", 'status': False})

        anket = SummitAnket.objects.filter(user=user, summit=summit)
        visited = request.data.get('visited', None)
        if anket.exists():
            anket = anket.get()
            if len(request.data['description']) > 0:
                anket.description = request.data['description']
            if visited in (True, False):
                anket.visited = visited
            anket.save()
        else:
            anket = SummitAnket.objects.create(
                user=user, summit=summit, visited=visited, description=request.data['description'])
            anket.code = '0{}'.format(4 * 1000 * 1000 + anket.id)
            anket.creator = request.user
            anket.save()
        data = {"message": "Данные успешно сохраненны",
                'status': True}
        if (data['status'] and request.data.get('send_email', False) and
                anket.summit.mail_template and anket.user.email and
                (int(request.user.id) == 4035 or True)):
            attach = generate_ticket(anket.code)
            pdf_name = '{} ({}).pdf'.format(anket.user.fullname, anket.code)
            send_db_mail(
                anket.summit.mail_template.slug,
                anket.user.email,
                anket,
                attachments=[(pdf_name, attach, 'application/pdf')],
                signals_kwargs={'anket': anket}
            )

        return Response(data)

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
        if page is not None:
            ankets = serializer(page, many=True)
            return self.get_paginated_response(ankets.data)
        ankets = serializer(ankets, many=True)

        return Response(ankets.data)

    @detail_route(methods=['post'])
    def set_ticket_status(self, request, pk=None):
        profile = self.get_object()
        new_status = request.data.get('new_status', settings.NEW_TICKET_STATUS[profile.ticket_status])

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
            return Response({'message': 'Только консультант может отмечать уроки.',
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
            return Response({'message': 'Только консультант может отмечать уроки.',
                             'lesson_id': pk,
                             'checked': True},
                            status=status.HTTP_400_BAD_REQUEST)

        lesson.viewers.remove(anket)

        return Response({'lesson': lesson.name, 'lesson_id': pk, 'anket_id': anket_id, 'checked': False})


class SummitUnregisterUserViewSet(viewsets.ModelViewSet):
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
                ticket.users.update(ticket_status=SummitAnket.PRINTED)
        except IntegrityError as err:
            data = {'detail': _('При сохранении возникла ошибка. Попробуйте еще раз.')}
            logger.error(err)
            return Response(data, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response({'detail': _('Билеты отмечены напечатаными.')})


# FOR APP


class SummitTypeForAppViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = SummitType.objects.prefetch_related('summits')
    serializer_class = SummitTypeForAppSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class SummitAnketForAppViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = SummitAnket.objects.select_related('user').order_by('id')
    serializer_class = SummitAnketForAppSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('summit',)
<<<<<<< HEAD
    permission_classes = (HasAPIAccess,)
=======
    # permission_classes = (HasAPIAccess,)
>>>>>>> f2477eda0401e29e58ab6300610bbc0b5e770edc
    pagination_class = None

    @list_route(methods=['GET'])
    def by_reg_code(self, request):
        reg_code = request.query_params.get('reg_code')
        try:
            reg_code = int('0x' + reg_code, 0)
            visitor_id = int(str(reg_code)[:-4])
        except ValueError:
            raise exceptions.ValidationError(_('Невозможно получить объект. '
                                               'Передан некорректный регистрационный код'))
        visitor = get_object_or_404(SummitAnket, pk=visitor_id)
        AnketStatus.objects.get_or_create(
            anket=visitor, defaults={'reg_code_requested': True,
                                     'reg_code_requested_date': datetime.now()})

        visitor = self.get_serializer(visitor)
        return Response(visitor.data)

    @list_route(methods=['GET'])
    def by_reg_date(self, request):
        from_date = request.query_params.get('from_date', datetime.now().date() - timedelta(days=1))
        to_date = request.query_params.get('to_date', datetime.now().date() - timedelta(days=1))

        if from_date > to_date:
            raise exceptions.ValidationError('Некорректно заданный временной интвервал. ')

        ankets = SummitAnket.objects.filter(
            status__reg_code_requested_date__date__range=[from_date, to_date])
        ankets = self.serializer_class(ankets, many=True)
        return Response(ankets.data)


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

    def dispatch(self, request, *args, **kwargs):
        return super(SummitProfileTreeForAppListView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.summit = get_object_or_404(Summit, pk=kwargs.get('summit_id', None))
        self.master_id = kwargs.get('master_id', None)
        return self.list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'profiles': serializer.data,
        })

    def annotate_queryset(self, qs):
        return qs.base_queryset().annotate_full_name().annotate(
            diff=ExpressionWrapper(F('user__rght') - F('user__lft'), output_field=IntegerField()),
        ).order_by('-hierarchy__level', 'last_name', 'first_name', 'middle_name')

    def get_queryset(self):
        is_consultant_or_high = self.request.user.is_summit_consultant_or_high(self.summit)
        if self.master_id is not None:
            if is_consultant_or_high:
                return self.annotate_queryset(self.summit.ankets.filter(user__master_id=self.master_id))
            return self.annotate_queryset(self.summit.ankets.filter(
                user__master_id=self.master_id, user_id__in=set(
                    self.request.user.get_descendants(include_self=True))))
        elif is_consultant_or_high:
            return self.annotate_queryset(self.summit.ankets.filter(user__level=0))
        else:
            return self.annotate_queryset(self.summit.ankets.filter(user__master_id=self.request.user.id))


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


class SummitTicketViewSet(viewsets.ModelViewSet):
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


class SummitTypeViewSet(viewsets.ModelViewSet):
    queryset = SummitType.objects.all()
    serializer_class = SummitTypeSerializer
    permission_classes = (IsAuthenticated,)

    @detail_route(methods=['get'], )
    def is_member(self, request, pk=None):
        user_id = request.query_params.get('user_id')
        if user_id and not user_id.isdigit():
            return Response({'result': 'user_id должен быть числом.'},
                            status=status.HTTP_400_BAD_REQUEST)
        if not user_id:
            user_id = request.user.id
        data = {
            'result': SummitAnket.objects.filter(
                user_id=user_id, summit__type_id=pk, visited=True).exists(),
            'user_id': user_id,
        }

        return Response(data)


class SummitAnketWithNotesViewSet(viewsets.ModelViewSet):
    queryset = SummitAnket.objects.select_related('user', 'user__hierarchy', 'user__master'). \
        prefetch_related('user__divisions', 'user__departments', 'notes')
    serializer_class = SummitAnketWithNotesSerializer
    pagination_class = None
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('user',)


def generate_code(request):
    code = request.GET.get('code', '00000000')

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
    report_date = request.query_params.get('date', datetime.now().strftime('%Y-%m-%d'))
    try:
        report_date = datetime.strptime(report_date, '%Y-%m-%d')
    except ValueError:
        report_date = datetime.now()

    bishops = get_report_by_bishop_or_high(summit_id, report_date, department, fio)

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
    ticket.users.set([a[0] for a in ankets])

    generate_tickets.apply_async(args=[summit_id, ankets, ticket.id])

    SummitAnket.objects.filter(id__in=[a[0] for a in ankets]).update(ticket_status=SummitAnket.DOWNLOADED)

    return Response(data={'ticket_id': ticket.id})


class SummitVisitorLocationViewSet(viewsets.ModelViewSet):
    serializer_class = SummitVisitorLocationSerializer
    queryset = SummitVisitorLocation.objects.all().prefetch_related('visitor')
    pagination_class = None
    permission_classes = (HasAPIAccess,)

    @list_route(methods=['POST'])
    def post(self, request):
        if not request.data.get('data'):
            raise exceptions.ValidationError(_('Невозможно создать запись, поле {data} не переданно'))
        data = request.data.get('data')
        visitor = get_object_or_404(SummitAnket, pk=request.data.get('visitor_id'))

        for chunk in data:
            if SummitVisitorLocation.objects.filter(visitor=visitor, date_time=chunk.get('date_time')).exists():
                continue
            SummitVisitorLocation.objects.create(visitor=visitor,
                                                 date_time=chunk.get('date_time', datetime.now()),
                                                 longitude=chunk.get('longitude', 0),
                                                 latitude=chunk.get('latitude', 0),
                                                 type=chunk.get('type', 1))

        return Response({'message': 'Successful created'},
                        status=status.HTTP_201_CREATED)

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
        date_format = '%Y-%m-%d %H:%M:%S'
        try:
            date_time = datetime.strptime(date_time.replace('T', ' '), date_format)
        except ValueError:
            raise exceptions.ValidationError(
                'Не верный формат даты. Передайте дату в формате date %Y-%m-%dT%H:%M:%S')

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


class SummitEventTableViewSet(viewsets.ModelViewSet):
    queryset = SummitEventTable.objects.all()
    serializer_class = SummitEventTableSerializer
    permission_classes = (HasAPIAccess,)
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('summit',)
    pagination_class = None


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
        date_today = datetime.now().date()
        if SummitAttend.objects.filter(anket_id=anket.id, date=date_today).exists():
            raise exceptions.ValidationError(
                _('Запись о присутствии этой анкеты за сегоднящней день уже существует'))

    @list_route(methods=['GET'], serializer_class=SummitAcceptMobileCodeSerializer)
    def accept_mobile_code(self, request):
        code = request.query_params.get('code', '')
        anket = get_object_or_404(SummitAnket, code=code)
        AnketStatus.objects.get_or_create(
            anket=anket, defaults={'reg_code_requested': True,
                                   'reg_code_requested_date': datetime.now()})

        if anket.status.active is False:
            return Response({'error_message': 'Данная анкета не активна', 'error_code': 1},
                            status=status.HTTP_200_OK)

        SummitAttend.objects.create(anket=anket, date=datetime.now().date())
        anket = self.serializer_class(anket)
        return Response(anket.data)

<<<<<<< HEAD
    @list_route(methods=['POST'], serializer_class=AnketActiveStatusSerializer)
=======
    @list_route(methods=['POST'], serializer_class=AnketActiveStatusSerializer,
                permission_classes=(IsAuthenticated,))
>>>>>>> f2477eda0401e29e58ab6300610bbc0b5e770edc
    def anket_active_status(self, request):
        active = request.data.get('active', 1)
        anket_id = request.data.get('anket_id', None)
        anket = get_object_or_404(SummitAnket, pk=anket_id)
<<<<<<< HEAD
=======
        AnketStatus.objects.get_or_create(anket=anket)
>>>>>>> f2477eda0401e29e58ab6300610bbc0b5e770edc

        if active == 1:
            anket.status.active = True
        anket.status.active = False
<<<<<<< HEAD
        anket.save()
=======
        anket.status.save()
>>>>>>> f2477eda0401e29e58ab6300610bbc0b5e770edc

        return Response({'message': _('Статус анкеты пользователя {%s} успешно изменен.') % anket.fullname,
                        'active': '%s' % active}, status=status.HTTP_200_OK)
