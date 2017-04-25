# -*- coding: utf-8
from __future__ import unicode_literals

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from rest_framework import exceptions
from django.utils.translation import ugettext_lazy as _

from group.models import Church
from group.serializers import (UserNameSerializer, ChurchNameSerializer,
                               HomeGroupNameSerializer)
from account.models import CustomUser
from .models import Meeting, MeetingAttend, MeetingType, ChurchReport


class MeetingTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingType
        fields = ('id', 'code')


class MeetingAttendSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingAttend
        fields = ('id', 'user', 'attended', 'note')


class MeetingCreateSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.filter(
       home_group__leader__id__isnull=False).distinct())

    class Meta:
        model = Meeting
        fields = ('id', 'home_group', 'owner', 'type', 'date', 'status',
                  'total_sum',)

        validators = [
            UniqueTogetherValidator(
                queryset=Meeting.objects.all(),
                fields=('home_group', 'type', 'date')
            )]

    def create(self, validated_data):
        home_group = validated_data.get('home_group')
        owner = validated_data.get('owner')
        if home_group.leader != owner:
            raise exceptions.ValidationError(_('Невозможно создать отчет. '
                                               'Переданный лидер - {%s} не является '
                                               'лидером данной Домашней Группы.' % owner))

        meeting = Meeting.objects.create(**validated_data)
        return meeting


class MeetingSerializer(MeetingCreateSerializer):
    visitors_absent = serializers.IntegerField(read_only=True)
    visitors_attended = serializers.IntegerField(read_only=True)
    type = MeetingTypeSerializer()
    home_group = HomeGroupNameSerializer()
    owner = UserNameSerializer()

    class Meta(MeetingCreateSerializer.Meta):
        fields = MeetingCreateSerializer.Meta.fields + (
            'phone_number', 'visitors_attended', 'visitors_absent')
        read_only_fields = ('__all__',)


class MeetingDetailSerializer(MeetingCreateSerializer):
    attends = MeetingAttendSerializer(many=True, required=False, read_only=True)

    class Meta(MeetingCreateSerializer.Meta):
        fields = MeetingCreateSerializer.Meta.fields + ('attends',)


class MeetingStatisticSerializer(serializers.ModelSerializer):
    total_visitors = serializers.IntegerField()
    total_visits = serializers.IntegerField()
    total_absent = serializers.IntegerField()
    new_repentance = serializers.IntegerField()
    total_donations = serializers.DecimalField(max_digits=13, decimal_places=0)
    reports_in_progress = serializers.IntegerField()
    reports_submitted = serializers.IntegerField()
    reports_expired = serializers.IntegerField()

    class Meta:
        model = Meeting
        fields = ('total_visitors', 'total_visits', 'total_absent', 'total_donations',
                  'new_repentance', 'reports_in_progress', 'reports_submitted',
                  'reports_expired')


class ChurchReportListSerializer(serializers.ModelSerializer):
    pastor = UserNameSerializer(read_only=True)
    church = ChurchNameSerializer(read_only=True)

    class Meta:
        model = ChurchReport
        fields = ('id', 'pastor', 'church', 'date', 'count_people', 'tithe', 'donations',
                  'transfer_payments', 'status')


class ChurchReportSerializer(ChurchReportListSerializer):
    church = serializers.PrimaryKeyRelatedField(queryset=Church.objects.all(), required=False)
    pastor = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.filter(
        church__pastor__id__isnull=False).distinct(), required=False)

    class Meta(ChurchReportListSerializer.Meta):
        fields = ChurchReportListSerializer.Meta.fields + (
            'new_people', 'count_repentance', 'currency_donations', 'pastor_tithe')

        validators = [
            UniqueTogetherValidator(
                queryset=ChurchReport.objects.all(),
                fields=('church', 'date', 'status')
            )]

    def create(self, validate_data):
        church = validate_data.get('church')
        pastor = validate_data.get('pastor')
        if church.pastor != pastor:
            raise exceptions.ValidationError(_('Невозможно создать отчет. '
                                               'Переданный пастор - {%s} не является '
                                               'пастором данной Церкви.' % pastor))

        church_report = ChurchReport.objects.create(**validate_data)
        return church_report

    def update(self, instance, validated_data):
        if instance.status != 2:
            raise exceptions.ValidationError(_('Невозможно обновить методом UPDATE. '
                                               'Отчет - {%s} еще небыл заполнен.') % instance)

        return super(ChurchReportSerializer, self).update(instance, validated_data)


class ChurchReportStatisticSerializer(serializers.ModelSerializer):
    total_peoples = serializers.IntegerField()
    total_new_peoples = serializers.IntegerField()
    total_repentance = serializers.IntegerField()
    total_tithe = serializers.DecimalField(max_digits=13, decimal_places=0)
    total_donations = serializers.DecimalField(max_digits=13, decimal_places=0)
    total_transfer_payments = serializers.DecimalField(max_digits=13, decimal_places=0)
    total_pastor_tithe = serializers.DecimalField(max_digits=13, decimal_places=0)

    class Meta:
        model = ChurchReport
        fields = ('id', 'total_peoples', 'total_new_peoples', 'total_repentance',
                  'total_tithe', 'total_donations', 'total_transfer_payments',
                  'total_pastor_tithe')
