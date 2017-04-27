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


class ValidateDataBeforeUpdateMixin(object):

    @staticmethod
    def validate_before_serializer_update(instance, validated_data, not_editable_fields):
        if instance.status != AbstractStatusModel.SUBMITTED:
            raise serializers.ValidationError(
                _('Невозможно обновить методом UPDATE. '
                  'Отчет - {%s} еще небыл подан.') % instance)

        if instance.date > validated_data.get('date'):
            raise serializers.ValidationError(
                _('Невозможно подать отчет. Переданная дата подачи отчета - {%s} '
                  'меньше чем дата его создания.' % validated_data.get('date'))
            )
        [validated_data.pop(field, None) for field in not_editable_fields]

        return instance, validated_data


class MeetingTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingType
        fields = ('id', 'code')


class MeetingAttendSerializer(serializers.ModelSerializer):

    class Meta:
        model = MeetingAttend
        fields = ('id', 'user', 'attended', 'note', 'user_phone_number')


class MeetingSerializer(serializers.ModelSerializer, ValidateDataBeforeUpdateMixin):
    owner = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.filter(
        home_group__leader__id__isnull=False).distinct())

    class Meta:
        model = Meeting
        fields = ('id', 'home_group', 'owner', 'type', 'date', 'total_sum',
                  'status')

        validators = [
            UniqueTogetherValidator(
                queryset=Meeting.objects.all(),
                fields=('home_group', 'type', 'date')
            )]

    def create(self, validated_data):
        owner = validated_data.get('owner')
        home_group = validated_data.get('home_group')
        if home_group.leader != owner:
            raise serializers.ValidationError(
                _('Переданный лидер не являетя лидером данной Домашней Группы'))

        meeting = Meeting.objects.create(**validated_data)

        return meeting


class MeetingListSerializer(MeetingSerializer):
    visitors_absent = serializers.IntegerField()
    visitors_attended = serializers.IntegerField()
    type = MeetingTypeSerializer()
    home_group = HomeGroupNameSerializer()
    owner = UserNameSerializer()
    status = serializers.CharField(source='get_status_display')

    class Meta(MeetingSerializer.Meta):
        fields = MeetingSerializer.Meta.fields + (
            'phone_number', 'visitors_attended', 'visitors_absent')
        read_only_fields = ['__all__']


class MeetingDetailSerializer(MeetingSerializer):
    attends = MeetingAttendSerializer(many=True, required=False, read_only=True)
    home_group = HomeGroupNameSerializer(read_only=True, required=False)
    type = MeetingTypeSerializer(read_only=True, required=False)
    owner = UserNameSerializer(read_only=True, required=False)
    status = serializers.ReadOnlyField(read_only=True, required=False)

    not_editable_fields = ['home_group', 'owner', 'type', 'status']

    class Meta(MeetingSerializer.Meta):
        fields = MeetingSerializer.Meta.fields + ('attends',)

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


class ChurchReportListSerializer(serializers.ModelSerializer, ValidateDataBeforeUpdateMixin):
    pastor = UserNameSerializer()
    church = ChurchNameSerializer()
    status = serializers.CharField(source='get_status_display')

    class Meta:
        model = ChurchReport
        fields = ('id', 'pastor', 'church', 'date', 'count_people', 'tithe', 'donations',
                  'transfer_payments', 'status')
        read_only_fields = ['__all__']


class ChurchReportSerializer(ChurchReportListSerializer):
    church = serializers.PrimaryKeyRelatedField(queryset=Church.objects.all(), required=False)
    pastor = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.filter(
        church__pastor__id__isnull=False).distinct(), required=False)

    not_editable_fields = ['church', 'pastor', 'status']

    class Meta(ChurchReportListSerializer.Meta):
        fields = ChurchReportListSerializer.Meta.fields + (
            'new_people', 'count_repentance', 'currency_donations', 'pastor_tithe')
        read_only_fields = None

        validators = [
            UniqueTogetherValidator(
                queryset=ChurchReport.objects.all(),
                fields=('church', 'date', 'status')
            )]

    def create(self, validated_data):
        pastor = validated_data.get('pastor')
        church = validated_data.get('church')
        if church.pastor != pastor:
            raise serializers.ValidationError(
                _('Переданный пастор не являетя пастором данной Церкви'))

        church_report = ChurchReport.objects.create(**validated_data)

        return church_report

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
