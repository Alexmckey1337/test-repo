# -*- coding: utf-8
from __future__ import unicode_literals

from datetime import datetime

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from apps.account.models import CustomUser
from common.fields import DecimalWithCurrencyField
from common.fields import ReadOnlyChoiceField
from apps.event.models import Meeting, MeetingAttend, MeetingType, ChurchReport, AbstractStatusModel
from apps.group.api.serializers import (
    UserNameSerializer, ChurchNameSerializer, HomeGroupNameSerializer, UserNameWithLinkSerializer)
from apps.group.models import Church
from apps.payment.api.serializers import CurrencySerializer


class ValidateDataBeforeUpdateMixin(object):
    @staticmethod
    def validate_before_serializer_update(instance, validated_data, not_editable_fields):
        if instance.status != AbstractStatusModel.SUBMITTED:
            raise serializers.ValidationError({
                'detail': _('Невозможно обновить методом UPDATE. Отчет - {%s} еще небыл подан.'
                            % instance)
            })

        if instance.date.isocalendar()[1] > validated_data.get('date').isocalendar()[1]:
            raise serializers.ValidationError({
                'detail': _('Невозможно подать отчет, переданная дата - %s. '
                            'Отчет должен подаваться за ту неделю на которой был создан.'
                            % validated_data.get('date'))
            })

        [validated_data.pop(field, None) for field in not_editable_fields]

        return instance, validated_data


class MeetingTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingType
        fields = ('id', 'code', 'name',)


class MeetingAttendSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(source='user.fullname')
    spiritual_level = ReadOnlyChoiceField(source='user.spiritual_level',
                                          choices=CustomUser.SPIRITUAL_LEVEL_CHOICES,
                                          read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)

    class Meta:
        model = MeetingAttend
        fields = ('id', 'user_id', 'fullname', 'spiritual_level', 'attended', 'note',
                  'phone_number',)


class MeetingVisitorsSerializer(serializers.ModelSerializer):
    spiritual_level = ReadOnlyChoiceField(
        choices=CustomUser.SPIRITUAL_LEVEL_CHOICES, read_only=True)
    user_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = CustomUser
        fields = ('user_id', 'fullname', 'spiritual_level', 'phone_number',)


class MeetingSerializer(serializers.ModelSerializer, ValidateDataBeforeUpdateMixin):
    owner = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.filter(
        home_group__leader__id__isnull=False).distinct())
    date = serializers.DateField(default=datetime.now().date())
    can_submit = serializers.BooleanField(read_only=True)
    cant_submit_cause = serializers.CharField(read_only=True)

    class Meta:
        model = Meeting
        fields = ('id', 'home_group', 'owner', 'type', 'date', 'total_sum',
                  'status', 'can_submit', 'cant_submit_cause', 'image')

        validators = [
            UniqueTogetherValidator(
                queryset=Meeting.objects.all(),
                fields=('home_group', 'type', 'date',)
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


class OwnerRelatedField(serializers.RelatedField):
    def get_attribute(self, instance):
        return instance.owner_id, instance.owner_name

    def to_representation(self, value):
        owner_id, owner_name = value
        return {
            'id': owner_id,
            'fullname': owner_name
        }


class MeetingListSerializer(MeetingSerializer):
    visitors_absent = serializers.IntegerField()
    visitors_attended = serializers.IntegerField()
    type = MeetingTypeSerializer()
    home_group = HomeGroupNameSerializer()
    owner = OwnerRelatedField(read_only=True)
    status = serializers.JSONField(source='get_status_display')

    class Meta(MeetingSerializer.Meta):
        fields = MeetingSerializer.Meta.fields + (
            'phone_number',
            'visitors_attended',
            'visitors_absent',
            'link',)
        read_only_fields = ['__all__']


class MeetingDetailSerializer(MeetingSerializer):
    attends = MeetingAttendSerializer(many=True, required=False, read_only=True)
    home_group = HomeGroupNameSerializer(read_only=True, required=False)
    type = MeetingTypeSerializer(read_only=True, required=False)
    owner = UserNameSerializer(read_only=True, required=False)
    status = serializers.ReadOnlyField(read_only=True, required=False)

    not_editable_fields = ['home_group', 'owner', 'type', 'status']

    class Meta(MeetingSerializer.Meta):
        fields = MeetingSerializer.Meta.fields + ('attends', 'table_columns',)

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
                  'reports_expired',)
        read_only_fields = ['__all__']


class MeetingDashboardSerializer(serializers.ModelSerializer):
    meetings_submitted = serializers.IntegerField()
    meetings_in_progress = serializers.IntegerField()
    meetings_expired = serializers.IntegerField()

    class Meta:
        model = Meeting
        fields = ('meetings_submitted', 'meetings_in_progress', 'meetings_expired')
        read_only_fields = ['__all__']


class MeetingSummarySerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source='fullname', read_only=True)
    master = UserNameWithLinkSerializer()
    meetings_submitted = serializers.IntegerField(read_only=True)
    meetings_in_progress = serializers.IntegerField(read_only=True)
    meetings_expired = serializers.IntegerField(read_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'owner', 'link', 'master', 'meetings_submitted', 'meetings_in_progress',
                  'meetings_expired')


class ChurchReportListSerializer(serializers.HyperlinkedModelSerializer,
                                 ValidateDataBeforeUpdateMixin):
    pastor = UserNameSerializer()
    church = ChurchNameSerializer()
    date = serializers.DateField(default=datetime.now().date())
    total_peoples = serializers.IntegerField(source='count_people', required=False)
    total_donations = serializers.DecimalField(source='donations', max_digits=13,
                                               decimal_places=0, required=False)
    total_pastor_tithe = serializers.DecimalField(source='pastor_tithe', max_digits=13,
                                                  decimal_places=0, required=False)
    total_tithe = serializers.DecimalField(source='tithe', max_digits=13,
                                           decimal_places=0, required=False)
    currency_donations = serializers.CharField(required=False, allow_blank=True)
    transfer_payments = serializers.DecimalField(max_digits=12, decimal_places=1, read_only=True)
    total_new_peoples = serializers.IntegerField(source='new_people', required=False)
    total_repentance = serializers.IntegerField(source='count_repentance', required=False)
    can_submit = serializers.BooleanField(read_only=True)
    cant_submit_cause = serializers.CharField(read_only=True)

    total_sum = DecimalWithCurrencyField(max_digits=12, decimal_places=0, read_only=True,
                                         currency_field='currency')
    value = serializers.DecimalField(max_digits=12, decimal_places=0, read_only=True)
    payment_status = serializers.IntegerField(read_only=True)
    currency = CurrencySerializer(read_only=True)

    class Meta:
        model = ChurchReport
        fields = ('id', 'pastor', 'church', 'date', 'status', 'link',
                  'total_peoples', 'total_new_peoples', 'total_repentance', 'transfer_payments',
                  'total_tithe', 'total_donations', 'total_pastor_tithe', 'currency_donations',
                  'can_submit', 'cant_submit_cause',
                  'value', 'total_sum', 'payment_status', 'currency', 'done')
        read_only_fields = ['__all__']


class ChurchReportSerializer(ChurchReportListSerializer):
    church = serializers.PrimaryKeyRelatedField(queryset=Church.objects.all(), required=False)
    pastor = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.filter(
        church__pastor__id__isnull=False).distinct(), required=False)
    status = serializers.IntegerField(default=ChurchReport.IN_PROGRESS)
    transfer_payments = serializers.DecimalField(max_digits=13, decimal_places=1)

    not_editable_fields = ['church', 'pastor', 'status', 'payment_status', 'value', 'total_sum']

    class Meta(ChurchReportListSerializer.Meta):
        fields = ChurchReportListSerializer.Meta.fields + ('comment',)

        read_only_fields = None

        validators = [
            UniqueTogetherValidator(
                queryset=ChurchReport.objects.all(),
                fields=('church', 'date', 'status')
            )]

    def update(self, instance, validated_data):
        instance, validated_data = self.validate_before_serializer_update(
            instance, validated_data, self.not_editable_fields)

        if validated_data.get('transfer_payments'):
            try:
                if instance.transfer_payments < validated_data['transfer_payments']:
                    instance.done = False
            except Exception:
                raise serializers.ValidationError(
                    {'message': '{transfer_payments} must be Integer or Decimal'})
        return super(ChurchReportSerializer, self).update(instance, validated_data)


class ChurchReportDetailSerializer(ChurchReportSerializer):
    pastor = UserNameSerializer()
    church = ChurchNameSerializer()


class ChurchReportStatisticSerializer(serializers.ModelSerializer):
    total_peoples = serializers.IntegerField()
    total_new_peoples = serializers.IntegerField()
    total_repentance = serializers.IntegerField()
    total_tithe = serializers.DecimalField(max_digits=13, decimal_places=0)
    total_donations = serializers.DecimalField(max_digits=13, decimal_places=0)
    total_transfer_payments = serializers.DecimalField(max_digits=13, decimal_places=1)
    total_pastor_tithe = serializers.DecimalField(max_digits=13, decimal_places=0)
    church_reports_in_progress = serializers.IntegerField()
    church_reports_submitted = serializers.IntegerField()
    church_reports_expired = serializers.IntegerField()

    class Meta:
        model = ChurchReport
        fields = ('id', 'total_peoples', 'total_new_peoples', 'total_repentance',
                  'total_tithe', 'total_donations', 'total_transfer_payments',
                  'total_pastor_tithe', 'church_reports_in_progress',
                  'church_reports_submitted', 'church_reports_expired')
        read_only_fields = ['__all__']


class ChurchReportsDashboardSerializer(serializers.ModelSerializer):
    church_reports_submitted = serializers.IntegerField()
    church_reports_in_progress = serializers.IntegerField()
    church_reports_expired = serializers.IntegerField()

    class Meta:
        model = ChurchReport
        fields = ('church_reports_submitted', 'church_reports_in_progress',
                  'church_reports_expired')
        read_only_fields = ['__all__']


class ChurchReportSummarySerializer(serializers.ModelSerializer):
    pastor = serializers.CharField(source='fullname', )
    master = UserNameWithLinkSerializer()
    reports_submitted = serializers.IntegerField()
    reports_in_progress = serializers.IntegerField(read_only=True)
    reports_expired = serializers.IntegerField(read_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'pastor', 'link', 'master',
                  'reports_submitted', 'reports_in_progress', 'reports_expired',)

        read_only_fields = ['__all__']


class MobileReportsDashboardSerializer(serializers.ModelSerializer):
    service = serializers.IntegerField()
    home_meetings = serializers.IntegerField()
    night = serializers.IntegerField()

    class Meta:
        model = Meeting
        fields = ('service', 'home_meetings', 'night')
