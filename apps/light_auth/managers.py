from datetime import timedelta

from django.db import models
from django.db.models import Q
from django.utils import timezone

from apps.light_auth import app_settings


class PhoneNumberManager(models.Manager):
    def add_phone(self, request, auth_user, phone, confirm=False, reset_password=False):
        phone_number, created = self.get_or_create(
            auth_user=auth_user, phone__iexact=phone, defaults={"phone": phone}
        )
        if created and confirm:
            phone_number.send_confirmation(request, reset_password=reset_password)
        return phone_number

    def get_primary(self, auth_user):
        try:
            return self.get(auth_user=auth_user, primary=True)
        except self.model.DoesNotExist:
            return None


class PhoneConfirmationManager(models.Manager):

    def all_expired(self):
        return self.filter(self.expired_q())

    def all_valid(self):
        return self.exclude(self.expired_q())

    def expired_q(self):
        sent_threshold = timezone.now() - timedelta(days=app_settings.EMAIL_CONFIRMATION_EXPIRE_DAYS)
        return Q(sent__lt=sent_threshold)

    def delete_expired_confirmations(self):
        self.all_expired().delete()
