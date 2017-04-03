from django.conf import settings

from account.abstact_models import UserPermission
from partnership.permissions import can_see_partners, can_see_deals, can_see_partner_stats, can_see_deal_payments


class PartnerUserPermission(UserPermission):
    class Meta:
        abstract = True

    def can_see_partners(self):
        request = self._perm_req()
        return can_see_partners(request)

    def can_see_deals(self):
        request = self._perm_req()
        return can_see_deals(request)

    def can_see_deal_payments(self):
        request = self._perm_req()
        return can_see_deal_payments(request)

    def can_see_partner_stats(self):
        request = self._perm_req()
        return can_see_partner_stats(request)

    def can_see_any_partner_block(self):
        return any((self.can_see_partners(),
                    self.can_see_deals(),
                    self.can_see_partner_stats(),
                    self.can_see_deal_payments()))

    @property
    def is_partner(self):
        return self._partner() is not None

    @property
    def is_partner_manager(self):
        partner = self._partner()
        return self.is_partner and partner.level == settings.PARTNER_LEVELS['manager']

    @property
    def is_partner_manager_or_high(self):
        partner = self._partner()
        return self.is_partner and partner.level <= settings.PARTNER_LEVELS['manager']

    @property
    def is_partner_supervisor(self):
        partner = self._partner()
        return self.is_partner and partner.level == settings.PARTNER_LEVELS['supervisor']

    @property
    def is_partner_supervisor_or_high(self):
        partner = self._partner()
        return self.is_partner and partner.level <= settings.PARTNER_LEVELS['supervisor']

    @property
    def is_partner_director(self):
        partner = self._partner()
        return self.is_partner and partner.level == settings.PARTNER_LEVELS['director']

    # Helpers

    def _partner(self):
        return getattr(self, 'partnership', None)
