================
User permissions
================

User
----

User can create new user if:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- user is staff
- user have hierarchy level >= 1 (leader)
- user is supervisor by partner section
- user is supervisor by active summit section


User can export user list if:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- user is staff
- user have hierarchy level >= 2 (pastor)


User can see user list if:
~~~~~~~~~~~~~~~~~~~~~~~~~~

- user is staff
- user is master (he have disciples)

Permissions
~~~~~~~~~~~

.. autoclass:: account.permissions.CanCreateUser
    :members:
    :noindex:

.. autoclass:: account.permissions.CanExportUserList
    :members:
    :noindex:

.. autoclass:: account.permissions.CanSeeUserList
    :members:
    :noindex:


Model methods of permission
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: account.models.CustomUser
    :members: can_create_user, can_export_user_list, can_see_user_list
    :noindex:
