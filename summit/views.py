# -*- coding: utf-8
from __future__ import unicode_literals

from dbmail import send_db_mail
from django.db.models import Case, When, BooleanField
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions, viewsets, filters, status, mixins
from rest_framework.decorators import list_route, detail_route, api_view
from rest_framework.generics import get_object_or_404, GenericAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.viewsets import GenericViewSet

from account.models import CustomUser
from common.filters import FieldSearchFilter
from payment.serializers import PaymentShowWithUrlSerializer
from payment.views_mixins import CreatePaymentMixin, ListPaymentMixin
from summit.filters import FilterByClub, ProductFilter, SummitUnregisterFilter, ProfileFilter, \
    FilterProfileMasterTreeWithSelf, HasPhoto
from summit.pagination import SummitPagination
from summit.utils import generate_ticket
from .models import Summit, SummitAnket, SummitType, SummitLesson, SummitUserConsultant, SummitTicket
from .serializers import (
    SummitSerializer, SummitTypeSerializer, SummitUnregisterUserSerializer, SummitAnketSerializer,
    SummitAnketNoteSerializer, SummitAnketWithNotesSerializer, SummitLessonSerializer, SummitAnketForSelectSerializer,
    SummitTypeForAppSerializer, SummitAnketForAppSerializer, SummitShortSerializer, SummitAnketShortSerializer,
    SummitLessonShortSerializer, SummitTicketSerializer, SummitAnketForTicketSerializer)
from .tasks import generate_tickets


def get_success_headers(data):
    try:
        return {'Location': data[api_settings.URL_FIELD_NAME]}
    except (TypeError, KeyError):
        return {}


class SummitProfileListView(mixins.ListModelMixin, GenericAPIView):
    queryset = SummitAnket.objects.base_queryset().annotate_total_sum().annotate_full_name().order_by(
        'user__last_name', 'user__first_name', 'user__middle_name')
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
        'user__email', 'hierarchy__level',
    )
    filter_backends = (
        filters.DjangoFilterBackend,
        filters.OrderingFilter,
        FieldSearchFilter,
        FilterProfileMasterTreeWithSelf,
        FilterByClub,
        HasPhoto,
    )

    field_search_fields = {
        'search_fio': ('last_name', 'first_name', 'middle_name', 'search_name'),
        'search_email': ('user__email',),
        'search_phone_number': ('user__phone_number',),
        'search_country': ('country',),
        'search_city': ('city',),
    }

    def get(self, request, *args, **kwargs):
        self.summit_id = kwargs.get('pk', None)
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        qs = self.queryset.filter(summit_id=self.summit_id)
        return qs.for_user(self.request.user)


class SummitProfileViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                           mixins.DestroyModelMixin, GenericViewSet,
                           CreatePaymentMixin, ListPaymentMixin):
    queryset = SummitAnket.objects.base_queryset().annotate_total_sum()
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
            anket.code = '0{}'.format(4*000*000 + anket.id)
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


# FOR APP


class SummitTypeForAppViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = SummitType.objects.prefetch_related('summits')
    serializer_class = SummitTypeForAppSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class SummitAnketForAppViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = SummitAnket.objects.select_related('user').order_by('id')
    serializer_class = SummitAnketForAppSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    # filter_fields = ('summit', 'id')
    # filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_class = ProductFilter
    permission_classes = (AllowAny,)
    pagination_class = None


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

    return Response(data={'ticket_id': ticket.id})
