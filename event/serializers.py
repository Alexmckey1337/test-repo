# -*- coding: utf-8
from __future__ import unicode_literals

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from django.utils.translation import ugettext_lazy as _

from group.models import Church
from group.serializers import (UserNameSerializer, ChurchNameSerializer,
                               HomeGroupNameSerializer)
from account.models import CustomUser
from .models import Meeting, MeetingAttend, MeetingType, ChurchReport, AbstractStatusModel
from datetime import datetime
from common.fields import ReadOnlyChoiceField


class ValidateDataBeforeUpdateMixin(object):
    @staticmethod
    def validate_before_serializer_update(instance, validated_data, not_editable_fields):
        if instance.status != AbstractStatusModel.SUBMITTED:
            raise serializers.ValidationError({
                'detail': _('Невозможно обновить методом UPDATE. Отчет - {%s} еще небыл подан.') % instance
            })

        if instance.date.isocalendar()[1] > validated_data.get('date').isocalendar()[1]:
            raise serializers.ValidationError({
                'detail': _('Невозможно подать отчет, переданная дата - %s. '
                            'Отчет должен подаваться за ту неделю на которой был создан.' % validated_data.get('date'))
            })

        [validated_data.pop(field, None) for field in not_editable_fields]

        return instance, validated_data


class MeetingTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingType
        fields = ('id', 'code', 'name')


class MeetingAttendSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(source='user.fullname')
    spiritual_level = ReadOnlyChoiceField(source='user.spiritual_level',
                                          choices=CustomUser.SPIRITUAL_LEVEL_CHOICES, read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)

    class Meta:
        model = MeetingAttend
        fields = ('id', 'user_id', 'fullname', 'spiritual_level', 'attended', 'note', 'phone_number')


class MeetingVisitorsSerializer(serializers.ModelSerializer):
    spiritual_level = ReadOnlyChoiceField(
        choices=CustomUser.SPIRITUAL_LEVEL_CHOICES, read_only=True)
    user_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = CustomUser
        fields = ('user_id', 'fullname', 'spiritual_level', 'phone_number')


class MeetingSerializer(serializers.ModelSerializer, ValidateDataBeforeUpdateMixin):
    owner = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.filter(
        home_group__leader__id__isnull=False).distinct())
    date = serializers.DateField(default=datetime.now().date())
    can_submit = serializers.BooleanField(read_only=True)
    cant_submit_cause = serializers.CharField(read_only=True)

    class Meta:
        model = Meeting
        fields = ('id', 'home_group', 'owner', 'type', 'date', 'total_sum',
                  'status', 'can_submit', 'cant_submit_cause')

        validators = [
            UniqueTogetherValidator(
                queryset=Meeting.objects.all(),
                fields=('home_group', 'type', 'date')
            )]

    def create(self, validated_data):
        owner = validated_data.get('owner')
        home_group = validated_data.get('home_group')
        if home_group.leader != owner:
            raise serializers.ValidationError({
                'detail': _('Переданный лидер не являетя лидером данной Домашней Группы')
            })

        meeting = Meeting.objects.create(**validated_data)
        return meeting


class MeetingListSerializer(MeetingSerializer):
    visitors_absent = serializers.IntegerField()
    visitors_attended = serializers.IntegerField()
    type = MeetingTypeSerializer()
    home_group = HomeGroupNameSerializer()
    owner = UserNameSerializer()
    status = serializers.JSONField(source='get_status_display')

    class Meta(MeetingSerializer.Meta):
        fields = MeetingSerializer.Meta.fields + (
            'phone_number', 'visitors_attended', 'visitors_absent', 'link')
        read_only_fields = ['__all__']


class MeetingDetailSerializer(MeetingSerializer):
    attends = MeetingAttendSerializer(many=True, required=False, read_only=True)
    home_group = HomeGroupNameSerializer(read_only=True, required=False)
    type = MeetingTypeSerializer(read_only=True, required=False)
    owner = UserNameSerializer(read_only=True, required=False)
    status = serializers.ReadOnlyField(read_only=True, required=False)

    not_editable_fields = ['home_group', 'owner', 'type', 'status']

    class Meta(MeetingSerializer.Meta):
        fields = MeetingSerializer.Meta.fields + ('attends', 'table_columns')

    def update(self, instance, validated_data):
        instance, validated_data = self.validate_before_serializer_update(
            instance, validated_data, self.not_editable_fields)

        return super(MeetingDetailSerializer, self).update(instance, validated_data)


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
        read_only_fields = ['__all__']


class MeetingDashboardSerializer(serializers.ModelSerializer):
    meetings_submitted = serializers.IntegerField()
    meetings_in_progress = serializers.IntegerField()
    meetings_expired = serializers.IntegerField()

    class Meta:
        model = Meeting
        fields = ('meetings_submitted', 'meetings_in_progress', 'meetings_expired')
        read_only_fields = ['__all__']


class ChurchReportListSerializer(serializers.ModelSerializer, ValidateDataBeforeUpdateMixin):
    pastor = UserNameSerializer()
    church = ChurchNameSerializer()
    date = serializers.DateField(default=datetime.now().date())

    class Meta:
        model = ChurchReport
        fields = ('id', 'pastor', 'church', 'date', 'status', 'link', 'count_people', 'new_people',
                  'count_repentance', 'tithe', 'donations', 'pastor_tithe')
        read_only_fields = ['__all__']


class ChurchReportSerializer(ChurchReportListSerializer):
    church = serializers.PrimaryKeyRelatedField(queryset=Church.objects.all(), required=False)
    pastor = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.filter(
        church__pastor__id__isnull=False).distinct(), required=False)
    status = serializers.IntegerField(default=1)
    can_submit = serializers.BooleanField(read_only=True)
    cant_submit_cause = serializers.CharField(read_only=True)

    not_editable_fields = ['church', 'pastor', 'status']

    class Meta(ChurchReportListSerializer.Meta):
        fields = ChurchReportListSerializer.Meta.fields + ('currency_donations', 'transfer_payments',
                                                           'can_submit', 'cant_submit_cause')
        read_only_fields = None

        validators = [
            UniqueTogetherValidator(
                queryset=ChurchReport.objects.all(),
                fields=('church', 'date', 'status')
            )]

    def update(self, instance, validated_data):
        instance, validated_data = self.validate_before_serializer_update(
            instance, validated_data, self.not_editable_fields)

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
        read_only_fields = ['__all__']
