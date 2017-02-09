================
Account REST API
================

CustomUser
----------


.. http:get:: /api/v1.1/users/

   List of the users for table (order by ``last_name``, ``first_name``, ``middle_name``).
   Pagination by 30 users per page. Filtered only active users.

   **Example request**:

   .. sourcecode:: http

      GET /api/v1.1/users/ HTTP/1.1
      Host: vocrm.org
      Accept: application/json

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept, Cookie
      Allow: GET,POST,HEAD,OPTIONS
      Content-Type: application/json

      {
        "results": [
          {
            "id": 2305,
            "link": "/account/2305/",
            "fullname": "Example User Name",
            "master": {
              "id": 2251,
              "fullname": "My Super Master"
            },
            "department": {
              "id": 8,
              "title": "Интернет ячейки"
            },
            "email": "example@email.com",
            "phone_number": "+3732222222",
            "born_date": null,
            "hierarchy": {
              "id": 4,
              "title": "Пастор"
            },
            "country": "Молдова",
            "region": "",
            "city": "Кишинев",
            "district": "",
            "address": " ",
            "divisions": [],
            "facebook": "",
            "vkontakte": "",
            "odnoklassniki": "",
            "skype": "laskype",
            "image": "http://crm.local:8000/media/images/blob_fTWYRTl",
            "image_source": "http://crm.local:8000/media/images/photo_TbioT0s.jpg"
          },
          {
            "id": 2303,
            "link": "/account/2303/",
            "fullname": "Other User Name",
            "master": {
              "id": 2251,
              "fullname": "My Super Master"
            },
            "department": {
              "id": 8,
              "title": "Интернет ячейки"
            },
            "email": "other@example.com",
            "phone_number": "+37333333333",
            "born_date": null,
            "hierarchy": {
              "id": 4,
              "title": "Пастор"
            },
            "country": "Молдова",
            "region": " ",
            "city": "",
            "district": "",
            "address": " ",
            "divisions": [],
            "facebook": "",
            "vkontakte": "",
            "odnoklassniki": "",
            "skype": "artur100566",
            "image": "http://crm.local:8000/media/images/blob_KRJoAqk",
            "image_source": "http://crm.local:8000/media/images/photo_n29qq0W.jpg"
          }
        ],
        "count": 2,
        "user_table": {
          "fullname": {
            "id": 196729,
            "title": "ФИО",
            "ordering_title": "last_name",
            "number": 1,
            "active": true,
            "editable": false
          },
          "master": {
            "id": 196737,
            "title": "Ответственный",
            "ordering_title": "master__last_name",
            "number": 2,
            "active": true,
            "editable": true
          },
          "department": {
            "id": 196728,
            "title": "Отдел",
            "ordering_title": "department__title",
            "number": 3,
            "active": true,
            "editable": true
          },
          "email": {
            "id": 196724,
            "title": "Email",
            "ordering_title": "email",
            "number": 4,
            "active": true,
            "editable": true
          },
          "phone_number": {
            "id": 196725,
            "title": "Номер телефона",
            "ordering_title": "phone_number",
            "number": 5,
            "active": true,
            "editable": true
          },
          "born_date": {
            "id": 196726,
            "title": "Дата рождения",
            "ordering_title": "born_date",
            "number": 6,
            "active": true,
            "editable": true
          },
          "hierarchy": {
            "id": 196727,
            "title": "Иерархия",
            "ordering_title": "hierarchy__level",
            "number": 7,
            "active": true,
            "editable": true
          },
          "country": {
            "id": 196730,
            "title": "Страна",
            "ordering_title": "country",
            "number": 8,
            "active": true,
            "editable": true
          },
          "region": {
            "id": 196731,
            "title": "Область",
            "ordering_title": "region",
            "number": 9,
            "active": true,
            "editable": true
          },
          "city": {
            "id": 196732,
            "title": "Населенный пункт",
            "ordering_title": "city",
            "number": 10,
            "active": true,
            "editable": true
          },
          "district": {
            "id": 196733,
            "title": "Район",
            "ordering_title": "district",
            "number": 11,
            "active": true,
            "editable": true
          },
          "address": {
            "id": 196734,
            "title": "Адрес",
            "ordering_title": "address",
            "number": 12,
            "active": true,
            "editable": true
          },
          "social": {
            "id": 196735,
            "title": "Социальные сети",
            "ordering_title": "facebook",
            "number": 13,
            "active": true,
            "editable": true
          },
          "divisions": {
            "id": 196736,
            "title": "Отдел церкви",
            "ordering_title": "divisions",
            "number": 14,
            "active": true,
            "editable": true
          }
        },
        "links": {
          "next": null,
          "previous": null
        }
      }

   :query int page: page number (one of ``int`` or ``last``). default is 1
   :query int hierarchy: filter by ``hierarchy_id``
   :query int master: filter by ``master_id``
   :query int department: filter by ``department_id``
   :query int page_size: page size, default is 30
   :query string search_fio: search by ``last_name``, ``first_name``, ``middle_name``, ``search_name``
   :query string search_email: search by ``email``
   :query string search_phone_number: search by main ``phone_number``
   :query string search_country: search by ``country``
   :query string search_city: search by ``city``
   :query string ordering: order by one of ``first_name``, ``last_name``, ``middle_name``,
                       ``born_date``, ``country``, ``region``, ``city``, ``disrict``,
                       ``address``, ``skype``,
                       ``phone_number``, ``email``, ``hierarchy__level``, ``department__title``,
                       ``facebook``, ``vkontakte``, ``hierarchy_order``, ``master__last_name``

   :reqheader Accept: the response content type depends on
                                      :mailheader:`Accept` header
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 200: no error

.. http:post:: /api/v1.1/users/

   Create new user.

   **Example request**:

   .. sourcecode:: http

      POST /api/v1.1/users/13350/ HTTP/1.1
      Host: vocrm.org
      Accept: application/json
      content-type: application/json
      content-length: 661

      {
        "email": "example@email.com",
        "first_name": "first",
        "last_name": "last",
        "middle_name": "middle",
        "search_name": "search",
        "facebook": "http://fb.com/test",
        "vkontakte": "http://vk.com/test",
        "odnoklassniki": "http://ok.com/test",
        "skype": "skype",
        "extra_phone_numbers": ["26426264"],
        "born_date": "2000-02-20",
        "coming_date": "2002-02-20",
        "repentance_date": "2020-02-22",
        "country": "C",
        "region": "R",
        "city": "City",
        "district": "D",
        "address": "A",
        "department": 1,
        "hierarchy": 1,
        "master": 1,
        "divisions": [1,2,3],
        "phone_number": "573135171",
        "partner": {
          "value": 30,
          "responsible": 4,
          "date": "2020-02-20"
        }
      }

   **Example response (Good request)**:

   .. sourcecode:: http

      HTTP/1.1 201 Created
      Vary: Accept, Cookie
      Allow: GET, POST, HEAD, OPTIONS
      Content-Type: application/json

      {
        "id": 15183,
        "email": "example@email.com",
        "first_name": "first",
        "last_name": "last",
        "middle_name": "middle",
        "search_name": "search",
        "facebook": "http://fb.com/test",
        "vkontakte": "http://vk.com/test",
        "odnoklassniki": "http://ok.com/test",
        "skype": "skype",
        "phone_number": "573135171",
        "extra_phone_numbers": [
            "26426264"
        ],
        "born_date": "20.02.2000",
        "coming_date": "20.02.2002",
        "repentance_date": "22.02.2020",
        "country": "C",
        "region": "R",
        "city": "City",
        "district": "D",
        "address": "A",
        "image": null,
        "image_source": null,
        "department": 1,
        "master": 1,
        "hierarchy": 1,
        "divisions": [
          1,
          2,
          3
        ],
        "partnership": {
          "value": 30,
          "responsible": 4,
          "date": "20.02.2020",
          "user": 15183
        },
        "fullname": "last first middle"
      }

   **Example response (Bad request 1)**:

   .. sourcecode:: http

      HTTP/1.1 403 Forbidden
      Vary: Accept, Cookie
      Allow: GET, POST, HEAD, OPTIONS
      Content-Type: application/json

      {
        "detail": "Учетные данные не были предоставлены."
      }

   **Example response (Bad request 2)**:

   .. sourcecode:: http

      HTTP/1.1 400 Bad Request
      Vary: Accept, Cookie
      Allow: GET, POST, HEAD, OPTIONS
      Content-Type: application/json

      {
        "first_name": [
          "Это поле обязательно."
        ]
      }

   :form email: user email
   :form first_name: first name, **required**
   :form last_name: last name, **required**
   :form middle_name: middle name
   :form search_name: search name
   :form facebook: facebook url
   :form vkontakte: vkontakte url
   :form odnoklassniki: odnoklassiniki url
   :form skype: login of skype
   :form phone_number: phone number, **required**
   :form extra_phone_numbers: additional phone numbers
   :form born_date: born date
   :form coming_date: coming date
   :form repentance_date: repentance date
   :form country: country
   :form city: city
   :form region: region
   :form district: district
   :form address: address
   :form image: user photo
   :form department: id of user department, **required**
   :form hierarchy: id of hierarchy, **required**
   :form master: id of master, **required**
   :form divisions: list of ids of divisions
   :form partner: dict of partnership fields
   :form partner[value]: sum of partner's contribution
   :form partner[responsible]: responsible of partner
   :form partner[date]: date when the user became a partner
   :reqheader Accept: the response content type depends on
                                                              :mailheader:`Accept` header
   :reqheader Content-Type: one of ``application/x-www-form-urlencoded``,
                            ``application/json``, ``multipart/form-data``
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 201: success create
   :statuscode 403: user is not authenticated
   :statuscode 400: bad request


.. http:put:: /api/v1.1/users/<user_id>/

   Update of user with ``id = user_id``.

   **Example request**:

   .. sourcecode:: http

      PUT /api/v1.1/users/13350/ HTTP/1.1
      Host: vocrm.org
      Accept: application/json
      content-type: application/json
      content-length: 661

      {
        "email": "example@email.com",
        "first_name": "first",
        "last_name": "last",
        "middle_name": "middle",
        "search_name": "search",
        "facebook": "http://fb.com/test",
        "vkontakte": "http://vk.com/test",
        "odnoklassniki": "http://ok.com/test",
        "skype": "skype",
        "extra_phone_numbers": ["26426264"],
        "born_date": "2000-02-20",
        "coming_date": "2002-02-20",
        "repentance_date": "2020-02-22",
        "country": "C",
        "region": "R",
        "city": "City",
        "district": "D",
        "address": "A",
        "department": 1,
        "hierarchy": 1,
        "master": 1,
        "divisions": [1,2,3],
        "phone_number": "573135171",
        "partner": {
          "value": 30,
          "responsible": 4,
          "date": "2020-02-20"
        }
      }

   **Example response (Good request)**:

   .. sourcecode:: http

      HTTP/1.1 201 Created
      Vary: Accept, Cookie
      Allow: GET, PUT, PATCH, DELETE, HEAD, OPTIONS
      Content-Type: application/json

      {
        "id": 15183,
        "email": "example@email.com",
        "first_name": "first",
        "last_name": "last",
        "middle_name": "middle",
        "search_name": "search",
        "facebook": "http://fb.com/test",
        "vkontakte": "http://vk.com/test",
        "odnoklassniki": "http://ok.com/test",
        "skype": "skype",
        "phone_number": "573135171",
        "extra_phone_numbers": [
            "26426264"
        ],
        "born_date": "20.02.2000",
        "coming_date": "20.02.2002",
        "repentance_date": "22.02.2020",
        "country": "C",
        "region": "R",
        "city": "City",
        "district": "D",
        "address": "A",
        "image": null,
        "image_source": null,
        "department": 1,
        "master": 1,
        "hierarchy": 1,
        "divisions": [
          1,
          2,
          3
        ],
        "partnership": {
          "value": 30,
          "responsible": 4,
          "date": "20.02.2020",
          "user": 15183
        },
        "fullname": "last first middle"
      }

   **Example response (Bad request 1)**:

   .. sourcecode:: http

      HTTP/1.1 403 Forbidden
      Vary: Accept, Cookie
      Allow: GET, PUT, PATCH, DELETE, HEAD, OPTIONS
      Content-Type: application/json

      {
        "detail": "Учетные данные не были предоставлены."
      }

   **Example response (Bad request 2)**:

   .. sourcecode:: http

      HTTP/1.1 400 Bad Request
      Vary: Accept, Cookie
      Allow: GET, PUT, PATCH, DELETE, HEAD, OPTIONS
      Content-Type: application/json

      {
        "first_name": [
          "Это поле обязательно."
        ]
      }

   :form email: user email
   :form first_name: first name, **required**
   :form last_name: last name, **required**
   :form middle_name: middle name
   :form search_name: search name
   :form facebook: facebook url
   :form vkontakte: vkontakte url
   :form odnoklassniki: odnoklassiniki url
   :form skype: login of skype
   :form phone_number: phone number, **required**
   :form extra_phone_numbers: additional phone numbers
   :form born_date: born date
   :form coming_date: coming date
   :form repentance_date: repentance date
   :form country: country
   :form city: city
   :form region: region
   :form district: district
   :form address: address
   :form image: user photo
   :form department: id of user department, **required**
   :form hierarchy: id of hierarchy, **required**
   :form master: id of master, **required**
   :form divisions: list of ids of divisions
   :form partner: dict of partnership fields
   :form partner[value]: sum of partner's contribution
   :form partner[responsible]: responsible of partner
   :form partner[date]: date when the user became a partner
   :reqheader Accept: the response content type depends on
                                                        :mailheader:`Accept` header
   :reqheader Content-Type: one of ``application/x-www-form-urlencoded``,
                            ``application/json``, ``multipart/form-data``
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 201: success create
   :statuscode 403: user is not authenticated
   :statuscode 400: bad request


.. http:patch:: /api/v1.1/users/(int:user_id)/

   Partial update user data.

   **Example request**:

   .. sourcecode:: http

      PATCH /api/v1.1/users/13350/ HTTP/1.1
      Host: vocrm.org
      Accept: application/json
      content-type: application/x-www-form-urlencoded
      content-length: 47

      first_name=new&last_name=name&middle_name=other

   **Example response (Good request)**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept, Cookie
      Allow: GET, PUT, PATCH, DELETE, HEAD, OPTIONS
      Content-Type: application/json

      {
        "id": 13350,
        "email": "old@email.com",
        "first_name": "new",
        "last_name": "name",
        "middle_name": "other",
        "facebook": "fb",
        "vkontakte": "vk",
        "odnoklassniki": "ok",
        "skype": "iskype",
        "phone_number": "+3846266646",
        "extra_phone_numbers": [
            "+3843333338"
        ],
        "born_date": "08.11.2016",
        "coming_date": "01.12.2016",
        "repentance_date": "02.12.2016",
        "country": "Италия",
        "region": "Regione Autonoma Friuli Venezia Giulia",
        "city": "Adria",
        "district": "",
        "address": " address",
        "image": "http://vocrm.org/media/images/blob_khTQWMg",
        "image_source": "http://vocrm.org/media/images/photo_foIDR7k.jpg",
        "department": 4,
        "master": 11021,
        "hierarchy": 2,
        "divisions": [
          6,
          4
        ],
        "partnership": {
          "id": 3810,
          "value": 255,
          "responsible": 1
        },
        "fullname": "name new other"
      }

   **Example response (Bad request 1)**:

   .. sourcecode:: http

      HTTP/1.1 403 Forbidden
      Vary: Accept, Cookie
      Allow: GET, PUT, PATCH, DELETE, HEAD, OPTIONS
      Content-Type: application/json

      {
        "detail": "Учетные данные не были предоставлены."
      }

   **Example response (Bad request 2)**:

   .. sourcecode:: http

      HTTP/1.1 404 Not Found
      Vary: Accept, Cookie
      Allow: GET, PUT, PATCH, DELETE, HEAD, OPTIONS
      Content-Type: application/json

      {
        "detail": "Не найдено."
      }

   :form email: user email
   :form first_name: first name
   :form last_name: last name
   :form middle_name: middle name
   :form search_name: search name
   :form facebook: facebook url
   :form vkontakte: vkontakte url
   :form odnoklassniki: odnoklassiniki url
   :form skype: login of skype
   :form phone_number: phone number
   :form extra_phone_numbers: additional phone numbers
   :form born_date: born date
   :form coming_date: coming date
   :form repentance_date: repentance date
   :form country: country
   :form city: city
   :form district: district
   :form address: address
   :form image: user photo
   :form department: id of user department
   :form hierarchy: id of hierarchy
   :form master: id of master
   :reqheader Accept: the response content type depends on
                                                  :mailheader:`Accept` header
   :reqheader Content-Type: one of ``application/x-www-form-urlencoded``,
                            ``application/json``, ``multipart/form-data``
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 200: success update
   :statuscode 403: user is not authenticated
   :statuscode 404: there's no summit


.. http:post:: /api/v1.1/users/export/

   Export user data.

   **Example request**:

   .. sourcecode:: http

      POST /api/v1.1/users/export/ HTTP/1.1
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
      Content-Disposition: attachment; filename=CustomUser-2016-12-20.xlsx

      ... body ...

   *CustomUser-2016-12-20.xlsx content*

   +-----+-----------+------+
   | id  | last_name | city |
   +=====+===========+======+
   | 1   | Gates     | Rio  |
   +-----+-----------+------+
   | 135 | Torvalds  | Kiev |
   +-----+-----------+------+

   :form fields: field names for export (comma-separated), optional. Default is (``id``, ``username``,
                  ``last_name``, ``first_name``, ``middle_name``,
                  ``email``, ``phone_number``, ``skype``,
                  ``country``, ``city``, ``address``,
                  ``department_title``, ``hierarchy_title``, ``master_name``,
                  ``born_date``, ``facebook``, ``vkontakte``, ``description``)
   :form ids: user ids for export (comma-separated), optional.
                  If ``ids`` is empty then will be used filter by query parameters.

   .. important:: **Query Parameters** used only if ids is empty

   :query int hierarchy: filter by ``hierarchy_id``
   :query int master: filter by ``master_id``
   :query int department: filter by ``department_id``
   :query string search_fio: search by ``last_name``, ``first_name``, ``middle_name``, ``search_name``
   :query string search_email: search by ``email``
   :query string search_phone_number: search by main ``phone_number``
   :query string search_country: search by ``country``
   :query string search_city: search by ``city``
   :reqheader Accept: the response content type depends on
                                                              :http:header:`Accept` header
   :reqheader Content-Type: one of ``application/x-www-form-urlencoded``,
                            ``application/json``, ``multipart/form-data``
   :resheader Content-Type: this depends on :http:header:`Accept`
                            header of request
   :statuscode 200: success export


.. http:get:: /api/v1.0/short_users/

   List of the users for select.

   **Example request**:

   .. sourcecode:: http

      GET /api/v1.0/short_users/?level_gte=4&level_lt=6 HTTP/1.1
      Host: vocrm.org
      Accept: application/json

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept, Cookie
      Allow: GET,POST,HEAD,OPTIONS
      Content-Type: application/json

      [
          {
              "id": 13891,
              "fullname": "Гарькавая Анна ",
              "hierarchy": {
                  "id": 5,
                  "title": "Ст. епископ",
                  "level": 5
              }
          },
          {
              "id": 12813,
              "fullname": "Раду Бронислав ",
              "hierarchy": {
                  "id": 5,
                  "title": "Епископ",
                  "level": 4
              }
          }
      ]

   :query int level_gt: filter by ``hierarchy__level`` -> ``user.hierarchy.level > level_gt``
   :query int level_gte: filter by ``hierarchy__level`` -> ``user.hierarchy.level >= level_gte``
   :query int level_lt: filter by ``hierarchy__level`` -> ``user.hierarchy.level < level_lt``
   :query int level_lte: filter by ``hierarchy__level`` -> ``user.hierarchy.level <= level_lte``
   :query int department: filter by ``department_id``
   :query string search: search by ``last_name``, ``first_name``, ``middle_name``

   :reqheader Accept: the response content type depends on
                                            :mailheader:`Accept` header
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 200: no error
