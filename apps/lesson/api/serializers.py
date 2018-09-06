from rest_framework import serializers

from apps.account.models import CustomUser
from apps.lesson.models import TextLesson, VideoLesson, AbstractLesson, TextLessonImage, VideoFile
from common.fields import ReadOnlyChoiceWithKeyField

LESSON_LIST_FIELDS = (
    'id', 'slug', 'title', 'published_date', 'authors', 'access_level',
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


class TextLessonImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextLessonImage
        fields = ('display_order', 'url')


class BaseLessonListSerializer(serializers.ModelSerializer):
    count_view = serializers.IntegerField()
    total_views = serializers.IntegerField()
    total_likes = serializers.IntegerField()
    unique_views = serializers.IntegerField()
    unique_likes = serializers.IntegerField()
    is_liked = serializers.BooleanField()
    authors = UserSerializer(many=True)
    access_level = ReadOnlyChoiceWithKeyField(choices=AbstractLesson.ACCESS_LEVELS, read_only=True)


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
    authors = UserSerializer(many=True)
    access_level = ReadOnlyChoiceWithKeyField(choices=AbstractLesson.ACCESS_LEVELS, read_only=True)


class VideoFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoFile
        fields = ("title", "description", "width", "height", "duration", "file")


class TextLessonDetailSerializer(BaseLessonDetailSerializer):
    images = TextLessonImageSerializer(many=True)
    video_files = VideoFileSerializer(read_only=True, many=True)

    class Meta:
        model = TextLesson
        fields = LESSON_LIST_FIELDS + ('content', 'image', 'images', 'video_files')


class VideoLessonDetailSerializer(BaseLessonDetailSerializer):
    video_urls = serializers.JSONField(source='file.formats', read_only=True)

    class Meta:
        model = VideoLesson
        fields = LESSON_LIST_FIELDS + ('url', 'description', 'youtube_id', 'video_urls')


class EmptyTextLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextLesson
        fields = ()


class EmptyVideoLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoLesson
        fields = ()
