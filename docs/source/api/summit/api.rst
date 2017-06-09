===============
Summit REST API
===============

Summit
------


Info by summit
~~~~~~~~~~~~~~

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

   :statuscode 200: no error
   :statuscode 404: there's no summit


PDF report by participant of the summit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. http:get:: /api/v1.0/summit/(int:summit_id)/master/(int:master_id).pdf

   Information about ``Summit`` with id = ``summit_id``.

   **Example request**:

   .. sourcecode:: http

      GET /api/v1.0/summit/4/master/13.pdf?date=2042-02-04&attended=false&short HTTP/1.1
      Host: vocrm.org
      Accept: application/json

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept, Cookie
      Allow: GET,HEAD,OPTIONS
      Content-Type: "application/pdf"
      Content-Disposition: "attachment;"

        ... body ...

   **Example response (Not Found)**:

   .. sourcecode:: http

      HTTP/1.1 404 Not Found
      Vary: Accept, Cookie
      Allow: GET,HEAD,OPTIONS
      Content-Type: application/json

      {
        "detail": "Не найдено."
      }

   **Example response (Bad request)**:

   .. sourcecode:: http

      HTTP/1.1 400 Bad Request
      Allow: OPTIONS, GET
      Content-Type: application/json
      Vary: Accept

      [
          "Invalid date."
      ]

   .. sourcecode:: http

      HTTP/1.1 403 Forbidden
      Allow: OPTIONS, GET
      Content-Type: application/json
      Vary: Accept

      {
          "detail": "You do not have permission to download report. "
      }

   :query string date: report date, format: ``YYYY-mm-dd``
   :query string attended: filter users by attended, one of (
         [``True``, ``true``, ``TRUE``, ``t``, ``yes``, ``Yes`` , ``YES``, ``1``] or
         [``False``, ``false``, ``FALSE``, ``f``, ``no``, ``No`` , ``NO``, ``0``])
   :query string short: if exist -> without break page

   :statuscode 200: no error
   :statuscode 400: bad request
   :statuscode 404: there's no master



List of summits
~~~~~~~~~~~~~~~

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

   :statuscode 200: no error


List of summit profiles
~~~~~~~~~~~~~~~~~~~~~~~

.. http:get:: /api/v1.0/summits/(int:summit_id)/users/

   List of users of summit (order by ``last_name``). Pagination by 30 profiles per page.

   **Example request**:

   .. sourcecode:: http

      GET /api/v1.0/summits/2/users/ HTTP/1.1
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
          "next": "http://crm.local:8000/api/v1.0/summits/7/users/?page=2",
          "previous": null
        },
        "count": 2565,
        "user_table": {
          "full_name": {
            "id": 1260620,
            "title": "ФИО",
            "ordering_title": "last_name",
            "number": 1,
            "active": true,
            "editable": true
          },
          "responsible": {
            "id": 1260621,
            "title": "Ответственный",
            "ordering_title": "responsible",
            "number": 2,
            "active": true,
            "editable": true
          },
          "spiritual_level": {
            "id": 1260622,
            "title": "Духовный уровень",
            "ordering_title": "spiritual_level",
            "number": 3,
            "active": true,
            "editable": true
          },
          "divisions_title": {
            "id": 1260623,
            "title": "Отдел церкви",
            "ordering_title": "divisions_title",
            "number": 4,
            "active": true,
            "editable": true
          },
          "department": {
            "id": 1260624,
            "title": "Отдел",
            "ordering_title": "department",
            "number": 5,
            "active": true,
            "editable": true
          },
          "hierarchy_title": {
            "id": 1260625,
            "title": "Иерархия",
            "ordering_title": "hierarchy__level",
            "number": 6,
            "active": true,
            "editable": true
          },
          "phone_number": {
            "id": 1260626,
            "title": "Номер телефона",
            "ordering_title": "user__phone_number",
            "number": 7,
            "active": true,
            "editable": true
          },
          "email": {
            "id": 1260627,
            "title": "Email",
            "ordering_title": "user__email",
            "number": 8,
            "active": true,
            "editable": true
          },
          "social": {
            "id": 1260628,
            "title": "Социальные сети",
            "ordering_title": "user__facebook",
            "number": 9,
            "active": true,
            "editable": true
          },
          "country": {
            "id": 1260629,
            "title": "Страна",
            "ordering_title": "country",
            "number": 10,
            "active": true,
            "editable": true
          },
          "city": {
            "id": 1260630,
            "title": "Населенный пункт",
            "ordering_title": "city",
            "number": 11,
            "active": true,
            "editable": true
          },
          "region": {
            "id": 1260631,
            "title": "Область",
            "ordering_title": "user__region",
            "number": 12,
            "active": true,
            "editable": true
          },
          "district": {
            "id": 1260632,
            "title": "Район",
            "ordering_title": "user__district",
            "number": 13,
            "active": true,
            "editable": true
          },
          "address": {
            "id": 1260633,
            "title": "Адрес",
            "ordering_title": "user__address",
            "number": 14,
            "active": true,
            "editable": true
          },
          "born_date": {
            "id": 1260634,
            "title": "Дата рождения",
            "ordering_title": "user__born_date",
            "number": 15,
            "active": true,
            "editable": true
          },
          "repentance_date": {
            "id": 1260635,
            "title": "Дата Покаяния",
            "ordering_title": "user__repentance_date",
            "number": 16,
            "active": true,
            "editable": true
          },
          "code": {
            "id": 1260636,
            "title": "Код",
            "ordering_title": "code",
            "number": 17,
            "active": true,
            "editable": true
          },
          "value": {
            "id": 1260637,
            "title": "Оплата",
            "ordering_title": "value",
            "number": 18,
            "active": true,
            "editable": true
          },
          "description": {
            "id": 1260638,
            "title": "Примечание",
            "ordering_title": "description",
            "number": 19,
            "active": true,
            "editable": true
          }
        },
        "common_table": {},
        "results": [
          {
            "id": 20083,
            "full_name": "User First Name",
            "responsible": "I Am Master",
            "spiritual_level": "Младенец",
            "divisions_title": "",
            "department": "Дочерняя Церковь",
            "hierarchy_title": "Прихожанин",
            "phone_number": "+37066666666",
            "email": "start@end.com",
            "social": ["http://facebook.com/user", "http://vk.com/user", "http://ok.com/user", "skype_user"],
            "country": "Литва",
            "city": "Kretingsodis",
            "region": "Kretingos rajonas",
            "district": "",
            "address": "",
            "born_date": null,
            "repentance_date": null,
            "code": "04020083",
            "value": "0",
            "description": "",
            "emails": [],
            "visited": false,
            "ticket_status": {"none": "Without ticket."},
            "link": "/summits/profile/20083/",
            "total_sum": "0"
          },
          {
            "id": 20489,
            "full_name": "Last Man Super",
            "responsible": "I Am Master",
            "spiritual_level": "Младенец",
            "divisions_title": "",
            "department": "Дочерняя Церковь",
            "hierarchy_title": "Прихожанин",
            "phone_number": "+45222222222",
            "email": "user@mail.com",
            "social": ",,,",
            "country": "Дания",
            "city": "",
            "region": "",
            "district": "",
            "address": "",
            "born_date": "2003-03-29",
            "repentance_date": null,
            "code": "04020489",
            "value": "0",
            "description": "",
            "emails": [],
            "visited": false,
            "ticket_status": {"print": "Ticket is printed."},
            "link": "/summits/profile/20489/",
            "total_sum": "0"
          }
        ]
      }

   :query int page: page number (one of ``int`` or ``last``). default is 1
   :query int hierarchy: filter by ``hierarchy_id``
   :query int master: filter by ``master_id``, returned children of master
   :query int master_tree: filter by ``master_id``, returned descendants of master and self master
   :query int department: filter by ``department_id``
   :query int ticket_status: filter by ``ticket_status`` (one of ``none``, ``download``, ``print``)
   :query string search_fio: search by ``last_name``, ``first_name``, ``middle_name``, ``search_name``
   :query string search_email: search by ``email``
   :query string search_phone_number: search by main ``phone_number``
   :query string search_country: search by ``country``
   :query string search_city: search by ``city``

   :statuscode 200: no error


Export summit profiles
~~~~~~~~~~~~~~~~~~~~~~

.. http:post:: /api/v1.0/summits/(int:summit_id)/export_users/

    Export profiles.

    **Example request**:

    .. sourcecode:: http

        POST /api/v1.0/summits/13/export_users/ HTTP/1.1
        Host: vocrm.org
        content-type: application/x-www-form-urlencoded
        content-length: 33

          fields=id,last_name,city&ids=1,135

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept, Cookie
        Allow: POST,OPTIONS
        Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
        Content-Disposition: attachment; filename=SummitAnket-2016-12-20.xlsx

        ... body ...

    *SummitAnket-2016-12-20.xlsx content*

    +-----+-----------+------+
    | id  | last_name | city |
    +=====+===========+======+
    | 1   | Gates     | Rio  |
    +-----+-----------+------+
    | 135 | Torvalds  | Kiev |
    +-----+-----------+------+

    :form fields: field names for export (comma-separated), optional. Default is (
                   ``last_name``, ``first_name``, ``middle_name``,
                   ``email``, ``phone_number``, ``skype``,
                   ``country``, ``city``, ``address``, ``region``,
                   ``departments``, ``hierarchy``, ``master``, ``spiritual_level``, ``divisions``, ``fullname``
                   ``born_date``, ``facebook``, ``vkontakte``, ``description``, ``code``)
    :form ids: user ids for export (comma-separated), optional.
                         If ``ids`` is empty then will be used filter by query parameters.

    .. important:: **Query Parameters** used only if ids is empty

    :query int hierarchy: filter by ``hierarchy_id``
    :query int master: filter by ``master_id``, returned children of master
    :query int master_tree: filter by ``master_id``, returned descendants of master and self master
    :query int department: filter by ``department_id``
    :query int ticket_status: filter by ``ticket_status`` (one of ``none``, ``download``, ``print``)
    :query string search_fio: search by ``last_name``, ``first_name``, ``middle_name``, ``search_name``
    :query string search_email: search by ``email``
    :query string search_phone_number: search by main ``phone_number``
    :query string search_country: search by ``country``
    :query string search_city: search by ``city``

    :reqheader Content-Type: one of ``application/x-www-form-urlencoded``,
                             ``application/json``, ``multipart/form-data``

    :statuscode 200: success export


List of summit lessons
~~~~~~~~~~~~~~~~~~~~~~

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

   :statuscode 200: no error
   :statuscode 404: there's no summit



Add new summit lesson
~~~~~~~~~~~~~~~~~~~~~

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
   :reqheader Content-Type: one of ``application/x-www-form-urlencoded``,
                            ``application/json``, ``multipart/form-data``
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
   :reqheader Content-Type: one of ``application/x-www-form-urlencoded``,
                            ``application/json``, ``multipart/form-data``
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
   :reqheader Content-Type: one of ``application/x-www-form-urlencoded``,
                            ``application/json``, ``multipart/form-data``
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


List of profile payments
~~~~~~~~~~~~~~~~~~~~~~~~

.. http:get:: /api/v1.0/summit_ankets/(int:profile_id)/payments/

   List of the payments of ``SummitAnket`` with ``id = profile_id``.

   **Example request**:

   .. sourcecode:: http

      GET /api/v1.0/summit_ankets/4/payments/ HTTP/1.1
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
          "id": 16084,
          "sum": "222",
          "effective_sum": "111.000",
          "sum_str": "222 грн.",
          "effective_sum_str": "111.000 грн.",
          "operation": "/",
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
          "rate": "2.000",
          "description": "",
          "created_at": "03.05.2017 14:18",
          "sent_date": "03.05.2017",
          "manager": {
            "id": 13885,
            "first_name": "Амир",
            "last_name": "Азиев",
            "middle_name": ""
          },
          "purpose": "/api/v1.0/summit_ankets/269/"
        },
        {
          "id": 6442,
          "sum": "100",
          "effective_sum": "100.000",
          "sum_str": "100 грн.",
          "effective_sum_str": "100.000 грн.",
          "operation": "*",
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
          "created_at": "03.07.2016 21:00",
          "sent_date": "04.07.2016",
          "manager": null,
          "purpose": "/api/v1.0/summit_ankets/269/"
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

   :statuscode 200: no error
         :statuscode 404: there's no summit

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
