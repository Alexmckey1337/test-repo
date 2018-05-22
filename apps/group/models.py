from django.core.cache import cache
from django.db import models
from django.db import transaction
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext as _
from slugify import slugify

from apps.analytics.models import LogModel
from apps.event.models import Meeting, MeetingType, ChurchReport
from apps.group.managers import ChurchManager, HomeGroupManager
from apps.payment.models import get_default_currency
from common import date_utils


class CommonGroup(models.Model):
    title = models.CharField(_('Title'), max_length=50)
    opening_date = models.DateField(_('Opening Date'), default=date_utils.today)
    city = models.CharField(_('City'), max_length=50, blank=True)

    address = models.CharField(_('Address'), max_length=300, blank=True)
    latitude = models.FloatField(_('Latitude'), blank=True, null=True)
    longitude = models.FloatField(_('Longitude'), blank=True, null=True)

    phone_number = models.CharField(_('Phone Number'), max_length=20, blank=True)
    website = models.URLField(_('Web Site'), blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.get_title

    @property
    def link(self):
        return self.get_absolute_url()

    @property
    def get_title(self):
        if self.title:
            return self.title
        return '{} {}'.format(self.owner_name, self.city)


class Church(LogModel, CommonGroup):
    locality = models.ForeignKey('location.City', on_delete=models.SET_NULL, related_name='churches',
                                 null=True, blank=True, verbose_name=_('Locality'),
                                 help_text=_('City/village/etc'))
    department = models.ForeignKey('hierarchy.Department', related_name='churches',
                                   on_delete=models.PROTECT, verbose_name=_('Department'))
    pastor = models.ForeignKey('account.CustomUser', related_name='church',
                               on_delete=models.PROTECT, verbose_name=_('Pastor'))
    country = models.CharField(_('Country'), max_length=50, blank=True)
    is_open = models.BooleanField(default=False)
    report_currency = models.IntegerField(default=get_default_currency, verbose_name=_('Report Currency'))

    image = models.ImageField(_('Church Image'), upload_to='churches/', blank=True, null=True)

    region = models.CharField(_('Region'), max_length=50, blank=True, null=True)

    objects = ChurchManager()

    tracking_fields = (
        'title', 'opening_date', 'city', 'address', 'phone_number', 'website',
        'department', 'pastor', 'country',
        'is_open', 'report_currency', 'image', 'region', 'locality', 'latitude', 'longitude',
    )

    tracking_reverse_fields = ()

    def save(self, *args, **kwargs):
        is_create = self.pk is None
        super(Church, self).save(*args, **kwargs)

        if is_create:
            ChurchReport.objects.create(
                church=self,
                pastor=self.pastor,
                date=timezone.now().date(),
                currency_id=self.report_currency)

    class Meta:
        verbose_name = _('Church')
        verbose_name_plural = _('Churches')
        ordering = ['-opening_date', '-id']

    def get_absolute_url(self):
        return reverse('church_detail', args=(self.id,))

    @property
    def link(self):
        return self.get_absolute_url()

    @property
    def owner_name(self):
        return self.pastor.last_name

    @property
    def stable_count(self):
        from apps.account.models import CustomUser

        cache_key = f'church.{self.id}.stable_people.count'
        count = cache.get(cache_key)
        if count is None:
            count = CustomUser.objects.filter(Q(cchurch=self, is_stable=True) | Q(
                hhome_group__church=self, is_stable=True)).count()
            cache.set(cache_key, count, timeout=60 * 60)
        return count

    def del_count_stable_people_cache(self):
        cache.delete(f'church.{self.id}.stable_people.count')

    del_count_stable_people_cache.alters_data = True

    @property
    def count_hg_people(self):
        from apps.account.models import CustomUser

        cache_key = f'church.{self.id}.hg.people.count'
        count = cache.get(cache_key)
        if count is None:
            count = CustomUser.objects.filter(hhome_group__church=self).count()
            cache.set(cache_key, count, timeout=60 * 60)
        return count

    @property
    def count_people(self):
        from apps.account.models import CustomUser

        cache_key = f'church.{self.id}.people.count'
        count = cache.get(cache_key)
        if count is None:
            count = CustomUser.objects.filter(Q(cchurch=self) | Q(
                hhome_group__church=self)).count()
            cache.set(cache_key, count, timeout=60 * 60)
        return count

    def del_count_people_cache(self):
        cache.delete(f'church.{self.id}.people.count')

    del_count_people_cache.alters_data = True

    @property
    def count_home_groups(self):
        return self.home_group.count()


class Direction(models.Model):
    code = models.SlugField(_('Code'), max_length=60, blank=True, db_index=True, editable=False)
    title = models.CharField(_('Title'), max_length=40)

    def save(self, *args, **kwargs):
        if self.code:
            super().save(*args, **kwargs)
        else:
            self.code = self.generate_slug()
            super().save(*args, **kwargs)
            self.ensure_slug_uniqueness()

    def generate_slug(self):
        return slugify(self.title)

    def ensure_slug_uniqueness(self):
        unique_code = self.code
        direction = self.__class__.objects.exclude(pk=self.pk)
        next_num = 2
        while direction.filter(code=unique_code).exists():
            unique_code = '{code}_{end}'.format(code=self.code, end=next_num)
            next_num += 1

        if unique_code != self.code:
            self.code = unique_code
            self.save()


class HomeGroup(LogModel, CommonGroup):
    locality = models.ForeignKey('location.City', on_delete=models.SET_NULL, related_name='home_groups',
                                 null=True, blank=True, verbose_name=_('Locality'),
                                 help_text=_('City/village/etc'))
    leader = models.ForeignKey('account.CustomUser', related_name='home_group',
                               on_delete=models.PROTECT, verbose_name=_('Leader'))
    church = models.ForeignKey('Church', related_name='home_group',
                               on_delete=models.PROTECT, verbose_name=_('Church'))
    active = models.BooleanField(default=True)

    image = models.ImageField(_('Home Group Image'), upload_to='home_groups/', blank=True, null=True)

    UA, RU, EN, DE = 'ua', 'ru', 'en', 'de'
    LANGUAGES = (
        (UA, _('Ukraine')),
        (RU, _('Russian')),
        (EN, _('English')),
        (DE, _('Germany')),
    )
    language = models.CharField(_('Language'), choices=LANGUAGES, blank=True, max_length=10)

    directions = models.ManyToManyField(Direction, related_name='home_groups')

    objects = HomeGroupManager()

    tracking_fields = (
        'title', 'opening_date', 'city', 'address', 'phone_number', 'website',
        'leader', 'church', 'active', 'image', 'locality', 'latitude', 'longitude',
        'language',
    )

    def save(self, *args, **kwargs):
        is_create = self.pk is None
        super(HomeGroup, self).save(*args, **kwargs)

        if is_create:
            meeting_types = MeetingType.objects.exclude(code='night')
            with transaction.atomic():
                for meeting_type in meeting_types:
                    Meeting.objects.create(home_group=self,
                                           owner=self.leader,
                                           date=timezone.now().date(),
                                           type=meeting_type)

        if self.leader and self.pk:
            Meeting.objects.filter(home_group=self, status=Meeting.IN_PROGRESS).update(owner=self.leader)

    class Meta:
        verbose_name = _('Home Group')
        verbose_name_plural = _('Home Groups')
        ordering = ['-opening_date', '-id']

    def get_absolute_url(self):
        return reverse('home_group_detail', args=(self.id,))

    @property
    def owner_name(self):
        return self.leader.last_name
