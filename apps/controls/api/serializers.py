from django.contrib.auth import password_validation
from rest_framework import serializers

from apps.account.api.serializers import HierarchyTitleSerializer
from apps.account.models import CustomUser
from apps.analytics.models import LogRecord
from apps.payment.api.serializers import CurrencySerializer
from apps.summit.api.serializers import SummitTypeSerializer
from apps.summit.models import Summit, SummitType
from apps.zmail.models import ZMailTemplate


class DatabaseAccessListSerializer(serializers.ModelSerializer):
    hierarchy = HierarchyTitleSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'link', 'fullname', 'hierarchy', 'is_staff', 'is_active', 'is_proposal_manager',
                  'can_login', 'has_usable_password')


class DatabaseAccessDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'password')

    def validate_password(self, value):
        password_validation.validate_password(password=value, user=CustomUser)
        return value

    def update(self, instance, validated_data):
        if validated_data.get('password'):
            new_password = validated_data.pop('password')
            instance.set_password(new_password)
            instance.save()
            return instance


class SummitPanelListSerializer(serializers.ModelSerializer):
    type = SummitTypeSerializer()

    class Meta:
        model = Summit
        fields = ('id', 'description', 'type', 'start_date', 'end_date', 'status')


class SummitPanelCreateUpdateSerializer(serializers.ModelSerializer):
    zmail_template = serializers.PrimaryKeyRelatedField(queryset=ZMailTemplate.objects.all(),
                                                        required=False, allow_null=True)

    class Meta:
        model = Summit
        fields = ('id', 'start_date', 'end_date', 'type', 'description', 'code',
                  'full_cost', 'special_cost', 'currency', 'zmail_template',
                  'status')


class SummitPanelDetailSerializer(SummitPanelCreateUpdateSerializer):
    type = SummitTypeSerializer(required=True)
    currency = CurrencySerializer()

    class Meta(SummitPanelCreateUpdateSerializer.Meta):
        fields = SummitPanelCreateUpdateSerializer.Meta.fields


class SummitTypePanelSerializer(serializers.ModelSerializer):
    class Meta:
        model = SummitType
        fields = ('id', 'title', 'club_name', 'image')


class LogPanelSerializer(serializers.ModelSerializer):
    object = serializers.CharField(source='content_type.model', read_only=True)
    action_flag = serializers.CharField(source='get_action_flag_display', read_only=True)
    author = serializers.CharField(source='user.fullname', read_only=True)

    class Meta:
        model = LogRecord
        fields = ('id', 'object', 'action_flag', 'author', 'change_data')
