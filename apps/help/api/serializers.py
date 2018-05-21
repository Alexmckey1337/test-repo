from rest_framework.serializers import ModelSerializer
from apps.help.models import Manual


class ManualSerializer(ModelSerializer):
    class Meta:
        model = Manual
        fields = ('title', 'content', 'category')
