from django.conf import settings
from django.db import models

from apps.partnership.api.permissions import (
    can_see_partners, can_see_deals, can_see_partner_stats, can_see_deal_payments,
    can_close_partner_deals, can_create_partner_payments, can_export_partner_list,
    can_create_deal_for_partner, can_update_partner_need, can_update_deal, can_create_payment_for_partner,
    can_update_partner, can_see_partner_summary, can_see_managers_summary, can_update_church_deal,
    can_update_church_partner,
    can_create_church_deal_for_partner, can_create_church_partner_payments, can_close_church_partner_deals)


class PartnerUserPermission(models.Model):
    class Meta:
        abstract = True

    def can_see_partners(self):
        """
        Checking that the ``self`` user has the right to see list of partners
        """
        return can_see_partners(self)

    def can_see_partner_summary(self):
        """
        Checking that the ``self`` user has the right to see partner summary
        """
        return can_see_partner_summary(self)

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

    def can_close_church_partner_deals(self):
        """
        Checking that the ``self`` user has the right to close deals of church partner
        """
        return can_close_church_partner_deals(self)

    def can_create_partner_payments(self):
        """
        Checking that the ``self`` user has the right to create payments by deals
        """
        return can_create_partner_payments(self)

    def can_create_church_partner_payments(self):
        """
        Checking that the ``self`` user has the right to create payments by church deals
        """
        return can_create_church_partner_payments(self)

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

    def can_update_partner(self, user):
        """
        Checking that the ``self`` user has the right to update partnership of ``user``
        """
        return can_update_partner(self, user)

    def can_update_partner_need(self, partner):
        """
        Checking that the ``self`` user has the right to update need field of certain ``partner``
        """
        return can_update_partner_need(self, partner)

    def can_see_managers_summary(self):
        """
        Checking that the ``self`` has the right to see manager's summary
        """
        return can_see_managers_summary(self)

    def can_update_church_deal(self, church_deal):
        """
        Checking that the ``self`` user has the right to update ``church_deal``
        """
        return can_update_church_deal(self, church_deal)

    def can_update_church_partner(self, church):
        """
        Checking that the ``self`` user has the right to update partnership of ``church``
        """
        return can_update_church_partner(self, church)

    def can_create_church_deal_for_partner(self, partner):
        """
        Checking that the ``self`` user has the right to create deal for certain ``partner``
        """
        return can_create_church_deal_for_partner(self, partner)

    @property
    def is_partner(self):
        """
        Checking that the ``self`` user is partner
        """
        return self.partners.exists()

    @property
    def has_partner_role(self):
        """
        Checking that the ``self`` user has partner role
        """
        return self._partner_role() is not None

    @property
    def is_partner_manager(self):
        """
        Checking that the ``self`` user is manager by partnership
        """
        partner_role = self._partner_role()
        return self.has_partner_role and partner_role.level == settings.PARTNER_LEVELS['manager']

    @property
    def is_partner_manager_or_high(self):
        """
        Checking that the ``self`` user is one of [manager, supervisor or director] by partnership
        """
        partner_role = self._partner_role()
        return self.has_partner_role and partner_role.level <= settings.PARTNER_LEVELS['manager']

    @property
    def is_partner_supervisor(self):
        """
        Checking that the ``self`` user is supervisor by partnership
        """
        partner_role = self._partner_role()
        return self.has_partner_role and partner_role.level == settings.PARTNER_LEVELS['supervisor']

    @property
    def is_partner_supervisor_or_high(self):
        """
        Checking that the ``self`` user is one of [supervisor or director] by partnership
        """
        partner_role = self._partner_role()
        return self.has_partner_role and partner_role.level <= settings.PARTNER_LEVELS['supervisor']

    @property
    def is_partner_director(self):
        """
        Checking that the ``self`` user is director by partnership
        """
        partner_role = self._partner_role()
        return self.has_partner_role and partner_role.level == settings.PARTNER_LEVELS['director']

    def is_partner_responsible_of(self, user_id, check_partner_role=True):
        """
        Checking that the ``self`` user is responsible of ``user``
        """
        from apps.partnership.models import Partnership
        if not isinstance(user_id, (int, str)):
            user_id = user_id.id
        is_responsible = Partnership.objects.filter(responsible=self, user_id=user_id).exists()
        if check_partner_role:
            return self.has_partner_role and is_responsible
        return is_responsible

    def is_partner_responsible_of_church(self, church_id, check_partner_role=True):
        """
        Checking that the ``self`` user is responsible of ``church``
        """
        from apps.partnership.models import ChurchPartner
        if not isinstance(church_id, (int, str)):
            church_id = church_id.id
        is_responsible = ChurchPartner.objects.filter(responsible=self, church_id=church_id).exists()
        if check_partner_role:
            return self.has_partner_role and is_responsible
        return is_responsible

    # Helpers

    def _partner_role(self):
        return getattr(self, 'partner_role', None)
