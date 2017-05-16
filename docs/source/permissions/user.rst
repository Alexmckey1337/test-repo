================
User permissions
================

User can
~~~~~~~~

Create new user if:
"""""""""""""""""""

- user is staff
- user have hierarchy level >= 1 (leader)
- user is supervisor by partner section
- user is supervisor by active summit section


Export user list if:
""""""""""""""""""""

- user is staff
- user have hierarchy level >= 2 (pastor)


See user list if:
"""""""""""""""""

- user is staff
- user is master (he have disciples)

See partner list if:
""""""""""""""""""""

- user is manager, supervisor or director by partnership

Export partner list if:
"""""""""""""""""""""""

- user is manager, supervisor or director by partnership

See deal list if:
"""""""""""""""""

- user is manager, supervisor or director by partnership

See deal payments if:
"""""""""""""""""""""

- user is manager, supervisor or director by partnership

See statistics by partner if:
"""""""""""""""""""""""""""""

- user is manager, supervisor or director by partnership

Closing deals if:
"""""""""""""""""

- user is manager, supervisor or director by partnership

Create payments by deals if:
""""""""""""""""""""""""""""

- user is supervisor or director by partnership

Create deal for partner if:
"""""""""""""""""""""""""""

- user is supervisor by partnership or he is responsible of partner

Update need field of partner:
"""""""""""""""""""""""""""""

- user is supervisor by partnership or he is responsible of partner

Permissions
~~~~~~~~~~~

Classes
"""""""
Use with django-rest-framework

.. autoclass:: account.permissions.CanCreateUser
    :members:
    :noindex:

.. autoclass:: account.permissions.CanExportUserList
    :members:
    :noindex:

.. autoclass:: account.permissions.CanSeeUserList
    :members:
    :noindex:

.. autoclass:: partnership.permissions.CanSeePartners
    :members:
    :noindex:

.. autoclass:: partnership.permissions.CanExportPartnerList
    :members:
    :noindex:

.. autoclass:: partnership.permissions.CanSeeDeals
    :members:
    :noindex:

.. autoclass:: partnership.permissions.CanSeeDealPayments
    :members:
    :noindex:

.. autoclass:: partnership.permissions.CanSeePartnerStatistics
    :members:
    :noindex:

.. autoclass:: partnership.permissions.CanCreatePartnerPayment
    :members:
    :noindex:

.. autoclass:: partnership.permissions.CanCreateDeals
    :members:
    :noindex:

.. autoclass:: partnership.permissions.CanUpdatePartner
    :members:
    :noindex:


Functions
"""""""""

.. autofunction:: account.permissions.can_see_account_page
    :noindex:

.. autofunction:: account.permissions.can_create_user
    :noindex:

.. autofunction:: account.permissions.can_export_user_list
    :noindex:

.. autofunction:: account.permissions.can_see_user_list
    :noindex:

.. autofunction:: account.permissions.can_edit_status_block
    :noindex:

.. autofunction:: account.permissions.can_edit_description_block
    :noindex:

.. autofunction:: summit.permissions.can_see_summit_block
    :noindex:

.. autofunction:: summit.permissions.can_edit_summit_block
    :noindex:

.. autofunction:: group.permissions.can_see_churches
    :noindex:

.. autofunction:: group.permissions.can_see_home_groups
    :noindex:

.. autofunction:: group.permissions.can_see_church_block
    :noindex:

.. autofunction:: group.permissions.can_edit_church_block
    :noindex:


Model methods of permission
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: account.models.CustomUser
    :members: can_create_user, can_export_user_list, can_see_user_list, can_see_partners, can_see_deals,
              can_see_deal_payments, can_see_partner_stats, can_close_partner_deals, can_create_deal_for_partner,
              can_create_partner_payments, can_see_any_partner_block, can_export_partner_list,
              can_update_partner_need, can_edit_status_block, can_edit_description_block, can_edit_partner_block,
              can_see_partner_block, can_edit_church_block, can_see_church_block, can_edit_summit_block,
              can_see_summit_block, can_see_deal_block, can_see_churches, can_see_home_groups
    :noindex:
