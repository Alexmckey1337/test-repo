from rest_framework import serializers
from models import Partnership, Deal


class PartnershipSerializer(serializers.HyperlinkedModelSerializer):
    date = serializers.DateField(format=None, input_formats=None)
    responsible = serializers.StringRelatedField()

    class Meta:
        model = Partnership
        fields = ('url', 'id', 'user', 'fullname', 'responsible', 'value', 'date',
                  'is_responsible', 'deals', 'deals_count', 'done_deals_count', 'undone_deals_count',
                  'expired_deals_count', 'result_value', 'fields', 'deal_fields', 'common', )


class DealSerializer(serializers.HyperlinkedModelSerializer):
    date = serializers.DateField(format=None, input_formats=None)

    class Meta:
        model = Deal
        fields = ('url', 'id', 'partnership', 'date', 'value', 'done', 'expired', 'description', 'fields', )
