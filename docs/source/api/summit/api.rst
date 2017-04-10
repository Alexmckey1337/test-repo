===============
Summit REST API
===============

Summit
------

.. http:get:: /api/v1.0/summit/(int:summit_id)/

   Information about ``Summit`` with id = ``summit_id``.

   **Example request**:

   .. sourcecode:: http

      GET /api/v1.0/summit/4/ HTTP/1.1
      Host: vocrm.org
      Accept: application/json

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept, Cookie
      Allow: GET,HEAD,OPTIONS
      Content-Type: application/json

      {
        "id": 4,
        "start_date": "14.11.2016",
        "end_date": "14.11.2016",
        "title": "Колледж",
        "description": "star wars",
        "lessons": [
          5,
          6,
          7
        ],
        "club_name": "",
        "full_cost": "0",
        "special_cost": null
      }

   **Example response (Not Found)**:

   .. sourcecode:: http

      HTTP/1.1 404 Not Found
      Vary: Accept, Cookie
      Allow: GET,HEAD,OPTIONS
      Content-Type: application/json

      {
        "detail": "Не найдено."
      }

   :reqheader Accept: the response content type depends on
                          :mailheader:`Accept` header
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 200: no error
   :statuscode 404: there's no summit


.. http:get:: /api/v1.0/summit/

   List of summits (order by ``-start_date`` desc). Pagination by 30 summits per page.

   **Example request**:

   .. sourcecode:: http

      GET /api/v1.0/summit/ HTTP/1.1
      Host: vocrm.org
      Accept: application/json

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept, Cookie
      Allow: GET,HEAD,OPTIONS
      Content-Type: application/json

      {
        "count": 2,
        "next": null,
        "previous": null,
        "results": [
          {
            "id": 4,
            "start_date": "14.11.2016",
            "end_date": "14.11.2016",
            "title": "Колледж",
            "description": "star wars",
            "lessons": [
              5,
              6,
              7
            ],
            "club_name": "",
            "full_cost": "0",
            "special_cost": null
          },
          {
            "id": 3,
            "start_date": "07.10.2016",
            "end_date": "08.10.2016",
            "title": "Облако Свидетелей",
            "description": "",
            "lessons": [
              8,
              9,
              10
            ],
            "club_name": "",
            "full_cost": "0",
            "special_cost": null
          }
        ]
      }

   :query int page: page number (one of ``int`` or ``last``). default is 1
   :query int type: filter by ``summit_type_id``
   :reqheader Accept: the response content type depends on
                                :mailheader:`Accept` header
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 200: no error


.. http:get:: /api/v1.0/summit/(int:summit_id)/lessons/

   List of the lessons of ``Summit`` with ``id = summit_id``.

   **Example request**:

   .. sourcecode:: http

      GET /api/v1.0/summit/4/lessons/ HTTP/1.1
      Host: vocrm.org
      Accept: application/json

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept, Cookie
      Allow: GET,HEAD,OPTIONS
      Content-Type: application/json

      [
        {
          "summit": 4,
          "name": "1",
          "viewers": []
        },
        {
          "summit": 4,
          "name": "11",
          "viewers": []
        },
        {
          "summit": 4,
          "name": "111",
          "viewers": []
        }
      ]

   **Example response (Not Found)**:

   .. sourcecode:: http

      HTTP/1.1 404 Not Found
      Vary: Accept, Cookie
      Allow: GET,HEAD,OPTIONS
      Content-Type: application/json

      {
        "detail": "Не найдено."
      }

   :reqheader Accept: the response content type depends on
                                      :mailheader:`Accept` header
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 200: no error
   :statuscode 404: there's no summit


.. http:post:: /api/v1.0/summit/(int:summit_id)/add_lesson/

   Create new lesson for ``Summit`` with ``id = summit_id``.
   Name of the lesson must be unique for summit.

   **Example request**:

   .. sourcecode:: http

      POST /api/v1.0/summit/4/add_lesson/ HTTP/1.1
      Host: vocrm.org
      Accept: application/json
      content-type: application/x-www-form-urlencoded
      content-length: 10

      name=test4

   **Example response (Good request)**:

   .. sourcecode:: http

      HTTP/1.1 201 Created
      Vary: Accept, Cookie
      Allow: POST,OPTIONS
      Content-Type: application/json

      {
        "summit": 4,
        "name": "test4",
        "viewers": []
      }

   **Example response (Bad request 1)**:

   .. sourcecode:: http

      HTTP/1.1 400 Bad Request
      Vary: Accept, Cookie
      Allow: POST,OPTIONS
      Content-Type: application/json

      {
        "non_field_errors": [
          "Поля name, summit должны производить массив с уникальными значениями."
        ]
      }

   **Example response (Bad request 2)**:

   .. sourcecode:: http

      HTTP/1.1 400 Bad Request
      Vary: Accept, Cookie
      Allow: POST,OPTIONS
      Content-Type: application/json

      {
        "summit": [
          "Недопустимый первичный ключ "4" - объект не существует."
        ]
      }

   :form name: lesson name
   :reqheader Accept: the response content type depends on
                                            :mailheader:`Accept` header
   :reqheader Content-Type: one of ``application/x-www-form-urlencoded``,
                            ``application/json``, ``multipart/form-data``
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 201: lesson created
   :statuscode 400: bad request — summit don't exist or pair ``(summit, lesson.name)`` not unique
   :statuscode 404: there's no summit


.. http:get:: /api/v1.0/summit/(int:summit_id)/consultants/

   List of the consultants of ``Summit`` with ``id = summit_id``.

   **Example request**:

   .. sourcecode:: http

      GET /api/v1.0/summit/4/consultants/ HTTP/1.1
      Host: vocrm.org
      Accept: application/json

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept, Cookie
      Allow: GET,HEAD,OPTIONS
      Content-Type: application/json

      [
        {
          "id": 13659,
          "role": 20,
          "user": {
            "id": 13337,
            "fullname": "Ivanov Ivan Ivanovich"
          }
        },
        {
          "id": 13665,
          "role": 20,
          "user": {
            "id": 13350,
            "fullname": "Super Mario Brother"
          }
        }
      ]

   **Example response (Not Found)**:

   .. sourcecode:: http

      HTTP/1.1 404 Not Found
      Vary: Accept, Cookie
      Allow: GET,HEAD,OPTIONS
      Content-Type: application/json

      {
        "detail": "Не найдено."
      }

   :reqheader Accept: the response content type depends on
                                            :mailheader:`Accept` header
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 200: no error
   :statuscode 404: there's no summit


.. http:post:: /api/v1.0/summit/(int:summit_id)/add_consultant/

   Set visitor of ``Summit`` as ``Consultant`` on this summit.
   Only ``Supervisor`` of ``Summit`` can set consultants.

   **Example request**:

   .. sourcecode:: http

      POST /api/v1.0/summit/4/add_consultant/ HTTP/1.1
      Host: vocrm.org
      Accept: application/json
      content-type: application/x-www-form-urlencoded
      content-length: 14

      anket_id=13659

   **Example response (Good request)**:

   .. sourcecode:: http

      HTTP/1.1 201 Created
      Vary: Accept, Cookie
      Allow: POST,OPTIONS
      Content-Type: application/json

      {
        "consultant_id": "13659",
        "action": "added",
        "summit_id": 4
      }

   **Example response (Bad request 1)**:

   .. sourcecode:: http

      HTTP/1.1 400 Bad Request
      Vary: Accept, Cookie
      Allow: POST,OPTIONS
      Content-Type: application/json

      {
        "result": "Выбранная анкета не соответствует данному саммиту."
      }

   **Example response (Bad request 2)**:

   .. sourcecode:: http

      HTTP/1.1 404 Not Found
      Vary: Accept, Cookie
      Allow: POST,OPTIONS
      Content-Type: application/x-www-form-urlencoded

      {
        "detail": "Не найдено."
      }

   **Example response (Bad request 3)**:

   .. sourcecode:: http

      HTTP/1.1 403 Forbidden
      Vary: Accept, Cookie
      Allow: POST,OPTIONS
      Content-Type: application/x-www-form-urlencoded

      {
        "result": "У вас нет прав для добавления консультантов."
      }

   :form anket_id: visitor id
   :reqheader Accept: the response content type depends on
                                                  :http:header:`Accept` header
   :reqheader Content-Type: one of ``application/x-www-form-urlencoded``,
                            ``application/json``, ``multipart/form-data``
   :resheader Content-Type: this depends on :http:header:`Accept`
                            header of request
   :statuscode 201: created consultant
   :statuscode 404: there's no summit
   :statuscode 400: bad request — selected summit don't have anket with id = ``anket_id``
   :statuscode 403: current user is not ``Supervisor`` of this summit


.. http:post:: /api/v1.0/summit/(int:summit_id)/del_consultant/

   Set visitor of ``Summit`` as ``Visitor`` on this summit.
   Only ``Supervisor`` of ``Summit`` can delete consultants.

   **Example request**:

   .. sourcecode:: http

      POST /api/v1.0/summit/4/del_consultant/ HTTP/1.1
      Host: vocrm.org
      Accept: application/json
      content-type: application/x-www-form-urlencoded
      content-length: 14

      anket_id=13659

   **Example response (Good request)**:

   .. sourcecode:: http

      HTTP/1.1 201 Created
      Vary: Accept, Cookie
      Allow: POST,OPTIONS
      Content-Type: application/json

      {
        "consultant_id": "13659",
        "action": "removed",
        "summit_id": 4
      }

   **Example response (Bad request 1)**:

   .. sourcecode:: http

      HTTP/1.1 400 Bad Request
      Vary: Accept, Cookie
      Allow: POST,OPTIONS
      Content-Type: application/json

      {
        "result": "Выбранная анкета не соответствует данному саммиту."
      }

   **Example response (Bad request 2)**:

   .. sourcecode:: http

      HTTP/1.1 404 Not Found
      Vary: Accept, Cookie
      Allow: POST,OPTIONS
      Content-Type: application/x-www-form-urlencoded

      {
        "detail": "Не найдено."
      }

   **Example response (Bad request 3)**:

   .. sourcecode:: http

      HTTP/1.1 403 Forbidden
      Vary: Accept, Cookie
      Allow: POST,OPTIONS
      Content-Type: application/x-www-form-urlencoded

      {
        "result": "У вас нет прав для удаления консультантов."
      }

   :form anket_id: visitor id
   :reqheader Accept: the response content type depends on
                                                        :http:header:`Accept` header
   :reqheader Content-Type: one of ``application/x-www-form-urlencoded``,
                            ``application/json``, ``multipart/form-data``
   :resheader Content-Type: this depends on :http:header:`Accept`
                            header of request
   :statuscode 201: created consultant
   :statuscode 404: there's no summit
   :statuscode 400: bad request — selected summit don't have anket with id = ``anket_id``
   :statuscode 403: current user is not ``Supervisor`` of this summit

Create anket payment
~~~~~~~~~~~~~~~~~~~~

.. http:post:: /api/v1.0/summit_ankets/(int:anket_id)/create_payment/

   Create new payment for ``Summit Anket``.

   **Example request**:

   .. sourcecode:: http

      POST /api/v1.0/summit_ankets/4/create_payment/ HTTP/1.1
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

Pre delete information
~~~~~~~~~~~~~~~~~~~~~~

.. http:get:: /api/v1.0/summit_ankets/(int:anket_id)/predelete/

   **Example request**:

   .. sourcecode:: http

      GET /api/v1.0/summit_ankets/4/predelete/ HTTP/1.1
      Host: vocrm.org
      Accept: application/json
      content-type: application/json


   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept, Cookie
      Allow: GET,HEAD,OPTIONS
      Content-Type: application/json

        {
          "notes": [
            {
              "text": "После академии остался в Киеве администратором базы.",
              "owner": "User User User",
              "date_created": "2017-01-09T06:04:43.649649Z",
              "owner_name": "User User User"
            },
            {
              "text": "Был ответственным за второй этаж. Так же очень сильно помогал по администрации базы.",
              "owner": "User User User",
              "date_created": "2017-01-09T00:45:01.266451Z",
              "owner_name": "User User User"
            }
          ],
          "lessons": [
            {
              "summit": 3,
              "name": "Урок 1"
            },
            {
              "summit": 3,
              "name": "Урок 2"
            },
            {
              "summit": 3,
              "name": "Урок 3"
            }
          ],
          "summits": [
            {
              "id": 1,
              "start_date": "04.07.2016",
              "end_date": "29.07.2016",
              "title": "Колледж",
              "description": "2016"
            }
          ],
          "users": [
            {
              "id": 11,
              "user": {
                "id": 2266,
                "email": "mail@gmail.com",
                "first_name": "Lol",
                "last_name": "Ahahah",
                "middle_name": "Blablabla",
                "search_name": "",
                "facebook": "",
                "vkontakte": "",
                "odnoklassniki": "",
                "skype": "",
                "description": "",
                "phone_number": "+3809999999",
                "extra_phone_numbers": null,
                "born_date": "13.05.1967",
                "coming_date": "31.05.2016",
                "repentance_date": null,
                "country": "Украина",
                "region": "Днепропетровская область",
                "city": "Днепропетровск",
                "district": "",
                "address": " ",
                "image": "/media/images/blob_HDYR9ag",
                "image_source": "/media/images/photo_dIGuVIt.jpg",
                "departments": [
                  {
                    "id": 6,
                    "title": "Днепр"
                  }
                ],
                "master": {
                  "id": 2248,
                  "fullname": "Iam Super Master"
                },
                "hierarchy": {
                  "id": 3,
                  "title": "Сотник",
                  "level": 2
                },
                "divisions": [],
                "partnership": {
                  "value": "1500",
                  "responsible": 117,
                  "date": "13.10.2016",
                  "user": 2246,
                  "currency": 2,
                  "is_active": true
                },
                "fullname": "Ahahah Lol Blablabla",
                "spiritual_level": "Младенец"
              },
              "code": "3000003",
              "description": "",
              "visited": false
            }
          ],
          "consultants": [
            {
              "id": 11,
              "user": {
                "id": 2266,
                "email": "blank@gmail.com",
                "first_name": "Lol",
                "last_name": "Ahahah",
                "middle_name": "Blablabla",
                "search_name": "",
                "facebook": "",
                "vkontakte": "",
                "odnoklassniki": "",
                "skype": "",
                "description": "",
                "phone_number": "+3809999999",
                "extra_phone_numbers": null,
                "born_date": "13.05.1967",
                "coming_date": "31.05.2016",
                "repentance_date": null,
                "country": "Украина",
                "region": "Днепропетровская область",
                "city": "Днепропетровск",
                "district": "",
                "address": " ",
                "image": "/media/images/blob_HDYR9ag",
                "image_source": "/media/images/photo_dIGuVIt.jpg",
                "departments": [
                  {
                    "id": 6,
                    "title": "Днепр"
                  }
                ],
                "master": {
                  "id": 2248,
                  "fullname": "Iam Super Master"
                },
                "hierarchy": {
                  "id": 3,
                  "title": "Сотник",
                  "level": 2
                },
                "divisions": [],
                "partnership": {
                  "value": "1500",
                  "responsible": 117,
                  "date": "13.10.2016",
                  "user": 2246,
                  "currency": 2,
                  "is_active": true
                },
                "fullname": "Ahahah Lol Blablabla",
                "spiritual_level": "Младенец"
              },
              "code": "3000003",
              "description": "",
              "visited": false
            }
          ]
        }


   **Example response (Not Found)**:

   .. sourcecode:: http

      HTTP/1.1 404 Not Found
      Vary: Accept, Cookie
      Allow: GET,HEAD,OPTIONS
      Content-Type: application/json

      {
        "detail": "Не найдено."
      }

   :statuscode 200: no error
   :statuscode 404: there's no summit profile


Delete summit profile
~~~~~~~~~~~~~~~~~~~~~

.. http:delete:: /api/v1.0/summit_ankets/(int:anket_id)/

    Delete summit profile with ``id = anket_id``

    **Example request**:

    .. sourcecode:: http

        DELETE /api/v1.0/summit_ankets/6/ HTTP/1.1
        Host: vocrm.org
        Accept: application/json
        content-type: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 204 No Content
        Vary: Accept, Cookie
        Allow: PATCH,DELETE,OPTIONS
        Content-Type: application/json

    **Example response (user have payments)**:

    .. sourcecode:: http

        HTTP/1.1 400 Bad Request
        Vary: Accept, Cookie
        Allow: PATCH,DELETE,OPTIONS
        Content-Type: application/json

        {
          "detail": "Summit profile has payments. Please, remove them before deleting profile.",
          "payments": [
            {
              "id": "7496",
              "url": "http://crm.local:8000/api/v1.0/payments/7496/detail/",
              "sum": "100",
              "effective_sum": "100.000",
              "sum_str": "100 грн.",
              "effective_sum_str": "100.000 грн.",
              "operation": "*",
              "currency_sum": {
                "id": "2",
                "name": "Гривна",
                "code": "uah",
                "short_name": "грн.",
                "symbol": "₴"
              },
              "currency_rate": {
                "id": "2",
                "name": "Гривна",
                "code": "uah",
                "short_name": "грн.",
                "symbol": "₴"
              },
              "rate": "1.000",
              "description": "",
              "created_at": "03.07.2016 21:00",
              "sent_date": "04.07.2016",
              "manager": "None",
              "purpose": "/api/v1.0/summit_ankets/3439/"
            }
          ]
        }

    **Example response (profile does not exist)**:

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

    :statuscode 204: profile deleted
    :statuscode 400: profile have payments
    :statuscode 404: profile does not exist
    :statuscode 403: user does not permissions for delete profile
