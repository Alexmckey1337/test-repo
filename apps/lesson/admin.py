from django.contrib import admin
from video_encoding.admin import FormatInline as BaseFormatInline

from apps.lesson.models import TextLesson, VideoLesson, VideoFile, TextLessonImage
from common.test_helpers.utils import get_real_user


class FormatInline(BaseFormatInline):
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return True


class ImageInline(admin.StackedInline):
    model = TextLessonImage
    fields = ('display_order', 'url')
    extra = 1


class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'published_date', 'creator', 'access_level')
    list_display_links = ('title',)

    autocomplete_fields = ('authors',)

    def save_model(self, request, obj, form, change):
        obj.creator = get_real_user(request)
        obj.save()


@admin.register(TextLesson)
class TextLessonAdmin(LessonAdmin):
    list_display = ('title', 'status', 'published_date', 'creator', 'access_level', 'image')
    readonly_fields = ('image',)
    inlines = (ImageInline,)


@admin.register(VideoLesson)
class VideoLessonAdmin(LessonAdmin):
    list_display = ('title', 'status', 'published_date', 'creator', 'access_level')


@admin.register(VideoFile)
class VideoFileAdmin(admin.ModelAdmin):
    inlines = (FormatInline,)

    list_display = ('title', 'width', 'height', 'duration')
    readonly_fields = ('width', 'height', 'duration')
