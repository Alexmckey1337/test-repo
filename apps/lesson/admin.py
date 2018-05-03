from django.contrib import admin

from apps.lesson.models import TextLesson, VideoLesson
from common.test_helpers.utils import get_real_user


class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'published_date', 'author', 'creator', 'access_level')
    list_display_links = ('title',)

    autocomplete_fields = ('author',)

    def save_model(self, request, obj, form, change):
        obj.creator = get_real_user(request)
        obj.save()


@admin.register(TextLesson)
class TextLessonAdmin(LessonAdmin):
    pass


@admin.register(VideoLesson)
class VideoLessonAdmin(LessonAdmin):
    pass
