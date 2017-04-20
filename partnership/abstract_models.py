from django.conf import settings

from account.abstact_models import UserPermission
from partnership.permissions import can_see_partners, can_see_deals, can_see_partner_stats, can_see_deal_payments, \
    can_close_partner_deals, can_create_partner_payments, can_export_partner_list, can_create_deal_for_partner, \
    can_update_partner_need, can_update_deal, can_create_payment_for_partner


class PartnerUserPermission(UserPermission):
    class Meta:
        abstract = True

    def can_see_partners(self):
        """
        Checking that the ``self`` user has the right to see list of partners
        """
        return can_see_partners(self)

    def can_export_partner_list(self):
        """
        Checking that the ``self`` user has the right to export list of partners
        """
        return can_export_partner_list(self)

    def can_see_deals(self):
        """
        Checking that the ``self`` user has the right to see list of deals
        """
        return can_see_deals(self)

    def can_see_deal_payments(self):
        """
        Checking that the ``self`` user has the right to see list of payments by deals
        """
        return can_see_deal_payments(self)

    def can_see_partner_stats(self):
        """
        Checking that the ``self`` user has the right to see statistic of partners
        """
        return can_see_partner_stats(self)

    def can_see_any_partner_block(self):
        """
        Checking that the ``self`` user has the right to see one of
        [``list of partners``, ``list of deals``, ``list of payments by deals`` or ``statistic by partners``]
        """
        return any((self.can_see_partners(),
                    self.can_see_deals(),
                    self.can_see_partner_stats(),
                    self.can_see_deal_payments()))

    def can_close_partner_deals(self):
        """
        Checking that the ``self`` user has the right to close deals of partnership
        """
        return can_close_partner_deals(self)

    def can_create_partner_payments(self):
        """
        Checking that the ``self`` user has the right to create payments by deals
        """
        return can_create_partner_payments(self)

    def can_create_payment_for_partner(self, partner):
        """
        Checking that the ``self`` user has the right to create payment for certain ``partner``
        """
        return can_create_payment_for_partner(self, partner)

    def can_create_deal_for_partner(self, partner):
        """
        Checking that the ``self`` user has the right to create deal for certain ``partner``
        """
        return can_create_deal_for_partner(self, partner)

    def can_update_deal(self, deal):
        """
        Checking that the ``self`` user has the right to update ``deal``
        """
        return can_update_deal(self, deal)

    def can_update_partner_need(self, partner):
        """
        Checking that the ``self`` user has the right to update need field of certain ``partner``
        """
        return can_update_partner_need(self, partner)

    @property
    def is_partner(self):
        """
        Checking that the ``self`` user is partner
        """
        return self._partner() is not None

    @property
    def is_partner_manager(self):
        """
        Checking that the ``self`` user is manager by partnership
        """
        partner = self._partner()
        return self.is_partner and partner.level == settings.PARTNER_LEVELS['manager']

    @property
    def is_partner_manager_or_high(self):
        """
        Checking that the ``self`` user is one of [manager, supervisor or director] by partnership
        """
        partner = self._partner()
        return self.is_partner and partner.level <= settings.PARTNER_LEVELS['manager']

    @property
    def is_partner_supervisor(self):
        """
        Checking that the ``self`` user is supervisor by partnership
        """
        partner = self._partner()
        return self.is_partner and partner.level == settings.PARTNER_LEVELS['supervisor']

    @property
    def is_partner_supervisor_or_high(self):
        """
        Checking that the ``self`` user is one of [supervisor or director] by partnership
        """
        partner = self._partner()
        return self.is_partner and partner.level <= settings.PARTNER_LEVELS['supervisor']

    @property
    def is_partner_director(self):
        """
        Checking that the ``self`` user is director by partnership
        """
        partner = self._partner()
        return self.is_partner and partner.level == settings.PARTNER_LEVELS['director']

    def is_partner_responsible_of(self, user):
        """
        Checking that the `` self`` user is responsible of ``user``
        """
        if not isinstance(user, (int, str)):
            user = user.id
        partner = self._partner()
        return self.is_partner and partner.disciples.filter(user_id=user).exists()

    # Helpers

    def _partner(self):
        return getattr(self, 'partnership', None)
