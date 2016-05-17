# -*- coding: utf-8
from models import Department, Hierarchy
from serializers import DepartmentSerializer, HierarchySerializer
from account.models import CustomUser as User
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


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class HierarchyViewSet(viewsets.ModelViewSet):
    queryset = Hierarchy.objects.exclude(title='Архонт').all()
    serializer_class = HierarchySerializer


@api_view(['POST'])
def create_department(request):
    response_dict = dict()
    if request.method == 'POST':
        user = request.user
        if user.is_staff:
            data = request.data
            department_title = data['title']
            department = Department.objects.filter(title=department_title).first()
            if department:
                response_dict['message'] = "Отдел с таким названием уже существует"
            else:
                department = Department.objects.create(title=department_title)
                department.save()
                response_dict['message'] = "Отдел успешно добавлен"
        else:
            response_dict['message'] = "Только администраторы имеют полномочия добавлять отделы"
    return Response(response_dict)


@api_view(['POST'])
def update_department(request):
    if request.method == 'POST':
        data = request.data
        object = Department.objects.filter(id=data['id']).first()
        if object:
            object.title = data['title']
            object.save()
            return Response({"message": "Отдел был изменен успешно"})
        else:
            return Response({"message": "Отдел не существует"})


@api_view(['POST'])
def delete_department(request):
    if request.method == 'POST':
        data = request.data
        object = Department.objects.filter(id=data['id']).first()
        if object:
            object.delete()
            return Response({"message": "Отдел был удален успешно"})
        else:
            return Response({"message": "Отдел не существует"})
