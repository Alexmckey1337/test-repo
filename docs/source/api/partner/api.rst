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
        "operation": "*",
        "currency": 1,
        "sent_date": "2000-02-22"
      }

   .. include:: ../payment/partials/create_payment.rst


List of partners
~~~~~~~~~~~~~~~~

.. http:get:: /api/v1.1/partnerships/

    List of the partners for table (order by ``last_name``, ``first_name``, ``middle_name``).
    Pagination by 30 partners per page.

    **Example request**:

    .. sourcecode:: http

        GET /api/v1.1/partnerships/?page_size=2 HTTP/1.1
        Host: vocrm.org
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept, Cookie
        Allow: GET,HEAD,OPTIONS
        Content-Type: application/json

        {
          "links": {
            "next": "http://vocrm.org/api/v1.1/partnerships/?page=2&page_size=2",
            "previous": null
          },
          "count": 6043,
          "common_table": {
            "responsible": {
              "id": 256711,
              "title": "Менеджер",
              "ordering_title": "responsible__last_name",
              "number": 17,
              "active": true,
              "editable": false
            },
            "value": {
              "id": 220767,
              "title": "Сумма",
              "ordering_title": "value",
              "number": 18,
              "active": true,
              "editable": false
            }
          },
          "user_table": {
            "phone_number": {
              "id": 220752,
              "title": "Номер телефона",
              "ordering_title": "user__phone_number",
              "number": 1,
              "active": false,
              "editable": true
            },
            "fullname": {
              "id": 220756,
              "title": "ФИО",
              "ordering_title": "user__last_name",
              "number": 1,
              "active": true,
              "editable": false
            },
            "email": {
              "id": 220751,
              "title": "Email",
              "ordering_title": "user__email",
              "number": 2,
              "active": false,
              "editable": true
            },
            "born_date": {
              "id": 220753,
              "title": "Дата рождения",
              "ordering_title": "user__born_date",
              "number": 3,
              "active": false,
              "editable": true
            },
            "hierarchy": {
              "id": 220754,
              "title": "Иерархия",
              "ordering_title": "user__hierarchy__level",
              "number": 4,
              "active": true,
              "editable": true
            },
            "departments": {
              "id": 220755,
              "title": "Отдел",
              "ordering_title": "user__department__title",
              "number": 5,
              "active": true,
              "editable": true
            },
            "country": {
              "id": 220757,
              "title": "Страна",
              "ordering_title": "user__country",
              "number": 6,
              "active": false,
              "editable": true
            },
            "region": {
              "id": 220758,
              "title": "Область",
              "ordering_title": "user__region",
              "number": 7,
              "active": false,
              "editable": true
            },
            "city": {
              "id": 220759,
              "title": "Населенный пункт",
              "ordering_title": "user__city",
              "number": 8,
              "active": false,
              "editable": true
            },
            "district": {
              "id": 220760,
              "title": "Район",
              "ordering_title": "user__district",
              "number": 9,
              "active": false,
              "editable": true
            },
            "address": {
              "id": 220761,
              "title": "Адрес",
              "ordering_title": "user__address",
              "number": 10,
              "active": false,
              "editable": true
            },
            "social": {
              "id": 220762,
              "title": "Социальные сети",
              "ordering_title": "user__facebook",
              "number": 11,
              "active": false,
              "editable": true
            },
            "divisions": {
              "id": 220763,
              "title": "Отдел церкви",
              "ordering_title": "user__divisions",
              "number": 12,
              "active": false,
              "editable": true
            },
            "master": {
              "id": 220764,
              "title": "Ответственный",
              "ordering_title": "user__master__last_name",
              "number": 13,
              "active": false,
              "editable": true
            },
            "repentance_date": {
              "id": 626200,
              "title": "Дата Покаяния",
              "ordering_title": "user__repentance_date",
              "number": 14,
              "active": false,
              "editable": true
            },
            "spiritual_level": {
              "id": 626201,
              "title": "Духовный уровень",
              "ordering_title": "user__spiritual_level",
              "number": 15,
              "active": false,
              "editable": true
            }
          },
          "results": [
            {
              "id": 5538,
              "user": {
                "id": 15269,
                "link": "/account/15269/",
                "extra_phone_numbers": [],
                "description": "",
                "fullname": "User Other ",
                "hierarchy": {
                  "id": 5,
                  "title": "Епископ",
                  "level": 4
                },
                "departments": [
                  {
                    "id": 4,
                    "title": "Германия"
                  },
                  {
                    "id": 3,
                    "title": "Молдован"
                  },
                  {
                    "id": 5,
                    "title": "США"
                  }
                ]
              },
              "responsible": "Bruce Lee",
              "value": "100 €",
              "date": "2017-01-14",
              "fullname": "User Other ",
              "need_text": "",
              "level": 3,
              "currency": 3,
              "is_active": true
            },
            {
              "id": 6086,
              "user": {
                "id": 15187,
                "link": "/account/15187/",
                "extra_phone_numbers": null,
                "description": "",
                "fullname": "User Super ",
                "hierarchy": {
                  "id": 1,
                  "title": "Прихожанин",
                  "level": 0
                },
                "departments": [
                  {
                    "id": 1,
                    "title": "Киев"
                  }
                ]
              },
              "responsible": "Аккаунт Технический №1",
              "value": "114 грн.",
              "date": "2020-04-13",
              "fullname": "User Super ",
              "need_text": "",
              "level": 3,
              "currency": 2,
              "is_active": true
            }
          ]
        }

    :query int page: page number (one of ``int`` or ``last``). default is 1
    :query int hierarchy: filter by ``hierarchy_id``
    :query int master: filter by ``master_id``, returned children of master
    :query int master_tree: filter by ``master_id``, returned descendants of master and self master
    :query int department: filter by ``department_id``
    :query int page_size: page size, default is 30
    :query string search_fio: search by ``last_name``, ``first_name``, ``middle_name``, ``search_name``
    :query string search_email: search by ``email``
    :query string search_phone_number: search by main ``phone_number``
    :query string search_country: search by ``country``
    :query string search_city: search by ``city``
    :query string ordering: order by one of ``user__first_name``, ``user__last_name``, ``user__master__last_name``,
                       ``user__middle_name``, ``user__born_date``, ``user__country``,
                       ``user__region``, ``user__city``, ``user__disrict``,
                       ``user__address``, ``user__skype``, ``user__phone_number``,
                       ``user__email``, ``user__hierarchy__level``,
                       ``user__facebook``, ``user__vkontakte``, ``value``, ``responsible__last_name``

    :statuscode 200: no error

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
        "operation": "*",
        "currency": 1,
        "sent_date": "2000-02-22"
      }

   .. include:: ../payment/partials/create_payment.rst
