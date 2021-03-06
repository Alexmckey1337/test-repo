from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.account.api.filters import FilterByUserBirthday, FilterByUserRepentance
from apps.account.models import CustomUser
from apps.notification.api.serializers import BirthdayNotificationSerializer, RepentanceNotificationSerializer
from apps.notification.backend import RedisBackend
from apps.summit.models import SummitTicket


class NotificationPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'results': data,
        })


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    permission_classes = (IsAuthenticated,)
    pagination_class = NotificationPagination
    serializer_class = BirthdayNotificationSerializer

    @action(detail=False)
    def tickets(self, request):
        try:
            r = RedisBackend()
            ticket_ids = r.smembers('summit:ticket:{}'.format(request.user.id))
            tickets = SummitTicket.objects.filter(id__in=ticket_ids)
        except Exception as err:
            tickets = SummitTicket.objects.none()
            print(err)
        return Response({'tickets_count': tickets.count()})

    @action(detail=False, methods=['GET'],
            filter_backends=[FilterByUserBirthday],
            serializer_class=BirthdayNotificationSerializer,
            pagination_class=NotificationPagination)
    def birthdays(self, request):
        birthdays = self.filter_queryset(self.request.user.get_descendants())

        if request.query_params.get('only_count'):
            return Response({'birthdays_count': len(birthdays)})

        page = self.paginate_queryset(birthdays)
        if page is not None:
            birthdays = self.get_serializer(page, many=True)
            return self.get_paginated_response(birthdays.data)

        birthdays = self.serializer_class(birthdays, many=True)
        return Response(birthdays.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'],
            filter_backends=[FilterByUserRepentance],
            serializer_class=RepentanceNotificationSerializer,
            pagination_class=NotificationPagination)
    def repentance(self, request):
        repentance = self.filter_queryset(self.request.user.get_descendants())

        if request.query_params.get('only_count'):
            return Response({'repentance_count': len(repentance)})

        page = self.paginate_queryset(repentance)
        if page is not None:
            repentance = self.get_serializer(page, many=True)
            return self.get_paginated_response(repentance.data)

        repentance = self.serializer_class(repentance, many=True)
        return Response(repentance.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def exports(self, request):
        try:
            r = RedisBackend()
            export_urls = r.smembers('export:%s' % request.user.id)
            result = []
            for url in export_urls:
                result.append({'url': url, 'name': url.decode('utf8').split('/')[-1].split('.')[0]})
            result.sort(key=lambda x: x['name'].split('_')[-1].replace(':', ''), reverse=True)
        except Exception as err:
            print(err)
            result = []

        return Response({'export_urls': result})
