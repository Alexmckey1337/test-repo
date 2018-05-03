from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from slugify import slugify
from tinymce.models import HTMLField

from apps.lesson.managers import PublishedLessonManager, LessonManager
from apps.lesson.validators import YoutubeURLField


class AbstractLesson(models.Model):
    title = models.CharField(_('Title'), max_length=30)
    slug = models.SlugField(_('URL'), max_length=255, editable=False)
    author = models.ForeignKey(
        'account.CustomUser', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='author_%(class)ss',
    )
    creator = models.ForeignKey(
        'account.CustomUser', on_delete=models.CASCADE, editable=False,
        related_name='creator_%(class)ss',
    )

    created_at = models.DateTimeField(_('Created Date'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated Date'), auto_now=True)
    published_date = models.DateTimeField(_('Published Date'), default=timezone.now)

    DRAFT, PUBLISHED = 'draft', 'published'
    STATUS = (
        (DRAFT, _('Draft')),
        (PUBLISHED, _('Published')),
    )
    status = models.CharField(_('Status'), max_length=9, choices=STATUS, default=DRAFT)

    objects = LessonManager()
    published = PublishedLessonManager()

    class Meta:
        abstract = True
        app_label = 'lesson'
        ordering = ['-published_date']

    def save(self, *args, **kwargs):
        if self.slug:
            super().save(*args, **kwargs)
        else:
            self.slug = self.generate_slug()
            super().save(*args, **kwargs)
            self.ensure_slug_uniqueness()

    def generate_slug(self):
        return slugify(self.title)

    def ensure_slug_uniqueness(self):
        unique_slug = self.slug
        lesson = self.__class__.objects.exclude(pk=self.pk)
        next_num = 2
        while lesson.filter(slug=unique_slug).exists():
            unique_slug = '{slug}_{end}'.format(slug=self.slug, end=next_num)
            next_num += 1

        if unique_slug != self.slug:
            self.slug = unique_slug
            self.save()


class TextLesson(AbstractLesson):
    content = HTMLField(verbose_name=_('Content'))
    image = models.ImageField(_('Image'), upload_to='lessons', null=True, blank=True)

    views = models.ManyToManyField(
        'account.CustomUser', through='TextLessonView', through_fields=('lesson', 'user'),
        related_name='view_text_lessons',
        verbose_name=_('Views')
    )
    likes = models.ManyToManyField(
        'account.CustomUser', through='TextLessonLike', through_fields=('lesson', 'user'),
        related_name='like_text_lessons',
        verbose_name=_('Views')
    )

    class Meta:
        app_label = 'lesson'
        db_table = 'lesson_text'
        ordering = ['-published_date']
        verbose_name = 'Text lesson'
        verbose_name_plural = 'Text lessons'


class VideoLesson(AbstractLesson):
    description = HTMLField(_('Description'), blank=True)
    url = YoutubeURLField(_('youtube url'), max_length=255)

    views = models.ManyToManyField(
        'account.CustomUser', through='VideoLessonView', through_fields=('lesson', 'user'),
        related_name='view_video_lessons',
        verbose_name=_('Views')
    )
    likes = models.ManyToManyField(
        'account.CustomUser', through='VideoLessonLike', through_fields=('lesson', 'user'),
        related_name='like_video_lessons',
        verbose_name=_('Views')
    )

    class Meta:
        app_label = 'lesson'
        db_table = 'lesson_video'
        ordering = ['-published_date']
        verbose_name = 'Video lesson'
        verbose_name_plural = 'Video lessons'

    @property
    def youtube_id(self):
        return self.url.split("/")[-1].split("?", 1)[0]


class AbstractTextLessonUserRelation(models.Model):
    lesson = models.ForeignKey('TextLesson', on_delete=models.CASCADE, related_name='+')
    user = models.ForeignKey('account.CustomUser', on_delete=models.CASCADE, related_name='+')

    created_at = models.DateTimeField(_('Date'), auto_now_add=True)

    class Meta:
        abstract = True


class AbstractVideoLessonUserRelation(models.Model):
    lesson = models.ForeignKey('VideoLesson', on_delete=models.CASCADE, related_name='+')
    user = models.ForeignKey('account.CustomUser', on_delete=models.CASCADE, related_name='+')

    created_at = models.DateTimeField(_('Date'), auto_now_add=True)

    class Meta:
        abstract = True


class TextLessonView(AbstractTextLessonUserRelation):
    class Meta:
        app_label = 'lesson'
        db_table = 'lesson_text_view'


class TextLessonLike(AbstractTextLessonUserRelation):
    class Meta:
        app_label = 'lesson'
        db_table = 'lesson_text_like'


class VideoLessonView(AbstractVideoLessonUserRelation):
    class Meta:
        app_label = 'lesson'
        db_table = 'lesson_video_view'


class VideoLessonLike(AbstractVideoLessonUserRelation):
    class Meta:
        app_label = 'lesson'
        db_table = 'lesson_video_like'
