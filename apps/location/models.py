from django.utils.translation import ugettext_lazy as _

from django.db import models


class OldCountry(models.Model):
    code = models.IntegerField()
    title = models.CharField(max_length=50)
    phone_code = models.CharField(max_length=5, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'location_country'


class OldRegion(models.Model):
    code = models.IntegerField()
    title = models.CharField(max_length=50)
    country = models.ForeignKey(OldCountry, on_delete=models.PROTECT)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'location_region'


class OldCity(models.Model):
    code = models.IntegerField()
    title = models.CharField(max_length=50)
    region = models.ForeignKey(OldRegion, on_delete=models.PROTECT, null=True, blank=True)
    country = models.ForeignKey(OldCountry, on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'location_city'


class Country(models.Model):
    id = models.CharField(_('Id'), max_length=2, primary_key=True)
    name = models.CharField(_('Name'), max_length=128, unique=True)
    fullname = models.CharField(_('Full name'), max_length=256, blank=True)
    english = models.CharField(_('English name'), max_length=64, blank=True)
    country_code3 = models.CharField(_('Country code 3'), max_length=3, blank=True)
    iso = models.CharField(_('ISO'), max_length=3, blank=True)
    telcod = models.CharField(_('Tel code'), max_length=4, blank=True)
    location = models.CharField(_('Location'), max_length=20, default='')
    capital = models.PositiveIntegerField(_('Capital'), default=0)
    mcc = models.PositiveIntegerField(_('Код страны телефонных операторов'), default=0)
    lang = models.CharField(_('Name'), max_length=128, blank=True)

    class Meta:
        db_table = 'geo_country'

    def __str__(self):
        return self.fullname


class Area(models.Model):
    name = models.CharField(_('Name'), max_length=128, blank=True)
    okrug = models.CharField(_('Okrug'), max_length=128, blank=True)
    autocod = models.CharField(_('Auto code'), max_length=128, blank=True)
    capital = models.PositiveIntegerField(_('Capital'), default=0)
    english = models.CharField(_('English name'), max_length=64, blank=True)
    iso = models.CharField(_('ISO'), max_length=3, blank=True)
    country = models.ForeignKey('location.Country', on_delete=models.PROTECT,
                                related_name='areas', verbose_name=_('Country'))

    class Meta:
        db_table = 'geo_area'

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(_('Name'), max_length=128, blank=True)
    area = models.ForeignKey('location.Area', on_delete=models.PROTECT,
                             related_name='cities', verbose_name=_('Area'))
    telcod = models.CharField(_('Tel code'), max_length=48, blank=True, db_index=True)
    english = models.CharField(_('English name'), max_length=64, blank=True)
    rajon = models.PositiveIntegerField(_('Rajon'), default=0)
    country = models.ForeignKey('location.Country', on_delete=models.PROTECT,
                                related_name='cities', verbose_name=_('Country'))
    sound = models.CharField(_('Sound'), max_length=4, blank=True, db_index=True)
    UNKNOWN_LEVEL, CAPITAL, LARGE, SMALL = 0, 1, 2, 3
    LEVELS = (
         (UNKNOWN_LEVEL, _('---------')),
         (CAPITAL, _('Столица Округа')),
         (LARGE, _('Крупный город')),
         (SMALL, _('Небольшой населенный пункт')),
    )
    level = models.SmallIntegerField(_('Level'), choices=LEVELS, default=UNKNOWN_LEVEL)
    iso = models.CharField(_('ISO'), max_length=3, blank=True)

    UNKNOWN_VID, CITY, POSELOK, SELO, DEREVNIA, STANITSA, HUTOR = 0, 1, 2, 3, 4, 5, 6
    VID = (
        (UNKNOWN_VID, _('---------')),
        (CITY, _('Город')),
        (POSELOK, _('Поселок')),
        (SELO, _('Село')),
        (DEREVNIA, _('Деревня')),
        (STANITSA, _('Станица')),
        (HUTOR, _('Хутор')),
    )
    vid = models.SmallIntegerField(_('Level'), choices=UNKNOWN_VID)
    post = models.CharField(_('Post'), max_length=64, blank=True, db_index=True)
    geonameid = models.PositiveIntegerField(_('Geo name id'), blank=True, null=True, db_index=True)

    timezone = models.FloatField(_('Timezone'), blank=True, null=True)
    latitude = models.FloatField(_('Latitude'), blank=True, null=True)
    longitude = models.FloatField(_('Longitude'), blank=True, null=True)

    class Meta:
        db_table = 'geo_city'

    def __str__(self):
        return self.name
