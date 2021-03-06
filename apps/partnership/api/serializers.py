from rest_framework import serializers

from apps.account.api.serializers import PartnerUserSerializer
from apps.group.api.serializers import BaseChurchListSerializer
from apps.partnership.models import Partnership, Deal, PartnerGroup, PartnerRole, ChurchPartner, ChurchDeal
from apps.partnership.models import TelegramUser
from apps.payment.api.serializers import CurrencySerializer
from apps.payment.models import Payment
from common.fields import DecimalWithCurrencyField

BASE_PARTNER_FIELDS = (
    'id', 'responsible', 'value', 'date', 'need_text', 'currency', 'is_active', 'group', 'title')
BASE_CHURCH_PARTNER_FIELDS = (
    'id', 'responsible', 'value', 'date', 'need_text', 'currency', 'is_active', 'group', 'title')


class PartnerGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerGroup
        fields = ('id', 'title', 'type')
        extra_kwargs = {'type': {'required': True}}


class PartnershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partnership
        fields = BASE_PARTNER_FIELDS


class PartnershipUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partnership
        fields = BASE_PARTNER_FIELDS
        extra_kwargs = {
            'group': {'required': True}
        }

    def update(self, instance, validated_data):
        responsible = validated_data.get('responsible')
        if responsible:
            Deal.objects.filter(partnership=instance, done=False).update(responsible=responsible)

        if validated_data.get('is_active') is False and instance.is_active is True:
            if not Partnership.objects.filter(user_id=instance.user.id,
                                              is_active=True).exclude(id=instance.id).exists():
                TelegramUser.objects.filter(user=instance.user).update(is_active=False, synced=False)

        return super(PartnershipUpdateSerializer, self).update(instance, validated_data)


class PartnershipCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partnership
        fields = ('user',) + BASE_PARTNER_FIELDS
        extra_kwargs = {
            'group': {'required': True}
        }


class PartnershipTableSerializer(serializers.ModelSerializer):
    user = PartnerUserSerializer()
    date = serializers.DateField(format=None, input_formats=None)
    responsible = serializers.StringRelatedField()
    group = serializers.StringRelatedField()
    value = DecimalWithCurrencyField(max_digits=12, decimal_places=0,
                                     read_only=True, currency_field='currency')
    is_vip = serializers.BooleanField()
    is_ruby = serializers.BooleanField()
    is_gold = serializers.BooleanField()
    is_stable_newbie = serializers.BooleanField(read_only=True)

    class Meta:
        model = Partnership
        fields = ('id',
                  'user',
                  'is_vip', 'is_ruby', 'is_gold',
                  'fullname', 'is_stable_newbie') + BASE_PARTNER_FIELDS


class ChurchPartnerTableSerializer(serializers.ModelSerializer):
    church = BaseChurchListSerializer()
    date = serializers.DateField(format=None, input_formats=None)
    responsible = serializers.StringRelatedField()
    group = serializers.StringRelatedField()
    value = DecimalWithCurrencyField(max_digits=12, decimal_places=0,
                                     read_only=True, currency_field='currency')
    fullname = serializers.CharField(source='church.title')

    class Meta:
        model = Partnership
        fields = ('id', 'church', 'fullname',) + BASE_CHURCH_PARTNER_FIELDS


class ChurchPartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChurchPartner
        fields = BASE_CHURCH_PARTNER_FIELDS


class ChurchPartnerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChurchPartner
        fields = ('church',) + BASE_CHURCH_PARTNER_FIELDS


class ChurchPartnerUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChurchPartner
        fields = BASE_CHURCH_PARTNER_FIELDS

    def update(self, instance, validated_data):
        responsible = validated_data.get('responsible')
        if responsible:
            ChurchDeal.objects.filter(partnership=instance, done=False).update(responsible=responsible)

        return super().update(instance, validated_data)


class DealCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deal
        fields = ('partnership', 'date', 'date_created',
                  'value', 'description', 'type',
                  )


class DealUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deal
        fields = ('done', 'description', 'type', 'value', 'date_created')

    def update(self, instance, validated_data):
        value = validated_data.get('value')
        if value:
            try:
                if instance.value < validated_data.get('value'):
                    instance.done = False
            except Exception:
                raise serializers.ValidationError({'message': '{value} must be Integer or Decimal'})
        return super().update(instance, validated_data)


class DealSerializer(serializers.ModelSerializer):
    date = serializers.DateField(format=None, input_formats=None, read_only=True)
    date_created = serializers.DateField(input_formats=None)
    partnership = serializers.PrimaryKeyRelatedField(queryset=Partnership.objects.all())
    full_name = serializers.CharField(read_only=True)
    value = serializers.CharField(read_only=True, source='value_str')
    responsible_name = serializers.CharField(read_only=True)
    total_sum = DecimalWithCurrencyField(max_digits=12, decimal_places=0,
                                         read_only=True, currency_field='currency')
    currency = CurrencySerializer()
    payment_status = serializers.IntegerField()
    group = serializers.CharField(source='partnership.group.title', read_only=True)

    class Meta:
        model = Deal
        fields = ('id', 'partnership', 'date', 'date_created',
                  'value', 'done', 'expired', 'description',
                  'full_name', 'responsible_name', 'partner_link',
                  'total_sum', 'currency', 'payment_status', 'type', 'group'
                  )


class AllDealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deal
        fields = ('id', 'value', 'date', 'date_created', 'done', 'expired', 'description')


class ChurchDealSerializer(serializers.ModelSerializer):
    date = serializers.DateField(format=None, input_formats=None, read_only=True)
    date_created = serializers.DateField(input_formats=None)
    partnership = serializers.PrimaryKeyRelatedField(queryset=ChurchPartner.objects.all())
    full_name = serializers.CharField(read_only=True)
    value = serializers.CharField(read_only=True, source='value_str')
    responsible_name = serializers.CharField(read_only=True)
    total_sum = DecimalWithCurrencyField(max_digits=12, decimal_places=0,
                                         read_only=True, currency_field='currency')
    currency = CurrencySerializer()
    payment_status = serializers.IntegerField()

    class Meta:
        model = ChurchDeal
        fields = ('id', 'partnership', 'date', 'date_created',
                  'value', 'done', 'expired', 'description',
                  'full_name', 'responsible_name', 'partner_link',
                  'total_sum', 'currency', 'payment_status', 'type',
                  )


class ChurchDealCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChurchDeal
        fields = ('partnership', 'date', 'date_created',
                  'value', 'description', 'type',
                  )


class ChurchDealUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChurchDeal
        fields = ('done', 'description', 'type', 'value', 'date_created')

    def update(self, instance, validated_data):
        value = validated_data.get('value')
        if value:
            try:
                if instance.value < validated_data.get('value'):
                    instance.done = False
            except Exception:
                raise serializers.ValidationError({'message': '{value} must be Integer or Decimal'})
        return super().update(instance, validated_data)


class PartnerRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerRole
        fields = ('level', 'plan')


class CreatePartnerRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerRole
        fields = ('user', 'level', 'plan')


class DealDuplicateSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Deal
        fields = ('id', 'full_name', 'value', 'date_created')


class ChurchDealDuplicateSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = ChurchDeal
        fields = ('id', 'full_name', 'value', 'date_created')


class LastDealSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source='get_type_display')
    manager = serializers.CharField(source='responsible_name')
    total_payments = serializers.FloatField()

    class Meta:
        model = Deal
        fields = ('date_created', 'manager', 'type', 'value', 'total_payments')


class LastDealPaymentSerializer(serializers.ModelSerializer):
    deal_date = serializers.DateField(format="%m.%Y")
    manager = serializers.CharField()

    class Meta:
        model = Payment
        fields = ('created_at', 'sent_date', 'deal_date', 'manager', 'sum', 'effective_sum')


class LastChurchDealSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source='get_type_display')
    manager = serializers.CharField(source='responsible_name')
    total_payments = serializers.FloatField()

    class Meta:
        model = ChurchDeal
        fields = ('date_created', 'manager', 'type', 'value', 'total_payments')


class LastChurchDealPaymentSerializer(serializers.ModelSerializer):
    deal_date = serializers.DateField(format="%m.%Y")
    manager = serializers.CharField()

    class Meta:
        model = Payment
        fields = ('created_at', 'sent_date', 'deal_date', 'manager', 'sum', 'effective_sum')
