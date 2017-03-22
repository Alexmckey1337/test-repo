================
Partner REST API
================

Partnership
-----------

Create partner payment
~~~~~~~~~~~~~~~~~~~~~~

.. http:post:: /api/v1.1/partnerships/(int:partner_id)/create_payment/

   Create new payment for ``Partner``.

   **Example request**:

   .. sourcecode:: http

      POST /api/v1.1/partnerships/4/create_payment/ HTTP/1.1
      Host: vocrm.org
      Accept: application/json
      content-type: application/json
      content-length: 100

      {
        "sum": "153",
        "description": "last",
        "rate": "1.24",
        "currency": 1,
        "sent_date": "2000-02-22"
      }

   .. include:: ../payment/partials/create_payment.rst

Deal
----

Create deal payment
~~~~~~~~~~~~~~~~~~~

.. http:post:: /api/v1.0/deals/(int:deal_id)/create_payment/

   Create new payment for ``Deal``.

   **Example request**:

   .. sourcecode:: http

      POST /api/v1.0/deals/4/create_payment/ HTTP/1.1
      Host: vocrm.org
      Accept: application/json
      content-type: application/json
      content-length: 100

      {
        "sum": "153",
        "description": "last",
        "rate": "1.24",
        "currency": 1,
        "sent_date": "2000-02-22"
      }

   .. include:: ../payment/partials/create_payment.rst
