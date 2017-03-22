================
Payment REST API
================

Payment
-------

Create payment
~~~~~~~~~~~~~~

.. http:post:: /api/v1.1/partnerships/(int:partner_id)/create_payment/
.. http:post:: /api/v1.0/deals/(int:deal_id)/create_payment/
.. http:post:: /api/v1.0/summit_ankets/(int:anket_id)/create_payment/

    Create new payment for ``Partner``, ``Deal`` or ``Summit Anket``.

    **Example request**:

    .. sourcecode:: http

        POST /api/v1.0/<purpose>/4/create_payment/ HTTP/1.1
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

    .. include:: partials/create_payment.rst


Delete payment
~~~~~~~~~~~~~~

.. http:delete:: /api/v1.0/payments/(int:payment_id)/

    Delete payment with ``id = payment_id``

    **Example request**:

    .. sourcecode:: http

        DELETE /api/v1.0/payments/6/ HTTP/1.1
        Host: vocrm.org
        Accept: application/json
        content-type: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 204 No Content
        Vary: Accept, Cookie
        Allow: PATCH,DELETE,OPTIONS
        Content-Type: application/json

    **Example response (payment does not exist)**:

    .. sourcecode:: http

        HTTP/1.1 404 Not Found
        Vary: Accept, Cookie
        Allow: PATCH,DELETE,OPTIONS
        Content-Type: application/json

        {
          "detail": "Не найдено."
        }

    **Example response (don't have permissions)**:

    .. sourcecode:: http

        HTTP/1.1 403 Forbidden
        Vary: Accept, Cookie
        Allow: PATCH,DELETE,OPTIONS
        Content-Type: application/json

        {
          "detail": "У вас нет прав для выполнения этой операции."
        }

    :statuscode 204: payment deleted
    :statuscode 404: payment does not exist
    :statuscode 403: user does not permissions for delete payment



Update payment
~~~~~~~~~~~~~~

.. http:patch:: /api/v1.0/payments/(int:payment_id)/

    Partial update payment with ``id = payment_id``

    **Example request**:

    .. sourcecode:: http

        PATCH /api/v1.0/payments/6/ HTTP/1.1
        Host: vocrm.org
        Accept: application/json
        content-type: application/json

        {
          "sum": 3010,
          "currency_sum": 2,
          "sent_date": "2017-02-03",
          "rate": 1,
          "description": "hello",
          "object_id": 19479
        }

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept, Cookie
        Allow: PATCH,DELETE,OPTIONS
        Content-Type: application/json

        {
          "sum": "3010",
          "currency_sum": 2,
          "sent_date": "03.02.2017",
          "rate": "1.000",
          "description": "hello",
          "object_id": 19479
        }

    **Example response (payment does not exist)**:

    .. sourcecode:: http

        HTTP/1.1 404 Not Found
        Vary: Accept, Cookie
        Allow: PATCH,DELETE,OPTIONS
        Content-Type: application/json

        {
          "detail": "Не найдено."
        }

    **Example response (don't have permissions)**:

    .. sourcecode:: http

        HTTP/1.1 403 Forbidden
        Vary: Accept, Cookie
        Allow: PATCH,DELETE,OPTIONS
        Content-Type: application/json

        {
          "detail": "У вас нет прав для выполнения этой операции."
        }

    **Example response (Bad request)**:

    .. sourcecode:: http

        HTTP/1.1 400 Bad Request
        Vary: Accept, Cookie
        Allow: PATCH,DELETE,OPTIONS
        Content-Type: application/json

        {
          "detail": "JSON parse error - Expecting value: line 1 column 1 (char 0)"
        }

    :form sum: sum of payment, integer, optional
    :form rate: rate of ``sum`` -> ``effective_sum``, decimal,
                format ``123.456`` or ``123.45`` or ``123.4`` or ``123``, optional
    :form description: description for payment, optional
    :form currency_sum: currency_id of ``sum``, optional
    :form sent_date: date of payment, format ``2015-03-24``, optional
    :form object_id: id of purpose (like as ``deal``, ``partner``, ``summit_anket``)

    :statuscode 200: payment updated
    :statuscode 404: payment does not exist
    :statuscode 403: user don't have permissions for update payment
    :statuscode 400: bad request

Currency
--------
