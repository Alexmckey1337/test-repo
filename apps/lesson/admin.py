from django.contrib import admin

from apps.lesson.models import TextLesson, VideoLesson


class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'published_date', 'author', 'creator')
    list_display_links = ('title',)

    readonly_fields = ('author',)

    def save_model(self, request, obj, form, change):
        obj.creator = request.user
        obj.save()


@admin.register(TextLesson)
class TextLessonAdmin(LessonAdmin):
    pass


@admin.register(VideoLesson)
class VideoLessonAdmin(LessonAdmin):
    pass
