# -*- coding: utf-8
from __future__ import unicode_literals

from rest_framework import serializers

from .models import Department, Hierarchy


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ('url', 'id', 'title',)


class HierarchySerializer(serializers.ModelSerializer):
    class Meta:
        model = Hierarchy
        fields = ('id', 'title', 'level',)
