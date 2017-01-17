====================
Account templatetags
====================

account_tags
------------

Checking the right to edit user
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. py:function:: user_can_edit(user_to_id[, user_from=None])

   Return whether the user ``user_from`` can edit user with id = ``user_to_id``

   :param int user_to_id: ``id`` of user
   :param int user_from: ``id`` of user or CustomUser object, optional.
                         If not specified, the current user is taken.
   :return: True or False

Using
~~~~~

.. code-block:: html

   load tags library
   {% load account_tags %}
   ...
   {% user_can_edit 11 as can_edit %}
     or
   {% user_can_edit 11 46 as can_edit %}
     or
   {% user_can_edit 11 custom_user_object as can_edit %}
     or
   {% user_can_edit 11 custom_user_object.id as can_edit %}
   ...
   {% if can_edit %}
     <button name="edit">Edit</button>
   {% endif %}
