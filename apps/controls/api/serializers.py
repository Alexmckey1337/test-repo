# -*- coding: utf-8
from rest_framework import serializers
from apps.account.models import CustomUser
from apps.account.api.serializers import HierarchyTitleSerializer
from django.contrib.auth.hashers import make_password, check_password
from django.utils.translation import ugettext_lazy as _
from apps.summit.models import Summit, SummitType
from apps.summit.api.serializers import SummitTypeSerializer
from apps.payment.api.serializers import CurrencySerializer
from apps.zmail.models import ZMailTemplate
from apps.account.api.serializers import HierarchyTitleSerializer
from django.contrib.auth import password_validation


class DatabaseAccessListSerializer(serializers.ModelSerializer):
    hierarchy = HierarchyTitleSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'link', 'fullname', 'hierarchy', 'is_staff', 'is_active',
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
            new_password = make_password(validated_data.pop('password'))
            instance.set_password(new_password)
            instance.save()

        return super(DatabaseAccessDetailSerializer, self).update(instance, validated_data)


class SummitPanelListSerializer(serializers.ModelSerializer):
    type = SummitTypeSerializer()

    class Meta:
        model = Summit
        fields = ('id', 'description', 'type', 'start_date', 'end_date', 'status')


class SummitPanelCreateUpdateSerializer(serializers.ModelSerializer):
    zmail_template = serializers.PrimaryKeyRelatedField(queryset=ZMailTemplate.objects.all())

    class Meta:
        model = Summit
        fields = ('id', 'start_date', 'end_date', 'type', 'description', 'code',
                  'full_cost', 'special_cost', 'currency', 'zmail_template',
                  'status')


class SummitPanelDetailSerializer(SummitPanelCreateUpdateSerializer):
    type = SummitTypeSerializer()
    currency = CurrencySerializer()

    class Meta(SummitPanelCreateUpdateSerializer.Meta):
        fields = SummitPanelCreateUpdateSerializer.Meta.fields


class SummitTypePanelSerializer(serializers.ModelSerializer):
    class Meta:
        model = SummitType
        fields = ('id', 'title', 'club_name', 'image')
