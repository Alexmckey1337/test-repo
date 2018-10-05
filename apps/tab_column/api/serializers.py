from rest_framework import serializers
from apps.tab_column.models import Table, Column


class ColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Column
        fields = ("id", "title", "ordering_title","active", "editable")


class TableSerializer(serializers.ModelSerializer):
    columns = ColumnSerializer(read_only=True, many=True)

    class Meta:
        model = Table
        fields = '__all__'


