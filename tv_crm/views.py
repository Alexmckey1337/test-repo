# -*- coding: utf-8
from serializers import LastCallSerializer, UserLittleSerializer, SynopsisSerializer
from rest_framework import viewsets, filters
from models import LastCall, Synopsis
from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework.decorators import api_view
from account.models import CustomUser
from status.models import Status
from django.http import HttpResponse
import json
from rest_framework.permissions import IsAuthenticated

def sync_user_call():
    users = CustomUser.objects.all()
    for user in users:
        last_call = LastCall.objects.filter(user_id=user.id)
        if not last_call:
            LastCall.objects.create(user=user, last_responce='')
    return True


def sync_unique_user_call(user):
    call = LastCall.objects.filter(user=user).first()
    if call:
        pass
    else:
        LastCall.objects.create(user=user, last_responce='')
    return True


class LastCallViewSet(viewsets.ModelViewSet):
    queryset_pastor = LastCall.objects.filter(user__hierarchy__level=4).order_by('user__master')
    queryset = queryset_pastor
    serializer_class = LastCallSerializer
    filter_backends = (filters.DjangoFilterBackend,
                       filters.SearchFilter,)
    permission_classes = (IsAuthenticated,)
    search_fields = ('user__first_name',
                     'user__last_name',
                     'user__middle_name',
                     'user__hierarchy__title',
                     'user__phone_number',
                     'user__city',
                     '@date',
                     'user__master__first_name',
                     'user__master__last_name',
                     'user__master__middle_name',
                     )
    filter_fields = ('user__department',
                     'user__master__id',
                     )

    @list_route()
    def subordinate(self, request):
        user = request.user
        tv_consult = Status.objects.get(id=6)
        if tv_consult in user.statuses.all():
            queryset = LastCall.objects.filter(user__hierarchy__level=4).order_by('user__master')
        else:
            queryset = LastCall.objects.filter(user__master=user).filter(user__hierarchy__level=4).order_by('user__master')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = LastCallSerializer(queryset, context={'request': request}, many=True)
        return Response(serializer.data)

    @list_route()
    def check_tv_consultant(self, request):
        user = request.user
        data = {}
        data['is_consultant'] = 'false'
        if user.statuses.filter(id=6):
            data['is_consultant'] = 'true'
        data['user_id'] = user.id
        return HttpResponse(json.dumps(data), content_type='application/json')


class CallStatViewSet(viewsets.ModelViewSet):
    users = CustomUser.objects.filter(disciples__hierarchy__level=4).distinct()
    queryset = users
    serializer_class = UserLittleSerializer
    filter_backends = (filters.DjangoFilterBackend,
                       filters.SearchFilter,)
    permission_classes = (IsAuthenticated,)
    search_fields = ('first_name',
                     'last_name',
                     'middle_name',
                     'email',
                     'phone_number',
                     'city',
                     )
    filter_fields = ('department',
                     )


@api_view(['POST'])
def update_last_call(request):
    if request.method == 'POST':
        user_id = request.data['id']
        text_responce = request.data['text_responce']
        last_call = LastCall.objects.filter(user=user_id).first()
        if last_call:
            last_call.last_responce = text_responce
            last_call.save()
            return Response({"message": u"Данные успешно измененны"})
        else:
            user = CustomUser.objects.get(id=user_id)
            LastCall.objects.create(user=user, last_responce=text_responce)
            return Response({"message": u"Данные успешно занесенны в базу данных"})


class SynopsisViewSet(viewsets.ModelViewSet):
    queryset = Synopsis.objects.all()
    serializer_class = SynopsisSerializer
    permission_classes = (IsAuthenticated,)

    @list_route(methods=['post'])
    def post_data(self, request):
        if request.method == 'POST':
            if 'id' in request.data.keys():
                synopsis_id = request.data['id']
                synopsis = Synopsis.objects.get(id=synopsis_id)
                for key in request.data:
                    if key == 'history_description':
                        synopsis.history_description = request.data['history_description']
                    elif key == 'decision_description':
                        synopsis.decision_description = request.data['decision_description']
                    elif key == 'recovery_docs':
                        synopsis.recovery_docs = request.data['recovery_docs']
                    elif key == 'recovery_information':
                        synopsis.recovery_information = request.data['recovery_information']
                    elif key == 'how_recovery':
                        synopsis.how_recovery = request.data['how_recovery']
                    elif key == 'how_to_know':
                        synopsis.how_to_know = request.data['how_to_know']
                    elif key == 'sick_description':
                        synopsis.sick_description = request.data['sick_description']
                    elif key == 'sick_docs':
                        synopsis.sick_docs = request.data['sick_docs']
                    elif key == 'diagnosis':
                        synopsis.diagnosis = request.data['diagnosis']
                    elif key == 'producer':
                        synopsis.producer = request.data['producer']
                    elif key == 'survey_date':
                        synopsis.survey_date = request.data['survey_date']
                    elif key == 'hero':
                        synopsis.hero = request.data['hero']
                    elif key == 'phone_number':
                        synopsis.phone_number = request.data['phone_number']
                    elif key == 'healing_description':
                        synopsis.healing_description = request.data['healing_description']
                synopsis.save()
                return Response({"message": u"Данные успешно измененны",
                                 "status": True})
            elif 'hero' in request.data.keys():
                history_description = request.data['history_description']
                hero = request.data['hero']
                phone_number = request.data['phone_number']
                if len(hero) == 0 or len(phone_number) == 0 or len(history_description) == 0:
                    return Response({"message": u"Заполните пустые поля",
                                     "status": False})
                else:
                    Synopsis.objects.create(
                        hero=hero,
                        history_description=request.data['history_description'],
                        diagnosis=request.data['diagnosis'],
                        sick_docs=request.data['sick_docs'],
                        sick_description=request.data['sick_description'],
                        healing_description=request.data['healing_description'],
                        how_to_know=request.data['how_to_know'],
                        how_recovery=request.data['how_recovery'],
                        recovery_information=request.data['recovery_information'],
                        recovery_docs=request.data['recovery_docs'],
                        decision_description=request.data['decision_description'],
                        producer=request.data['producer'],
                        survey_date=request.data['survey_date'],
                        interviewer=request.user,
                        phone_number=phone_number,
                    )
                return Response({"message": u"Данные успешно занесенны в базу данных",
                                 'status': True})
            else:
                return Response({"message": u"Некорректные данные",
                                 'status': False})
