# -*- coding: utf-8
from models import Participation, Event
from serializers import ParticipationSerializer, EventSerializer
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
from rest_framework.permissions import AllowAny
import hashlib
import random
import json
from account.models import CustomUser as User
from django.utils import timezone
from datetime import timedelta
from report.models import UserReport
from event.models import VERBOSE_FIELDS as verbose_fields
from django.db import IntegrityError

def sync_user(user):
    events = Event.objects.all()
    for event in events:
        participation = Participation.objects.filter(user=user, event=event).first()
        if not participation:
            participation = Participation.objects.create(user=user, event=event, check=False)
            participation.save()
    return True

def sync_event(event):
    users = User.objects.all()
    for user in users:
        participation = Participation.objects.filter(user=user, event=event).first()
        if not participation:
            participation = Participation.objects.create(user=user, event=event, check=False)
            participation.save()
    return True


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    filter_backends = (filters.DjangoFilterBackend,
                       filters.SearchFilter,)
    search_fields = ('@date', 'title', )
    filter_fields = ['date', ]

    @list_route()
    def today(self, request):
        weekday = timezone.now().weekday() + 1
        date = timezone.now().date()
        date_events = Event.objects.filter(date=date).all()
        weekday_events = Event.objects.filter(day=weekday, cyclic=True).all()
        objects = date_events | weekday_events
        page = self.paginate_queryset(objects)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(objects, many=True)
        return Response(serializer.data)

    @list_route()
    def last_week(self, request):
        day = timezone.now().date() - timedelta(days=7)
        date_events = Event.objects.filter(date__gte=day, date__lte=timezone.now().date()).all()
        weekday_events = Event.objects.filter(cyclic=True).all()
        objects = date_events | weekday_events
        page = self.paginate_queryset(objects)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(objects, many=True)
        return Response(serializer.data)

    @list_route()
    def last_month(self, request):
        day = timezone.now().date() - timedelta(days=30)
        date_events = Event.objects.filter(date__gte=day, date__lte=timezone.now().date()).all()
        weekday_events = Event.objects.filter(cyclic=True).all()
        objects = date_events | weekday_events
        page = self.paginate_queryset(objects)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(objects, many=True)
        return Response(serializer.data)


    @list_route()
    def last_year(self, request):
        day = timezone.now().date() - timedelta(days=365)
        date_events = Event.objects.filter(date__gte=day, date__lte=timezone.now().date()).all()
        weekday_events = Event.objects.filter(cyclic=True).all()
        objects = date_events | weekday_events
        page = self.paginate_queryset(objects)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(objects, many=True)
        return Response(serializer.data)


class ParticipationViewSet(viewsets.ModelViewSet):
    queryset = Participation.objects.all()
    serializer_class = ParticipationSerializer
    filter_backends = (filters.DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter,)
    t = tuple(verbose_fields.values())
    ordering_fields = t
    filter_fields = ('user', 'event', 'user__first_name', 'user__last_name', 'user__middle_name', 'user__phone_number', 'user__email', 'user__master', 'user__department', 'user__hierarchy' )

@api_view(['POST'])
def create_event(request):
    response_dict = dict()
    if request.method == 'POST':
        data = request.data
        if not 'id' in  data.keys():
            object = Event.objects.filter(title=data['title'],
                                          day=data['day'],
                                          ).first()
            if object:
                response_dict['message'] = u"Это событие уже существует"
            else:
                try:
                    object = Event.objects.create(title=data['title'],
                                                  date=data['date'],
                                                  day=data['day'],
                                                  cyclic=['cyclic'])

                except IntegrityError:
                    response_dict['message'] = u"Событие c nfrим именем уже существует"
                else:
                    object.save()
                    sync_event(object)
                    response_dict['message'] = u"Событие успешно добавлено"
        else:
            object = Event.objects.filter(id=data['id']).first()
            if object:
                for key, value in data.iteritems():
                    setattr(object, key, value)
                object.save()
                response_dict['message'] = u"Событие успешно изменен"
    return Response(response_dict)

@api_view(['POST'])
def delete_event(request):
    if request.method == 'POST':
        data = request.data
        object = Event.objects.filter(id=data['id']).first()
        if object:
            object.delete()
            return Response({"message": "Событие было удалено успешно"})
        else:
            return Response({"message": "Событие не существует"})




@api_view(['POST'])
def delete_participation(request):
    if request.method == 'POST':
        data = request.data
        participation = Participation.objects.filter(id=data['id']).first()
        if participation:
            participation.delete()
            return Response({"message": "Участник был удален успешно"})
        else:
            return Response({"message": "Участника не существует"})



@api_view(['POST'])
def create_participations(request):
    response_dict = dict()
    if request.method == 'POST':
        data = request.data
        event = Event.objects.filter(id=data['event_id']).first()
        user_ids = data['user_id']
        response_dict['message'] = u"Участники успешно добавлены"
        for id in user_ids:
            user = User.objects.filter(id=id).first()
            if user:
                if not Participation.objects.filter(user=user, event=event).first():
                    participation = Participation.objects.create(user=user, event=event)
                    participation.save()
                else:
                    response_dict['message'] = u"Нельзя дважды добавить одного и того же участника"

        return Response(response_dict)
def recount(user, event):
    master = user.master
    if user.master:
        report = UserReport.objects.filter(user=master, event=event).last()
        report.get_count()
        recount(master, event)
    else:
        pass
    return True


@api_view(['POST'])
def update_participation(request):
    response_dict = dict()
    date = timezone.now().date()
    if request.method == 'POST':
        data = request.data
        participation = Participation.objects.filter(id=data['id']).first()
        if participation:

            for key, item in data.iteritems():
                if not key == 'id':
                    setattr(participation, key, item)
                    participation.save()

            if participation.check:
                report = UserReport.objects.filter(user=participation.user, event=participation.event).last()
                report.count = 1
                report.save()
                recount(participation.user, participation.event)
            else:
                report = UserReport.objects.filter(user=participation.user, event=participation.event).last()
                report.count = 0
                report.save()
                recount(participation.user, participation.event)
                        
            response_dict['message'] = "Ok"
        else:
            response_dict['message'] = 'Not Ok'
    return Response(response_dict)




