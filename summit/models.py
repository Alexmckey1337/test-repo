# -*- coding: utf-8
from __future__ import unicode_literals

from datetime import datetime
from decimal import Decimal

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.validators import int_list_validator
from django.db import models
from django.db.models import Sum
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from analytics.decorators import log_change_payment
from account.abstract_models import CustomUserAbstract
from payment.models import get_default_currency, AbstractPaymentPurpose
from summit.managers import ProfileManager, SummitManager
from summit.regcode import encode_reg_code


@python_2_unicode_compatible
class SummitType(models.Model):
    """
    Type of the summit.
    """
    #: Title of the summit
    title = models.CharField(max_length=100, verbose_name='Название саммита')
    #: Club name of the summit.
    club_name = models.CharField(_('Club name'), max_length=30, blank=True)
    #: Summit image
    image = models.ImageField(upload_to='summit_type/images/', blank=True)
    #: Code of the summit type. Is an identifier for a summit_type.
    #: By code we can find the summit_type.
    code = models.SlugField(_('Code'), max_length=255, blank=True)

    class Meta:
        verbose_name = _('Summit Type')
        verbose_name_plural = _('Summits Types')

    def __str__(self):
        return self.title

    @property
    def image_url(self):
        if self.image:
            return self.image.url
        else:
            return ''


@python_2_unicode_compatible
class Summit(models.Model):
    #: Start date of the summit
    start_date = models.DateField()
    #: End date of the summit
    end_date = models.DateField()
    #: Summit type
    type = models.ForeignKey('SummitType', related_name='summits', blank=True, null=True)
    #: Display name
    description = models.CharField(max_length=255, verbose_name='Описание',
                                   blank=True, null=True)
    #: Code of the summit. Is an identifier for a summit.
    #: By code we can find the summit.
    code = models.SlugField(_('Code'), max_length=255, blank=True)
    #: Full cost of the summit.
    full_cost = models.DecimalField(_('Full cost'), max_digits=12, decimal_places=0,
                                    default=Decimal('0'))
    #: Special cost of the summit. If user is member of this summit type then he
    #: has discount for this summit.
    special_cost = models.DecimalField(_('Special cost'), max_digits=12, decimal_places=0,
                                       blank=True, null=True)
    #: Currency of full_cost and special_cost
    currency = models.ForeignKey('payment.Currency', on_delete=models.PROTECT, verbose_name=_('Currency'),
                                 default=get_default_currency, null=True)
    #: Template for sending tickets. This template using in dbmail.
    mail_template = models.ForeignKey('dbmail.MailTemplate', related_name='summits',
                                      verbose_name=_('Mail template'),
                                      null=True, blank=True)
    OPEN, CLOSE = 'open', 'close'
    STATUSES = (
        (OPEN, _('Open')),
        (CLOSE, _('Close')),
    )
    status = models.CharField(_('Status'), choices=STATUSES, default=OPEN, max_length=20)

    objects = SummitManager()

    class Meta:
        ordering = ('type',)
        verbose_name = _('Summit')
        verbose_name_plural = _('Summits')

    def __str__(self):
        return '%s %s' % (self.type.title, self.start_date)

    def get_absolute_url(self):
        return reverse('summit:detail', kwargs={'pk': self.id})

    def clean(self):
        """
        Validate a summit costs.

        If special cost is exist then the special cost must be less then full cost.
        """
        if self.special_cost is not None and self.full_cost <= self.special_cost:
            raise ValidationError(_('Special cost must be less then full cost'))

    @property
    def consultants(self):
        """
        Return list of the summit consultants

        :return: QuerySet
        """
        return self.ankets.filter(role__gte=SummitAnket.CONSULTANT)

    @property
    def title(self):
        return self.type.title

    @property
    def club_name(self):
        return self.type.club_name


def validate_master_path(value):
    return int_list_validator(sep='.', message=_('Enter only digits separated by dots.'))


class ProfileAbstract(models.Model):
    """ Cloned the user when create/update profile """

    first_name = models.CharField(_('Fisrt name'), max_length=255, blank=True, editable=False, db_index=True)
    last_name = models.CharField(_('Last name'), max_length=255, blank=True, editable=False, db_index=True)

    pastor = models.CharField(_('Name of pastor'), max_length=255, blank=True, editable=False)
    bishop = models.CharField(_('Name of bishop'), max_length=255, blank=True, editable=False)
    sotnik = models.CharField(_('Name of sotnik'), max_length=255, blank=True, editable=False)

    pastor_fk = models.ForeignKey('account.CustomUser', on_delete=models.SET_NULL,
                                  null=True, blank=True, editable=False, related_name='pastor_users',
                                  verbose_name=_('Pastor'))
    bishop_fk = models.ForeignKey('account.CustomUser', on_delete=models.SET_NULL,
                                  null=True, blank=True, editable=False, related_name='bishop_users',
                                  verbose_name=_('Bishop'))
    sotnik_fk = models.ForeignKey('account.CustomUser', on_delete=models.SET_NULL,
                                  null=True, blank=True, editable=False, related_name='sotnik_users',
                                  verbose_name=_('Sotnik'))

    #: Date created
    date = models.DateField(_('Date created'), auto_now_add=True, editable=False)
    #: User who added a profile
    creator = models.ForeignKey('account.CustomUser', related_name='added_profiles', editable=False,
                                null=True, blank=True, verbose_name=_('Creator'), on_delete=models.SET_NULL)

    divisions = models.ManyToManyField('status.Division', verbose_name=_('Divisions'), editable=False)
    divisions_title = models.CharField(_('Divisions title'), max_length=255, blank=True, editable=False)

    departments = models.ManyToManyField('hierarchy.Department',
                                         verbose_name=_('Departments'), editable=False)
    department = models.CharField(_('Titles of departments'), max_length=255, blank=True, editable=False, db_index=True)

    hierarchy = models.ForeignKey('hierarchy.Hierarchy', null=True, blank=True,
                                  on_delete=models.SET_NULL, verbose_name=_('Hierarchy'), editable=False, db_index=True)
    hierarchy_title = models.CharField(_('Title of hierarchy'), max_length=255, blank=True, editable=False)
    master = models.ForeignKey('account.CustomUser', null=True, blank=True, verbose_name=_('Master'),
                               on_delete=models.PROTECT, editable=False, db_index=True)
    master_path = ArrayField(
        models.PositiveIntegerField(_('User id')),
        verbose_name=_('Master path'),
        default=[], editable=False
    )
    responsible = models.CharField(_('Name of master'), max_length=255, blank=True, editable=False)

    class Meta:
        abstract = True


@python_2_unicode_compatible
class SummitAnket(CustomUserAbstract, ProfileAbstract, AbstractPaymentPurpose):
    user = models.ForeignKey('account.CustomUser', related_name='summit_profiles')
    summit = models.ForeignKey('Summit', related_name='ankets', verbose_name='Саммит',
                               blank=True, null=True, db_index=True)

    #: The amount paid for the summit
    value = models.DecimalField(_('Paid amount'), max_digits=12, decimal_places=0,
                                default=Decimal('0'), editable=False)
    code = models.CharField(max_length=8, blank=True, db_index=True)

    ticket = models.FileField(_('Ticket'), upload_to='tickets', null=True, blank=True)

    VISITOR = settings.SUMMIT_ANKET_ROLES['visitor']
    CONSULTANT = settings.SUMMIT_ANKET_ROLES['consultant']
    SUPERVISOR = settings.SUMMIT_ANKET_ROLES['supervisor']

    ROLES = (
        (VISITOR, _('Visitor')),
        (CONSULTANT, _('Consultant')),
        (SUPERVISOR, _('Supervisor')),
    )
    role = models.PositiveSmallIntegerField(_('Summit Role'), choices=ROLES, default=VISITOR, db_index=True)

    summit_consultants = models.ManyToManyField(
        'summit.Summit', related_name='consultant_ankets',
        through='summit.SummitUserConsultant', through_fields=('user', 'summit'))

    #: Payments of the current anket
    payments = GenericRelation('payment.Payment', related_query_name='summit_profiles')

    # Editable fields
    description = models.CharField(max_length=255, blank=True)

    visited = models.BooleanField(default=False)

    NONE, DOWNLOADED, PRINTED, GIVEN = 'none', 'download', 'print', 'given'
    TICKET_STATUSES = (
        (NONE, _('Without ticket.')),
        (DOWNLOADED, _('Ticket is created.')),
        (PRINTED, _('Ticket is printed')),
        (GIVEN, _('Ticket is given')),
    )
    ticket_status = models.CharField(_('Ticket status'), choices=TICKET_STATUSES, default=NONE, max_length=20)

    objects = ProfileManager()

    class Meta:
        ordering = ('summit__type', '-summit__start_date')
        unique_together = (('user', 'summit'),)

    def __str__(self):
        return '%s %s %s' % (self.user.fullname, self.summit.type.title, self.summit.start_date)

    def get_absolute_url(self):
        return reverse('summit:profile-detail', kwargs={'pk': self.id})

    def link(self):
        return self.user.get_absolute_url()

    def save(self, *args, **kwargs):
        update = kwargs.get('update_archive_fields', True)
        if self.summit.status == Summit.OPEN and update:
            self.update_archive_fields()
            super(SummitAnket, self).save(*args, **kwargs)
            self.divisions.set(self.user.divisions.all())
            self.departments.set(self.user.departments.all())
        else:
            super(SummitAnket, self).save(*args, **kwargs)

    def update_archive_fields(self):
        self.first_name = self.user.first_name
        self.last_name = self.user.last_name
        self.middle_name = self.user.middle_name
        self.search_name = self.user.search_name
        self.city = self.user.city
        self.country = self.user.country
        self.spiritual_level = self.user.spiritual_level

        pastor = self.user.get_pastor()
        self.pastor = pastor.fullname if pastor else ''
        self.pastor_fk = pastor

        bishop = self.user.get_bishop()
        self.bishop = bishop.fullname if bishop else ''
        self.bishop_fk = bishop

        sotnik = self.user.get_sotnik()
        self.sotnik = sotnik.fullname if sotnik else ''
        self.sotnik_fk = sotnik

        master = self.user.master
        self.responsible = master.fullname if master else ''
        self.master = master
        master_path = list(self.user.get_ancestors().values_list('pk', flat=True))
        self.master_path = master_path

        hierarchy = self.user.hierarchy
        self.hierarchy = hierarchy
        self.hierarchy_title = hierarchy.title if hierarchy else ''

        self.divisions_title = ', '.join(self.user.divisions.values_list('title', flat=True))
        self.department = ', '.join(self.user.departments.values_list('title', flat=True))

    update_archive_fields.alter_data = True

    @property
    def fullname(self):
        return ' '.join(filter(lambda n: n.strip(), [self.last_name, self.first_name, self.middle_name]))

    @property
    def name(self):
        return self.fullname

    @property
    def phone_number(self):
        return self.user.phone_number

    @property
    def region(self):
        return self.user.region

    @property
    def total_payed(self):
        return self.payments.aggregate(value=Sum('effective_sum'))['value']

    @property
    def currency(self):
        return self.summit.currency

    def calculate_value(self):
        payments = self.payments.filter(currency_rate=self.currency)
        # for payment in payments:
        #     payment.update_effective_sum(save=True)
        if self.payments.exclude(currency_rate=self.currency).exists():
            # TODO logging
            pass

        # payments.refresh_from_db()
        if payments.exists():
            value = payments.aggregate(value=Sum('effective_sum'))['value']
        else:
            value = 0
        return value

    @log_change_payment(['value'])
    def update_after_cancel_payment(self, editor, payment):
        self.update_value()

    update_after_cancel_payment.alters_data = True

    def update_value(self):
        self.value = self.calculate_value()
        self.save()

    update_value.alters_data = True

    @property
    def is_member(self):
        """
        Verification that the user is member of summit type.

        :return: boolean
        """
        summit_type = self.summit.type
        return summit_type.summits.filter(ankets__visited=True, ankets__user=self.user).exists()

    @property
    def is_full_paid(self):
        """
        Verification that the user paid for the summit.

        :return: boolean
        """
        if self.is_member and self.summit.special_cost is not None:
            return self.summit.special_cost <= self.total_payed
        else:
            return self.summit.full_cost <= self.total_payed

    @property
    def reg_code(self):
        return encode_reg_code(self.id)

    @property
    def get_passes_count(self):
        return self.passes_count.filter(datetime__date=datetime.now().date()).count()


@python_2_unicode_compatible
class SummitTicket(models.Model):
    title = models.CharField(_('Title'), max_length=255, blank=True)
    summit = models.ForeignKey('Summit', on_delete=models.CASCADE, related_name='tickets', verbose_name=_('Summit'))
    attachment = models.FileField(_('Ticket'), upload_to='tickets', null=True, blank=True)

    owner = models.ForeignKey('account.CustomUser', on_delete=models.SET_NULL, related_name='created_tickets',
                              verbose_name=_('User'), null=True)
    created_at = models.DateTimeField(_('Date created'), auto_now_add=True)

    IN_PROGRESS, COMPLETE, ERROR = 'progress', 'complete', 'error'
    STATUSES = (
        (IN_PROGRESS, _('In progress')),
        (COMPLETE, _('Complete')),
        (ERROR, _('Error')),
    )
    status = models.CharField(_('Status'), choices=STATUSES, default=IN_PROGRESS, max_length=20)

    users = models.ManyToManyField('summit.SummitAnket', related_name='tickets',
                                   verbose_name=_('Users'))
    is_printed = models.BooleanField(_('Is printed'), default=False)

    class Meta:
        ordering = ('summit', 'title')
        verbose_name = _('Summit ticket')
        verbose_name_plural = _('List of summit tickets')

    def __str__(self):
        return '{}: {} ({})'.format(str(self.summit), self.title, self.status)

    def get_absolute_url(self):
        return reverse("summit:ticket-detail", kwargs={"pk": self.id})


@python_2_unicode_compatible
class AnketEmail(models.Model):
    anket = models.ForeignKey('summit.SummitAnket', on_delete=models.CASCADE, related_name='emails',
                              verbose_name=_('Anket'))
    #: Email of recipient user
    recipient = models.CharField(_('Email'), max_length=255)

    subject = models.CharField(_('Subject'), max_length=255, blank=True)
    text = models.TextField(_('Text'), blank=True)
    html = models.TextField(_('HTML text'), blank=True)
    error_message = models.TextField(_('Error message'), blank=True)
    is_success = models.BooleanField(_('Is success'), default=True)
    attach = models.FileField(_('Attach'), upload_to='tickets', null=True, blank=True)

    created_at = models.DateTimeField(_('Date created'), auto_now_add=True)

    def __str__(self):
        return '{}: {}'.format(self.created_at, self.anket)

    def get_absolute_url(self):
        return reverse('summit:profile-email-detail', kwargs={'pk': self.pk})

    class Meta:
        ordering = ('-created_at', 'anket')
        verbose_name = _('Anket email')
        verbose_name_plural = _('Anket emails')


@python_2_unicode_compatible
class SummitLesson(models.Model):
    #: Summit to which the lesson
    summit = models.ForeignKey('summit.Summit', on_delete=models.CASCADE, related_name='lessons',
                               related_query_name='lessons', verbose_name=_('Summit'))
    #: List of the users who is view this lesson
    viewers = models.ManyToManyField('summit.SummitAnket', related_name='all_lessons',
                                     verbose_name=_('Viewers'))
    #: Lesson name
    name = models.CharField(_('Name'), max_length=255)

    def __str__(self):
        return '{}: {}'.format(self.summit, self.name)

    class Meta:
        ordering = ('summit', 'name')
        verbose_name = _('Summit lesson')
        verbose_name_plural = _('Summit lessons')
        unique_together = ('name', 'summit')


@python_2_unicode_compatible
class SummitUserConsultant(models.Model):
    consultant = models.ForeignKey('summit.SummitAnket', on_delete=models.CASCADE, related_name='consultees',
                                   limit_choices_to={'role__gte': SummitAnket.CONSULTANT},
                                   verbose_name=_('Consultant'))
    user = models.ForeignKey('summit.SummitAnket', on_delete=models.CASCADE, related_name='consultants',
                             verbose_name=_('User'))
    summit = models.ForeignKey('summit.Summit', on_delete=models.CASCADE, related_name='consultees',
                               verbose_name=_('Summit'))

    def __str__(self):
        return '{}: {} is consultant for {}'.format(self.summit, self.consultant, self.user)

    class Meta:
        verbose_name = _('Summit consultant')
        verbose_name_plural = _('Summit consultants')
        unique_together = ('user', 'summit')

    def clean(self):
        if self.summit != self.user.summit:
            raise ValidationError(_('Этот пользователь не участвует в данном саммите.'))
        if self.summit != self.consultant.summit:
            raise ValidationError(_('Этот пользователь не является консультантом на данном саммите.'))


@python_2_unicode_compatible
class SummitAnketNote(models.Model):
    summit_anket = models.ForeignKey('summit.SummitAnket', on_delete=models.CASCADE, related_name='notes',
                                     verbose_name=_('Summit anket'))
    owner = models.ForeignKey('account.CustomUser', on_delete=models.SET_NULL, related_name='notes',
                              null=True, blank=True, verbose_name=_('Owner of note'))

    text = models.CharField(_('Note'), max_length=1000)

    date_created = models.DateTimeField(_('Datetime created'), auto_now_add=True)

    def __str__(self):
        return self.short_text

    @property
    def short_text(self):
        return '{}...'.format(self.text[:47]) if len(self.text) > 50 else self.text

    @property
    def owner_name(self):
        return self.owner.fullname

    class Meta:
        verbose_name = _('Summit Anket Note')
        verbose_name_plural = _('Summit Anket Notes')
        ordering = ('-date_created',)


@python_2_unicode_compatible
class SummitVisitorLocation(models.Model):
    visitor = models.ForeignKey('summit.SummitAnket', verbose_name=_('Summit Visitor'),
                                related_name='visitor_locations')
    date_time = models.DateTimeField(verbose_name='Date Time', db_index=True)
    longitude = models.FloatField(verbose_name=_('Longitude'))
    latitude = models.FloatField(verbose_name=_('Latitude'))
    type = models.PositiveSmallIntegerField(verbose_name=_('Type'), default=1)

    class Meta:
        verbose_name_plural = _('Summit Users Location')
        verbose_name = _('Summit User Location')
        ordering = ('-id',)
        unique_together = ['visitor', 'date_time']

    def __str__(self):
        return 'Местонахождение участника саммита %s. Дата и время: %s' % (self.visitor, self.date_time)


@python_2_unicode_compatible
class SummitEventTable(models.Model):
    summit = models.ForeignKey('Summit', on_delete=models.CASCADE, verbose_name=_('Саммит'))
    hide_time = models.BooleanField(verbose_name=_('Не отображать время'), default=False)
    date_time = models.DateTimeField(verbose_name=_('Дата и Время'))
    name_ru = models.CharField(max_length=64, verbose_name=_('Название на Русском'))
    author_ru = models.CharField(max_length=64, verbose_name=_('Имя автора на Русском'), blank=True)
    name_en = models.CharField(max_length=64, verbose_name=_('Название на Английском'))
    author_en = models.CharField(max_length=64, verbose_name=_('Имя автора на Английском'), blank=True)
    name_de = models.CharField(max_length=64, verbose_name=_('Название на Немецком'))
    author_de = models.CharField(max_length=64, verbose_name=_('Имя автора на Немецком'), blank=True)

    class Meta:
        verbose_name = _('Расписание Саммита')
        verbose_name_plural = _('Расписание Саммита')
        ordering = ('-id',)

    @property
    def date(self):
        return self.date_time.date()

    @property
    def time(self):
        return self.date_time.time()

    def __str__(self):
        return self.author_ru


@python_2_unicode_compatible
class SummitAttend(models.Model):
    anket = models.ForeignKey('summit.SummitAnket', related_name='attends', verbose_name=_('Anket'))
    date = models.DateField(verbose_name=_('Date'), db_index=True)
    time = models.TimeField(verbose_name=_('Time'), null=True)
    status = models.CharField(verbose_name=_('Status'), max_length=20, default='')
    created_at = models.DateTimeField(_('Created at'), null=True, default=timezone.now, editable=False)

    class Meta:
        verbose_name = _('Summit Attend')
        verbose_name_plural = _('Summit Attends')
        ordering = ('-date',)
        unique_together = ['anket', 'date']

    def __str__(self):
        return '%s - visitor of Summit. Date: %s' % (self.anket.user.fullname, self.date)


@python_2_unicode_compatible
class AnketStatus(models.Model):
    anket = models.OneToOneField('summit.SummitAnket', related_name='status', verbose_name=_('Anket'))
    reg_code_requested = models.BooleanField(verbose_name=_('Запрос регистрационного кода'), default=False)
    reg_code_requested_date = models.DateTimeField(verbose_name=_('Дата ввода регистрационного кода'),
                                                   null=True, blank=True)
    active = models.BooleanField(verbose_name=_('Активна'), default=True)

    class Meta:
        verbose_name = _('Статус Анкеты')
        verbose_name_plural = _('Статусы Анкет')

    def __str__(self):
        return 'Anket %s. Reg_code_requested: %s. Active: %s' % (self.anket, self.reg_code_requested, self.active)


@python_2_unicode_compatible
class AnketPasses(models.Model):
    anket = models.ForeignKey('summit.SummitAnket', related_name='passes_count', verbose_name=_('Anket'))
    datetime = models.DateTimeField(verbose_name='Дата и время прохода', auto_now=True, editable=False)

    def __str__(self):
        return 'Проход анкеты: %s. Дата и время: %s.' % (self.anket, self.datetime)
