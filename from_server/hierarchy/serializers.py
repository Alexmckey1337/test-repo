from models import Department, Hierarchy
from rest_framework import serializers


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ('url', 'id', 'title',)


class HierarchySerializer(serializers.ModelSerializer):
    class Meta:
        model = Hierarchy
        fields = ('url', 'id', 'title', 'level', )
