from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.light_auth.api.permissions import has_light_auth_perm
from apps.light_auth.models import PhoneNumber, PhoneConfirmation, LightAuthUser, LightToken
from apps.light_auth.utils import make_phone_number


class AbstractProjectUser(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        try:
            light_auth = LightAuthUser.objects.get(user=self)
            primary_phone = PhoneNumber.objects.get_primary(auth_user=light_auth)
            new_phone = make_phone_number(self.phone_number)
            if PhoneNumber.objects.filter(phone=new_phone).exclude(auth_user__user=self).exists():
                # TODO light_auth with this phone is already exist
                # PhoneNumber.objects.filter(auth_user=light_auth, primary=True).delete()
                raise ValidationError(_('Пользователь с телефоном %s уже существует') % new_phone)
            if primary_phone is None:
                primary_phone = PhoneNumber.objects.add_phone(None, light_auth, new_phone, confirm=True)
                # primary_phone.set_as_primary()
            elif primary_phone.phone != new_phone:
                primary_phone.change(None, new_phone)
                LightToken.objects.filter(user=light_auth).delete()
        except LightAuthUser.DoesNotExist:
            pass
        super().save(*args, **kwargs)

    def has_light_auth(self):
        return bool(self.light_auth)

    def has_light_auth_password(self):
        return self.has_light_auth() and self.light_auth.has_usable_password()

    def phone_number_is_already_exist(self):
        return self.similar_user() is not None

    def similar_user(self):
        phone = make_phone_number(self.phone_number)
        if not phone:
            return None
        try:
            return PhoneNumber.objects.get(phone=phone).auth_user.user
        except PhoneNumber.DoesNotExist:
            return None

    @property
    def light_auth_phones(self):
        if self.has_light_auth():
            return PhoneNumber.objects.filter(auth_user=self.light_auth)
        return PhoneNumber.objects.none()

    @property
    def light_auth_verified_phones(self):
        return self.light_auth_phones.filter(verified=True)

    @property
    def light_auth_primary_phone(self):
        if self.has_light_auth():
            return PhoneNumber.objects.get_primary(auth_user=self.light_auth)
        return None

    @property
    def last_phone_confirmation(self):
        return PhoneConfirmation.objects.filter(
            phone_number=self.light_auth_primary_phone, sent__isnull=False).order_by('-sent', '-created').first()

    def has_light_auth_perm(self, user=None):
        return has_light_auth_perm(self, user)
