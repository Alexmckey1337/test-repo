import datetime

from django.contrib.auth import password_validation
from django.contrib.auth.hashers import (
    check_password, is_password_usable, make_password,
)
from django.db import models, transaction
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _

from apps.light_auth import app_settings
from apps.light_auth.managers import PhoneConfirmationManager, PhoneNumberManager
from apps.light_auth.utils import send_confirmation_sms


class LightAuthUser(models.Model):
    user = models.OneToOneField(
        app_settings.USER_MODEL, on_delete=models.CASCADE, related_name='light_auth'
    )
    password = models.CharField(_('password'), max_length=128)
    last_login = models.DateTimeField(_('last login'), blank=True, null=True)
    is_active = models.BooleanField(
        _('active'),
        default=True,
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    def __str__(self):
        return str(self.user)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not hasattr(self, '_password'):
            self._password = None
        elif self._password is not None:
            password_validation.password_changed(self._password, self)
            self._password = None

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self._password = raw_password

    def check_password(self, raw_password):
        """
        Return a boolean of whether the raw_password was correct. Handles
        hashing formats behind the scenes.
        """

        def setter(raw_password):
            self.set_password(raw_password)
            # Password hash upgrades shouldn't be considered password changes.
            self._password = None
            self.save(update_fields=["password"])

        return check_password(raw_password, self.password, setter)

    def set_unusable_password(self):
        # Set a value that will never be a valid hash
        self.password = make_password(None)

    def has_usable_password(self):
        """
        Return False if set_unusable_password() has been called for this user.
        """
        return is_password_usable(self.password)


class LightToken(models.Model):
    """
    The light authorization token model.
    """
    key = models.CharField(_("Key"), max_length=40, primary_key=True)
    user = models.ForeignKey(
        'light_auth.LightAuthUser', related_name='auth_tokens',
        on_delete=models.CASCADE, verbose_name=_("Light User")
    )
    created = models.DateTimeField(_("Created"), auto_now_add=True)

    class Meta:
        verbose_name = _("Token")
        verbose_name_plural = _("Tokens")

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    def generate_key(self):
        return get_random_string(20)

    def __str__(self):
        return self.key


class PhoneNumber(models.Model):
    auth_user = models.ForeignKey(
        'light_auth.LightAuthUser', verbose_name=_('auth'), on_delete=models.CASCADE
    )
    phone = models.CharField(unique=True, max_length=40, verbose_name=_('phone number'))
    verified = models.BooleanField(verbose_name=_('verified'), default=False)
    primary = models.BooleanField(verbose_name=_('primary'), default=False)

    objects = PhoneNumberManager()

    class Meta:
        verbose_name = _("phone number")
        verbose_name_plural = _("phone numbers")

    def __str__(self):
        return f"{self.phone} ({self.auth_user})"

    def set_as_primary(self, conditional=False):
        old_primary = PhoneNumber.objects.get_primary(self.auth_user)
        if old_primary:
            if conditional:
                return False
            old_primary.primary = False
            old_primary.save()
        self.primary = True
        self.save()
        return True

    def send_confirmation(self, request=None, reset_password=False):
        confirmation = PhoneConfirmation.create(self)
        confirmation.send(request, reset_password=reset_password)
        return confirmation

    def change(self, request, new_phone, confirm=True):
        """
        Given a new phone, change self and re-confirm.
        """
        with transaction.atomic():
            # self.auth_user.user.phone_number = new_phone
            # self.auth_user.user.save()
            self.phone = new_phone
            self.verified = False
            self.save()
            if confirm:
                self.send_confirmation(request)


class PhoneConfirmation(models.Model):
    phone_number = models.ForeignKey(
        PhoneNumber, verbose_name=_('phone number'), on_delete=models.CASCADE
    )
    created = models.DateTimeField(verbose_name=_('created'), default=timezone.now)
    sent = models.DateTimeField(verbose_name=_('sent'), null=True)
    key = models.CharField(verbose_name=_('key'), max_length=64, unique=True)

    objects = PhoneConfirmationManager()

    class Meta:
        verbose_name = _("phone confirmation")
        verbose_name_plural = _("phone confirmations")

    def __str__(self):
        return "confirmation for %s" % self.phone_number

    @classmethod
    def create(cls, phone_number):
        key = get_random_string(8).lower()
        while cls._default_manager.filter(key=key).exists():
            key = get_random_string(8).lower()
        return cls._default_manager.create(phone_number=phone_number, key=key)

    def key_expired(self):
        expiration_date = self.sent + datetime.timedelta(days=app_settings.EMAIL_CONFIRMATION_EXPIRE_DAYS)
        return expiration_date <= timezone.now()

    key_expired.boolean = True

    def confirm(self, request):
        if not self.key_expired() and not self.phone_number.verified:
            self.phone_number.verified = True
            self.phone_number.set_as_primary(conditional=True)
            self.phone_number.save()
            return self.phone_number

    def send(self, request=None, reset_password=False):
        send_confirmation_sms(request, self, reset_password)
        self.sent = timezone.now()
        self.save()
