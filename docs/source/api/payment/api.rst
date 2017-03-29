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


List of deal payments
~~~~~~~~~~~~~~~~~~~~~

.. http:get:: /api/v1.0/payments/deal/

    List of the deal payments for table.
    Pagination by 30 payment per page.

    **Example request**:

    .. sourcecode:: http

        GET /api/v1.1/payments/deal/?page_size=2 HTTP/1.1
        Host: vocrm.org
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept, Cookie
        Allow: GET,HEAD,OPTIONS
        Content-Type: application/json

        {
          "count": 6415,
          "next": "http://vocrm.org/api/v1.0/payments/deal/?page=2&page_size=2",
          "previous": null,
          "results": [
            {
              "id": 8614,
              "sum": "44",
              "effective_sum": "44.000",
              "sum_str": "44 грн.",
              "effective_sum_str": "44.000 грн.",
              "currency_sum": {
                "id": 2,
                "name": "Гривна",
                "code": "uah",
                "short_name": "грн.",
                "symbol": "₴"
              },
              "currency_rate": {
                "id": 2,
                "name": "Гривна",
                "code": "uah",
                "short_name": "грн.",
                "symbol": "₴"
              },
              "rate": "1.000",
              "description": "",
              "created_at": "14.03.2017 11:33",
              "sent_date": "14.03.2017",
              "manager": {
                "id": 13885,
                "first_name": "Manager",
                "last_name": "Your",
                "middle_name": ""
              },
              "purpose": "/api/v1.0/deals/16495/",
              "purpose_fio": "I Am User"
            },
            {
              "id": 8613,
              "sum": "40",
              "effective_sum": "56.000",
              "sum_str": "40 €",
              "effective_sum_str": "56.000 грн.",
              "currency_sum": {
                "id": 3,
                "name": "Евро",
                "code": "eur",
                "short_name": "eвр.",
                "symbol": "€"
              },
              "currency_rate": {
                "id": 2,
                "name": "Гривна",
                "code": "uah",
                "short_name": "грн.",
                "symbol": "₴"
              },
              "rate": "1.400",
              "description": "",
              "created_at": "14.03.2017 11:33",
              "sent_date": "14.03.2017",
              "manager": {
                "id": 13885,
                "first_name": "Super",
                "last_name": "Man",
                "middle_name": ""
              },
              "purpose": "/api/v1.0/deals/27087/",
              "purpose_fio": "And Iam Too"
            }
          ]
        }

    :query int page: page number (one of ``int`` or ``last``). default is 1
    :query int sum_from: filter by ``sum``, returned payments with ``sum >= sum_from``
    :query int sum_to: filter by ``sum``, returned payments with ``sum <= sum_to``
    :query int eff_sum_from: filter by ``effective_sum``, returned payments with ``effective_sum >= eff_sum_from``
    :query int eff_sum_to: filter by ``effective_sum``, returned payments with ``effective_sum <= eff_sum_to``
    :query int currency_sum: filter by ``currency_sum.id``, returned payments with currency.id of sum == ``currency_sum``
    :query int currency_rate: filter by ``currency_rate.id``,
                              returned payments with currency.id of effective sum == ``currency_rate``
    :query int manager: filter by ``manager.id``
    :query string create_from: filter by created date of payment, ``created_at >= create_from``
    :query string create_to: filter by created date of payment, ``created_at <= create_to``
    :query string sent_from: filter by sent date of payment, ``sent_date >= sent_from``
    :query string sent_to: filter by sent date of payment, ``sent_date <= sent_to``
    :query string search_description: search by ``description``
    :query string search_purpose_fio: search by ``fio`` of purpose.user
    :query string ordering: order by one of ``sum``, ``effective_sum``, ``currency_sum__name``,
                        ``currency_rate__name``, ``created_at``, ``sent_date``,
                        ``manager__last_name``

    :statuscode 200: no error

Currency
--------
