==============
Group REST API
==============

Church
------


.. http:get:: /api/v1.0/churches/

    List of Churches (order by ``opening_date``, ``id``).
    Displaying title of Church is  or ``get_title``.
    Pagination by 30 churches per page.

    **Example request**:

    .. sourcecode:: http

        GET /api/v1.0/churches HTTP/1.1
        Host: vocrm.org
        Accept: application/json

    **Example response (Good request)**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, POST, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "count": 2,
            "results": [
                {
                    "id": 6,
                    "opening_date": "12.01.2017",
                    "is_open": false,
                    "link": "/churches/6/",
                    "title": "Тествая Цервковь №1",
                    "get_title": "Тествая Цервковь №1",
                    "department": {
                        "id": 1,
                        "title": "Киев"
                    },
                    "pastor": {
                        "id": 15160,
                        "fullname": "П Ростислав С"
                    },
                    "country": "Украина",
                    "city": "КИЕВ",
                    "address": "Гарматная 55",
                    "phone_number": "093-222-22-22",
                    "website": "",
                    "count_groups": 2,
                    "count_users": 9
                },
                {
                    "id": 7,
                    "opening_date": "07.12.2016",
                    "is_open": true,
                    "link": "/churches/7/",
                    "title": "Тествая Цервковь №2",
                    "get_title": "Тествая Цервковь №2",
                    "department": {
                        "id": 1,
                        "title": "Киев"
                    },
                    "pastor": {
                        "id": 15160,
                        "fullname": "П Ростислав С"
                    },
                    "country": "Россия",
                    "city": "Москва",
                    "address": "Пушкина 1а",
                    "phone_number": "",
                    "website": "",
                    "count_groups": 0,
                    "count_users": 0
                }
            ]
            "links": {
                "previous": null,
                "next": null
            }
        }

    :query int page: page number (one of ``int`` or ``last``). default is 1
    :query int department: filter by ``department_id``
    :query int pastor: filter by ``pastor_id``
    :query int page_size: page size, default is 30
    :query string title: search by ``title``
    :query string country: search by ``country``
    :query string city: search by ``city``
    :query string is_open: search by ``is_open``
    :query string phone_number: search by ``phone_number``
    :query string ordering: order by one of ``title``, ``city``, ``department``, ``home_group``, ``is_open``,
                                            ``opening_date``, ``pastor``, ``phone_number``, ``title``, ``website``
                                            ``count_groups``, ``count_users``,

    **Example response(Bad request)**:

    .. sourcecode:: http

        HTTP/1.1 403 Forbidden
        Allow: GET, POST, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "detail": "Учетные данные не были предоставлены."
        }


    :statuscode 200: no error
    :statuscode 403: user is not authenticated

.. http:post:: /api/v1.0/churches/

    Create new church.
    Church pastor hierarchy level must be more then ``leader``.

    **Example request**:

    .. sourcecode:: http

        POST /api/v1.0/churches HTTP/1.1
        Host: vocrm.org
        Accept: application/json
        content-type: application/json

        {
            "opening_date": "2017-01-01",
            "is_open": false,
            "title": "Церковь №1",
            "department": 1,
            "pastor": 1,
            "country": "Украина",
            "city": "Киев",
            "address": "Крещатик 1",
            "phone_number": "050-123-45-67",
            "website": "http://google.com"
        }

    **Example response (Good request)**:

    .. sourcecode:: http

        HTTP/1.1 201 Created
        Allow: GET, POST, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "id": 14,
            "opening_date": "01.01.2017",
            "is_open": false,
            "link": "/churches/14/",
            "title": "Церковь №1",
            "get_title": "Церковь №1",
            "department": 1,
            "pastor": 1,
            "country": "Украина",
            "city": "Киев",
            "address": "Крещатик 1",
            "phone_number": "050-123-45-67",
            "website": "http://google.com"
        }

    **Example response (Bad request 1, with "required_field": null)**:

    .. sourcecode:: http

        HTTP/1.1 400 Bad Request
        Allow: GET, POST, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "department": [
                "Это поле не может быть null."
            ]
        }

    **Example response (Bad request 2)**:

    .. sourcecode:: http

        HTTP/1.1 400 Bad Request
        Allow: GET, POST, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "department": [
                "Это поле обязательно."
            ]
        }

    **Example response (Bad request3, with pastor hierarchy level < 2)**:

    .. sourcecode:: http

        HTTP/1.1 400 Bad Request
        Allow: GET, POST, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "pastor": [
                "Данный пользователь \"50\" - не может быть назначен пастором Церкви."
            ]
        }

    :form opening_date: the opening of the church date, **required**
    :form is_open: true or false
    :form title: title
    :form department: department id, **required**
    :form pastor: pastor id, **required**
    :form country: "", **required**
    :form city: city
    :form address: address
    :form phone_number: phone number
    :form website: web site

    :statuscode 201: success create
    :statuscode 400: bad request
    :statuscode 403: user is not authenticated


.. http:get:: /api/v1.0/churches/(int:<church_id>)/

    Detail information about ``Church`` with ``id`` = ``church_id``.

    **Example request**:

    .. sourcecode:: http

        GET /api/v1.0/churches/6 HTTP/1.1
        Host: vocrm.org
        Accept: application/json

    **Example response**

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, PUT, PATCH, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "id": 6,
            "opening_date": "01.01.2016",
            "is_open": true,
            "link": "/churches/6/",
            "title": "",
            "get_title": "Москва Аккаунт",
            "department": 1,
            "pastor": 5,
            "country": "Россия",
            "city": "Москва",
            "address": "Горького 55",
            "phone_number": "050-222-22-22",
            "website": ""
        }

    **Example response (Not Found)**:

    .. sourcecode:: http

        HTTP/1.1 403 Forbidden
        Allow: GET, PUT, PATCH, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "detail": "Учетные данные не были предоставлены."
        }

    **Example response (Not Found)**:

    .. sourcecode:: http

        HTTP/1.1 404 Not Found
        Allow: GET, PUT, PATCH, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "detail": "Не найдено."
        }

    :statuscode 200: no error
    :statuscode 403: user is not authenticated
    :statuscode 404: there's no church


.. http:put:: /api/v1.0/churches/(int:<church_id>)/
.. http:patch:: /api/v1.0/churches/(int:<church_id>)/

    Update church instance with ``id`` = ``church_id``.

    **Example request**:

    .. sourcecode:: http

        PUT api/v1.1/churches/6/ HTTP/1.1
        Host: vocrm.org
        Allow: GET, PUT, PATCH, HEAD, OPTIONS
        Content-type: application/json
        Vary: Accept

        {
            "id": 6,
            "opening_date": "2016-01-01",
            "is_open": true,
            "link": "/churches/6/",
            "title": "Тествая Цервковь №1",
            "get_title": "Тествая Цервковь №1",
            "department": 1,
            "pastor": 5,
            "country": "Россия",
            "city": "Москва",
            "address": "Горького 55",
            "phone_number": "050-222-22-22",
            "website": ""
        }

    **Example response (Good response)**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, PUT, PATCH, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "id": 6,
            "opening_date": "01.01.2016",
            "is_open": true,
            "link": "/churches/6/",
            "title": "Тествая Цервковь №1",
            "get_title": "Тествая Цервковь №1",
            "department": 1,
            "pastor": 5,
            "country": "Россия",
            "city": "Москва",
            "address": "Горького 55",
            "phone_number": "050-222-22-22",
            "website": ""
        }

    **Example response (Bad request 1, with "required_field": null)**:

    .. sourcecode:: http

        HTTP/1.1 400 Bad Request
        Allow: GET, PUT, PATCH, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "department": [
                "Это поле не может быть null."
            ]
        {

    **Example response (Bad request 2)**:

    .. sourcecode:: http

        HTTP/1.1 400 Bad Request
        Allow: GET, PUT, PATCH, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "department": [
                "Это поле обязательно."
            ]
        }

    **Example response (Bad request 3, with pastor hierarchy level < 2 or pastor_id not exists)**:

    .. sourcecode:: http

        HTTP/1.1 400 Bad Request
        Allow: GET, PUT, PATCH, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "pastor": [
                "Данный пользователь \"50\" - не может быть назначен пастором Церкви."
            ]
        }

    **Example response (Bad request 4, with incorrect date format)**:

    .. sourcecode:: http

        HTTP/1.1 400 Bad Request
        Allow: GET, PUT, PATCH, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "opening_date": [
                "Неправильный формат date. Используйте один из этих форматов: YYYY[-MM[-DD]]."
            ]
        }

    **Example response (Not Found, with home_group_id doesn't exists)**:

    .. sourcecode:: http

        HTTP/1.1 404 Not Found
        Allow: GET, PUT, PATCH, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "detail": "Не найдено."
        }

    :form opening_date: the opening of the church date, **required**
    :form is_open: Church opening status - true or false, **required**
    :form title: title
    :form department: department id, **required**
    :form pastor: pastor id, **required**
    :form country: "", **required**
    :form city: city, **required**
    :form address: address
    :form phone_number: phone number
    :form website: web site

    :statuscode 201: success create
    :statuscode 400: bad request
    :statuscode 403: user is not authenticated
    :statuscode 404: there's no church


.. http:get:: /api/v1.0/churches/(int:<church_id>)/home_groups

    Details of ``Home Groups`` in selected ``Churhc`` with ``id = church_id``.
    Paginated by 30 home_groups per page

    **Example request**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "count": 1,
            "links": {
                "previous": null,
                "next": null
            },
            "results": [
                {
                    "id": 8,
                    "link": "/home_groups/8/",
                    "opening_date": "01.01.2017",
                    "title": "Тестовая Домашняя Группа 2",
                    "city": "Одесса",
                    "get_title": "Тестовая Домашняя Группа 2",
                    "church": {
                        "id": 6
                    },
                    "leader": {
                        "id": 50,
                        "fullname": "Болжеларская Марина Александровна"
                    },
                    "address": "Гарматная",
                    "phone_number": "093-288-23-32",
                    "website": ""
                }
            ]
        }

    **Example response (Bad request)**:

    .. sourcecode:: http

        HTTP/1.1 404 Not Found
        Allow: GET, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "detail": "Не найдено."
        }

    :statuscode 200: no error
    :statuscode 404: there's no church


.. http:get:: /api/v1.0/churches/potential_users_church/

    List of users for append to current church, only 30.

    **Example request**:

    .. sourcecode:: http

        GET /api/v1.0/churches/potential_users_church/?search=гал+ру HTTP/1.1
        Host: vocrm.org
        Content-type: application/json

    **Example response (Good request)**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        [
          {
            "id": 13096,
            "city": "Днепропетровск",
            "country": "Украина",
            "full_name": "Руденко Галина Ивановна"
          },
          {
            "id": 13834,
            "city": "Санкт Петербург",
            "country": "Россия",
            "full_name": "Мандрусова Галина Руслановна"
          },
          {
            "id": 15101,
            "city": "Луганск",
            "country": "Украина",
            "full_name": "Русинова Галина Пантелеевна"
          }
        ]

    **Example response (Bad Requst)**:

    .. sourcecode:: http

        HTTP/1.1 400 Bad Request
        Allow: GET, POST, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
          "search": "Length of search query must be > 2"
        }

    :query string search: search by ``full_name``, required (min length == ``3``)
    :query int department: filter by ``department id``, optional

    :statuscode 200: no error
    :statuscode 400: length of search request < 3


.. http:get:: /api/v1.0/churches/(int:<church_id>)/potential_users_group/

    List of users for append to group of current church, only 30.

    **Example request**:

    .. sourcecode:: http

        GET /api/v1.0/churches/1/potential_users_group/?search=гал+ру HTTP/1.1
        Host: vocrm.org
        Content-type: application/json

    **Example response (Good request)**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        [
          {
            "id": 13096,
            "city": "Днепропетровск",
            "country": "Украина",
            "full_name": "Руденко Галина Ивановна"
          },
          {
            "id": 13834,
            "city": "Санкт Петербург",
            "country": "Россия",
            "full_name": "Мандрусова Галина Руслановна"
          },
          {
            "id": 15101,
            "city": "Луганск",
            "country": "Украина",
            "full_name": "Русинова Галина Пантелеевна"
          }
        ]

    **Example response (Bad Request)**:

    .. sourcecode:: http

        HTTP/1.1 400 Bad Request
        Allow: GET, POST, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
          "search": "Length of search query must be > 2"
        }

    :query string search: search by ``full_name``, required (min length == ``3``)
    :query int department: filter by ``department id``, optional

    :statuscode 200: no error
    :statuscode 400: length of search request < 3


.. http:get:: /api/v1.0/churches/(int:<church_id>)/all_users

    List of users in the current ``Church`` including all users in home groups with ``id = church_id``.
    Pagination by 30 users per page.

    **Example request**

    .. sourcecode:: http

        GET /api/v1.0/churches/6/all_users/ HTTP/1.1
        Host: vocrm.org
        Content-type: application/json

    **Example response (Good request)**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "count": 3,
            "links": {
                "previous": null,
                "next": null
            },
            "results": [
                {
                    "id": 2,
                    "link": "/account/2/",
                    "fullname": "Аккаунт Технический №2",
                    "phone_number": "+38066666",
                    "repentance_date": null,
                    "spiritual_level": "Baby",
                    "born_date": "01.10.1993"
                },
                {
                    "id": 3,
                    "link": "/account/3/",
                    "fullname": "Аккаунт Технический №3",
                    "phone_number": "",
                    "repentance_date": null,
                    "spiritual_level": "Baby",
                    "born_date": "13.10.1993"
                },
                {
                    "id": 4,
                    "link": "/account/4/",
                    "fullname": "Аккаунт Технический №4",
                    "phone_number": "",
                    "repentance_date": null,
                    "spiritual_level": "Baby",
                    "born_date": "12.10.1993"
                },
            ]
        }

    **Example response (Not Found)**:

    .. sourcecode:: http

        HTTP/1.1 404 Not Found
        Allow: GET, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "detail": "Не найдено."
        }

    :statuscode 200: no error
    :statuscode 404: there's no church


.. http:get:: /api/v1.0/churches/(int:<church_id>)/users/

    Details of users without home group in single ``Church`` with ``id = church_id``.
    Pagination by 30 users per page.

    **Example request**:

    .. sourcecode:: http

        GET /api/v1.0/churches/6/users/ HTTP/1.1
        Host: vocrm.org
        Content-type: application/json

    **Example response (Good request)**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "count": 3,
            "results": [
                {
                    "id": 2,
                    "fullname": "Аккаунт Технический №2",
                    "phone_number": "+38066666",
                    "repentance_date": null,
                    "spiritual_level": 1,
                    "born_date": "01.10.1993"
                },
                {
                    "id": 3,
                    "fullname": "Аккаунт Технический №3",
                    "phone_number": "",
                    "repentance_date": null,
                    "spiritual_level": 1,
                    "born_date": "13.10.1993"
                },
                {
                    "id": 50,
                    "fullname": "Болжеларская Марина Александровна",
                    "phone_number": "+380506650363",
                    "repentance_date": null,
                    "spiritual_level": 1,
                    "born_date": "31.03.1978"
                }
            ],
            "links": {
                "previous": null,
                "next": null
            }
        }

    **Example response (Forbidden)**:

    .. sourcecode:: http

        HTTP/1.1 403 Forbidden
        Allow: GET, POST, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "detail": "Учетные данные не были предоставлены."
        }

    :query int page: page number (one of ``int`` or ``last``). default is 1
    :query int spiritual_level: filter by ``spiritual_level_id``
    :query string first_name: filter by ``first_name``
    :query string last_name: filter by ``last_name``
    :query int page_size: page size, default is 30

    :statuscode 200: no error
    :statuscode 403: user is not authenticated


.. http:post:: /api/v1.0/churches/(int:<church_id>)/add_user/

    Add new user for ``Church`` with ``id = church_id``.

    New user must be exists.
    New user should not be added in another ``Church``.
    New user should not be added in any ``Home Group``.

    **Example request**

    .. sourcecode:: http

        POST /api/v1.0/churches/6/add_user/10 HTTP/1.1
        Host: vocrm.org
        Content-type: application/json

        {
            "user_id": 10
        }

    **Example response (Good request)**:

    .. sourcecode:: http

        HTTP/1.1 201 Created
        Allow: POST, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "message": "Пользователь успешно добавлен."
        }

    **Example response (Forbidden)**:

    .. sourcecode:: http

        HTTP/1.1 403 Forbidden
        Allow: POST, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "detail": "Учетные данные не были предоставлены."
        }

    **Example response (Bad request 1)**:

    .. sourcecode:: http

        HTTP/1.1 400 Bad Request
        Allow: POST, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "message": "Некоректные данные"
        }

    **Example response (Bad request 2)**:

    .. sourcecode:: http

        HTTP/1.1 400 Bad Request
        Allow: POST, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "message": "Невозможно добавить пользователя. Данного пользователя не существует."
        }

    **Example response (Bad request 3)**:

    .. sourcecode:: http

        HTTP/1.1 400 Bad Request
        Allow: POST, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "message": "Невозможно добавить пользователя. Данный пользователь уже состоит в Церкви."
        }

    **Example response (Bad request 4)**:

    .. sourcecode:: http

        HTTP/1.1 400 Bad Request
        Allow: POST, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "message": "Невозможно добавить пользователя. Данный пользователь уже состоит в Домашней Группе."
        }

    :statuscode 201: success create
    :statuscode 400: bad request
    :statuscode 403: user is not authenticated


.. http:post:: /api/v1.0/churches/(<int:church_id>)/del_user

    Remove user from ``church`` with ``id = church_id``.

    **Example request**:

    .. sourcecode:: http

        POST /api/v1.0/churches/6/remove_user/ HTTP/1.1
        Allow: POST, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "user_id": "2"
        }

    **Example response (Good request)**:

    .. sourcecode:: http

        HTTP/1.1 204 No Content
        Allow: POST, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "message": "Пользователь успешно удален из Церкви"
        }

    **Example response (Bad request 1)**:

    .. sourcecode:: http

        HTTP/1.1 400 Bad Request
        Allow: POST, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "message": "Некоректные данные"
        }

    **Example response (Bad request 2)**:

    .. sourcecode:: http

        HTTP/1.1 400 Bad Request
        Allow: POST, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "message": "Невозможно удалить пользователя. Данного пользователя не существует."
        }

    **Example response (Bad request 3)**:

    .. sourcecode:: http

        HTTP/1.1 400 Bad Request
        Allow: POST, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "message": "Невозможно удалить пользователя. Пользователь не принадлежит к данной Церкви."
        }

    :statuscode 204: no content
    :statuscode 400: bad request
    :statuscode 403: user is not authenticated


HomeGroup
_________


.. http:get:: /api/v1.1/home_groups/

    List of the home groups. (order by ``opening_data``, ``id``).
    Displaying title of Home Group is ``get_title``.
    Paginate by 30 users per page.

    **Example request**:

    .. sourcecode:: http

        GET /api/v1.1/home_groups/ HTTP/1.1
        Host: vocrm.org
        Content-type: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, POST, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "count": 2,
            "results": [
                {
                    "id": 6,
                    "opening_date": "26.01.2017",
                    "title": "",
                    "get_title": "Киев П",
                    "city": "Киев",
                    "church": {
                        "id": 6,
                        "get_title": "Тествая Цервковь №1"
                    },
                    "leader": {
                        "id": 15160,
                        "fullname": "П Ростислав С"
                    },
                    "address": "",
                    "phone_number": "",
                    "website": ""
                },
                {
                    "id": 8,
                    "opening_date": "18.01.2017",
                    "title": "Тестовая Домашняя Группа 2",
                    "get_title": "Тестовая Домашняя Группа 2",
                    "city": "Одесса",
                    "church": {
                        "id": 6,
                        "get_title": "Тествая Цервковь №1"
                    },
                    "leader": {
                        "id": 15160,
                        "fullname": "П Ростислав С"
                    },
                    "address": "Гарматная",
                    "phone_number": "093-288-23-32",
                    "website": ""
                }
            ],
            "links": {
                "previous": null,
                "next": null
            }
        }

    **Example response(Forbidden)**:

    .. sourcecode:: http

        HTTP/1.1 403 Forbidden
        Allow: GET, POST, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "detail": "Учетные данные не были предоставлены."
        }

    :query int page: page number (one of ``int`` or ``last``). default is 1
    :query int church: filter by ``church_id``
    :query int leader: filter by ``leader_id``
    :query string city: filter by ``city``
    :query string title: filter by ``title``
    :query string phone_number: filter by ``phone_number``
    :query string website: filter by ``website``
    :query string ordering: order by one of ``address``, ``church``, ``city``, ``leader``,
                                            ``opening_date``, ``phone_number``, ``title``,
                                            ``website``,

    :statuscode 200: no error
    :statuscode 403: no authentication


.. http:post:: /api/v1.0/home_groups/

    Create new home_group with following parameters.
    Home group leader hierarchy level must be more then ``parishioner``.

    **Example request**:

    .. sourcecode:: http

        POST /api/v1.1/home_groups HTTP/1.1
        Host: vocrm.org
        Content-type: application/json

        {
            "opening_date": "2017-01-01",
            "title": "Домашняя Группа №1",
            "city": "Киев",
            "church": 6,
            "leader": 5,
            "address": "Крещатик 1",
            "phone_number": "050-237-09-26",
            "website": "http://facebook.com"
        }

    **Example response (Good response)**:

    .. sourcecode:: http

        HTTP/1.1 201 Created
        Allow: GET, POST, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "id": 10,
            "opening_date": "01.01.2017",
            "title": "Домашняя Группа №1",
            "get_title": "Домашняя Группа №1",
            "city": "Киев",
            "church": 6,
            "leader": 5,
            "address": "Крещатик 1",
            "phone_number": "050-237-09-26",
            "website": "http://facebook.com"
        }

    **Example response (Bad request 1)**:

    .. sourcecode:: http

        HTTP/1.1 400 Bad Request
        Allow: GET, POST, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "church": [
                "Это поле не может быть null."
            ]
        }

    **Example response (Bad request 2)**:

    .. sourcecode:: http

        HTTP/1.1 400 Bad Request
        Allow: GET, POST, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "church": [
                "Недопустимый первичный ключ \"200\" - объект не существует."
            ]
        }

    **Example response (Bad request 3)**:

    .. sourcecode:: http

        HTTP/1.1 400 Bad Request
        Allow: GET, POST, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "church": [
                "Это поле обязательно."
            ]
        }

    **Example response (Bad request 4, with "leader" hierarchy level < 1)**:

    .. sourcecode:: http

        HTTP/1.1 400 Bad Request
        Allow: GET, POST, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "leader": [
                "Данный пользователь \"23\" - не может быть назначен лидером Домашней Группы."
            ]
        }

    :form opening_date: home group opening date, **required**
    :form title: title
    :form city: city, **required**
    :form church: church id, **required**
    :form leader: leader id, **required**
    :form address: address
    :form phone_number: phone_number
    :form website: web site

    :statuscode 201: success create
    :statuscode 400: bad request
    :statuscode 403: user is not authenticated


.. http:get:: /api/v1.0/home_group/(int:<home_group_id>)/

    Detail information about ``Home Group``. Response consists of list of users for requested Home Group
    with ``id`` = ``home_group_id``.

    **Example request**:

    .. sourcecode:: http

        GET /api/v1.0/home_groups/8/ HTTP/1.1
        Host: vocrm.org
        Accept: application/json

    **Example response (Good request)**:

    .. sourcecode:: http

        {
            "id": 8,
            "link": "/home_groups/8/",
            "opening_date": "01.01.2017",
            "title": "Тестовая Домашняя Группа 2",
            "city": "Одесса",
            "get_title": "Тестовая Домашняя Группа 2",
            "church": 6,
            "leader": 50,
            "address": "Гарматная",
            "phone_number": "093-288-23-32",
            "website": ""
        }

    **Example response (Forbidden)**:

    .. sourcecode:: http

        HTTP/1.1 403 Forbidden
        Allow: GET, PUT, PATCH, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "detail": "Учетные данные не были предоставлены."
        }

    **Example response (Not Found)**:

    .. sourcecode:: http

        HTTP/1.1 404 Not Found
        Allow: GET, PUT, PATCH, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "detail": "Не найдено."
        }

    :statuscode 200: no error
    :statuscode 403: no authentication
    :statuscode 404: there's no home groups


.. http:put:: /api/v1.0/home_group/(int:<home_group_id>)/
.. http:patch:: /api/v1.0/home_group/(int:<home_group_id>)/

    Update home_group instance with ``id = home_group_id``.

    **Example request**:

    .. sourcecode:: http

        PUT /api/v1.0/home_group/(int:<home_group_id>)/ HTTP/1.1
        Host: vocrm.org
        Content-type: application/json

        {
            "id": 6,
            "opening_date": "2017-01-01",
            "title": "Домашняя Группа №2",
            "get_title": "Домашняя Группа №2",
            "city": "Киев",
            "church": 6,
            "leader": 15160,
            "address": "Крещатик 10",
            "phone_number": "",
            "website": ""
        }

    **Example response (Good response)**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, PUT, PATCH, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "id": 6,
            "opening_date": "01.01.2017",
            "title": "Домашняя Группа №2",
            "get_title": "Домашняя Группа №2",
            "city": "Киев",
            "church": 6,
            "leader": 15160,
            "address": "Крещатик 10",
            "phone_number": "",
            "website": ""
        }

    **Example response (Bad request 1, without required field)**:

    .. sourcecode:: http

        HTTP/1.1 400 Bad Request
        Allow: GET, PUT, PATCH, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "church": [
                "Это поле обязательно."
            ]
        }

    **Example response (Bad request 2, with "required_field": null)**:

    .. sourcecode:: http

        HTTP/1.1 400 Bad Request
        Allow: GET, PUT, PATCH, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "church": [
                "Это поле не может быть null."
            ]
        }

    **Example response (Bad request 3, with incorrect date format)**:

    .. sourcecode:: http

        HTTP/1.1 400 Bad Request
        Allow: GET, PUT, PATCH, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "opening_date": [
                "Неправильный формат date. Используйте один из этих форматов: YYYY[-MM[-DD]]."
            ]
        }

    **Example response (Bad request 4, with leader hierarchy level < 1 or leader_id not exists)**:

    .. sourcecode:: http

        HTTP/1.1 400 Bad Request
        Allow: GET, PUT, PATCH, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "leader": [
                "Данный пользователь \"23\" - не может быть назначен лидером Домашней Группы."
            ]
        }

    **Example response (Forbidden)**:

    .. sourcecode:: http

        HTTP/1.1 403 Forbidden
        Allow: GET, PUT, PATCH, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "detail": "Учетные данные не были предоставлены."
        }


    :form opening_date: home group opening date, **required**
    :form title: title
    :form city: city, **required**
    :form church: church id, **required**
    :form leader: leader id, **required**
    :form address: address
    :form phone_number: phone_number
    :form website: web site

    :statuscode 200: updated
    :statuscode 400: bad request
    :statuscode 403: user is not authenticated


.. http:get:: /api/v1.0/home_groups/(int:<home_group_id>)/users

    List of the users of ``Home Group`` with ``id = home_group_id``.
    Pagination by 30 user per page.

    **Example request**:

    .. sourcecode:: http

        GET /api/v1.0/home_groups/8/users/ HTTP/1.1
        Host: vocrm.org
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
        "count": 3,
            "links": {
                "previous": null,
                "next": null
            },
            "results": [
                {
                    "id": 7,
                    "fullname": "Аккаунт Технический №7",
                    "phone_number": "",
                    "repentance_date": null,
                    "spiritual_level": 1,
                    "born_date": "09.10.1993"
                },
                {
                    "id": 8,
                    "fullname": "Аккаунт Технический №8",
                    "phone_number": "",
                    "repentance_date": null,
                    "spiritual_level": 1,
                    "born_date": "26.01.1995"
                },
                {
                    "id": 2,
                    "fullname": "Аккаунт Технический №2",
                    "phone_number": "+38066666",
                    "repentance_date": null,
                    "spiritual_level": 1,
                    "born_date": "01.10.1993"
                },
            ]
        }

    **Example response (Not Found)**:

    .. sourcecode:: http

        HTTP/1.1 404 Not Found
        Allow: GET, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "detail": "Не найдено."
        }

    **Example response (Forbidden)**:

    .. sourcecode:: http

        HTTP/1.1 403 Forbidden
        Allow: GET, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "detail": "Учетные данные не были предоставлены."
        }

    :statuscode 200: no error
    :statuscode 403: user is not authenticated
    :statuscode 404: there's no home_group


.. http:post:: /api/v1.0/home_groups/6/add_user

    Add new user for ``Home Group`` with ``id = home_group_id``.

    **Example request**:

    .. sourcecode:: http

        POST /api/v1.0/home_groups/add_user/ HTTP/1.1
        Host: vocrm.org
        Content-type: application/json

        {
            "user_id": 5
        }

    **Example response (Good request)**:

    .. sourcecode:: http

        HTTP/1.1 201 Created
        Allow: POST, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "message": "Пользователь успешно добавлен."
        }

    **Example response (Bad request 1, with "user_id": null)**

    .. sourcecode:: http

        HTTP/1.1 400 Bad Request
        Allow: POST, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "message": "Некоректные данные"
        }

    **Example response (Bad request 2, with user_id not exists)**

    .. sourcecode:: http

        HTTP/1.1 400 Bad Request
        Allow: POST, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "message": "Невозможно добавить пользователя. Данного пользователя не существует."
        }

    **Example response (Bad request 3)**:

    .. sourcecode:: http

        HTTP/1.1 400 Bad Request
        Allow: POST, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "message": "Невозможно добавить пользователя. Данный пользователь уже состоит в Домашней Группе."
        }

    **Example response (Bad request 4)**:

    .. sourcecode:: http

        HTTP/1.1 400 Bad Request
        Allow: POST, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "message": "Невозможно добавить пользователя. Пользователь не состоит в Церкви"
        }

    **Example response (Bad request 5)**:

    .. sourcecode:: http

        HTTP/1.1 400 Bad Request
        Allow: POST, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "message": "Невозможно добавить пользователя. Данный пользователь является членом другой Церкви"
        }

    **Example response (Forbidden)**:

    .. sourcecode:: http

        HTTP/1.1 403 Forbidden
        Allow: POST, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "detail": "Учетные данные не были предоставлены."
        }

    :statuscode 201: user added
    :statuscode 400: bad request
    :statuscode 403: no authentication


.. http:post:: /api/v1.0/home_groups/(int:<home_group_id>)/del_user

    Delete user from ``Home Group`` with ``id`` = ``home_group_id``.
    A remote user becomes a member of the his Church, without a home group.
    
    **Example request**:

    .. sourcecode:: http

        POST /api/v1.0/home_group/6/del_user HTTP/1.1
        Host: vocrm.org
        Content-type: application/json

        {
            "user_id": 2
        }

    **Example response (Good request)**:

    .. sourcecode:: http

        HTTP/1.1 204 No Content
        Allow: POST, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "message": "Пользователь успешно удален."
        }

    **Example response (Bad request 1)**:

    .. sourcecode:: http

        HTTP/1.1 400 Bad Request
        Allow: POST, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "message": "Невозможно удалить пользователя. Пользователь не принадлежит к данной Домашней Группе."
        }

    **Example response (Bad request 2, with "user_id": null)**:

    .. sourcecode:: http

        HTTP/1.1 400 Bad Request
        Allow: POST, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "message": "Некоректные данные"
        }

    **Example response (Bad request 3, with user_id not exists)**:

    .. sourcecode:: http

        HTTP/1.1 400 Bad Request
        Allow: POST, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "message": "Невозможно удалить пользователя. Данного пользователя не существует."
        }

    **Example response (Not Found, with home_group_id doesn't exists)**:

    .. sourcecode:: http

        HTTP/1.1 404 Not Found
        Allow: POST, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "detail": "Не найдено."
        }

    **Example response(Forbidden)**:

    .. sourcecode:: http

        HTTP/1.1 403 Forbidden
        Allow: POST, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "detail": "Учетные данные не были предоставлены."
        }

    :statuscode 204: user deleted
    :statuscode 400: bad request
    :statuscode 403: user is not authenticated
    :statuscode 404: there's no home group
