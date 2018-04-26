from rest_framework import serializers

from apps.account.models import CustomUser
from apps.lesson.models import TextLesson, VideoLesson


LESSON_LIST_FIELDS = (
    'id', 'slug', 'title', 'published_date', 'author',
    'count_view', 'is_liked',
    'total_views', 'total_likes',
    'unique_views', 'unique_likes',
)
LESSON_DETAIL_FIELDS = LESSON_LIST_FIELDS


class UserSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='fullname')

    class Meta:
        model = CustomUser
        fields = ('pk', 'title')


class BaseLessonListSerializer(serializers.ModelSerializer):
    count_view = serializers.IntegerField()
    total_views = serializers.IntegerField()
    total_likes = serializers.IntegerField()
    unique_views = serializers.IntegerField()
    unique_likes = serializers.IntegerField()
    is_liked = serializers.BooleanField()
    author = UserSerializer()


class TextLessonListSerializer(BaseLessonListSerializer):
    class Meta:
        model = TextLesson
        fields = LESSON_LIST_FIELDS


class VideoLessonListSerializer(BaseLessonListSerializer):
    class Meta:
        model = VideoLesson
        fields = LESSON_LIST_FIELDS


class BaseLessonDetailSerializer(serializers.ModelSerializer):
    count_view = serializers.IntegerField()
    total_views = serializers.IntegerField()
    total_likes = serializers.IntegerField()
    unique_views = serializers.IntegerField()
    unique_likes = serializers.IntegerField()
    is_liked = serializers.BooleanField()
    author = UserSerializer()


class TextLessonDetailSerializer(BaseLessonDetailSerializer):
    class Meta:
        model = TextLesson
        fields = LESSON_LIST_FIELDS + ('content', 'image')


class VideoLessonDetailSerializer(BaseLessonDetailSerializer):
    class Meta:
        model = VideoLesson
        fields = LESSON_LIST_FIELDS + ('url', 'description')
