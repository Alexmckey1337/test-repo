==================
vo.org.ua REST API
==================

Departments
-----------


List of departments
~~~~~~~~~~~~~~~~~~~

.. http:get:: /api/vo/departments/

    List of the departments.

    **Example request**:

    .. sourcecode:: http

        GET /api/vo/departments/ HTTP/1.1
        Host: vocrm.net
        Vo-Org-Ua-Token: voorguatoken
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept, Cookie
        Allow: GET,HEAD,OPTIONS
        Content-Type: application/json

        [
            {
                "id": 1,
                "title": "Киев"
            },
            {
                "id": 2,
                "title": "Дочерняя Церковь"
            },
            {
                "id": 4,
                "title": "Германия"
            },
            {
                "id": 5,
                "title": "США"
            },
            {
                "id": 6,
                "title": "Днепр"
            },
            {
                "id": 7,
                "title": "Другая церковь"
            },
            {
                "id": 8,
                "title": "Интернет ячейки"
            }
        ]

    **Example request (forbidden)**:

    .. sourcecode:: http

        GET /api/vo/departments/ HTTP/1.1
        Host: vocrm.net
        Accept: application/json

    **Example response (forbidden)**:

    .. sourcecode:: http

        HTTP/1.1 403 Forbidden
        Vary: Accept, Cookie
        Allow: GET,HEAD,OPTIONS
        Content-Type: application/json

        {"detail": "Учетные данные не были предоставлены."}

    :statuscode 200: no error
    :statuscode 403: forbidden


Directions
----------


List of directions
~~~~~~~~~~~~~~~~~~

.. http:get:: /api/vo/home_groups/directions/

    List of the directions.

    **Example request**:

    .. sourcecode:: http

        GET /api/vo/home_groups/directions/ HTTP/1.1
        Host: vocrm.net
        Vo-Org-Ua-Token: voorguatoken
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept, Cookie
        Allow: GET,HEAD,OPTIONS
        Content-Type: application/json

        [
            {
                "code": "one",
                "title_by_languages": {
                    "ru": "ru title",
                    "en": "en title",
                    "de": "de title"
                }
            },
            {
                "code": "two",
                "title_by_languages": {
                    "ru": "ru other",
                    "en": "en other",
                    "de": "de other"
                }
            }
        ]

    **Example request (forbidden)**:

    .. sourcecode:: http

        GET /api/vo/home_groups/directions/ HTTP/1.1
        Host: vocrm.net
        Accept: application/json

    **Example response (forbidden)**:

    .. sourcecode:: http

        HTTP/1.1 403 Forbidden
        Vary: Accept, Cookie
        Allow: GET,HEAD,OPTIONS
        Content-Type: application/json

        {"detail": "Учетные данные не были предоставлены."}

    :statuscode 200: no error
    :statuscode 403: forbidden


Cities
------


List of cities
~~~~~~~~~~~~~~

.. http:get:: /api/vo/city/

    List of the available cities. Min length of the search request == 2.
    Max result == 100 cities. Ordering by score.

    **Example request**:

    .. sourcecode:: http

        GET /api/vo/city/?city=abc HTTP/1.1
        Host: vocrm.net
        Vo-Org-Ua-Token: voorguatoken
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept, Cookie
        Allow: GET,HEAD,OPTIONS
        Content-Type: application/json

        {
            "cities": [
                {
                    "pk": 1039613,
                    "city": "Abcoven",
                    "location": {
                        "lat": 12.3456,
                        "lon": -9.876,
                    },
                    "country": "Нидерланды",
                    "area": "Noord-Brabant",
                    "district": "Gemeente Goirle",
                    "score": 18.1083
                },
                {
                    "pk": 1037476,
                    "city": "Gemeente Abcoude",
                    "location": {},
                    "country": "Нидерланды",
                    "area": "Utrecht",
                    "district": "",
                    "score": 14.315948
                }
            ],
            "filters": {
                "countries": [
                    {
                        "pk": "NL",
                        "name": "Нидерланды",
                        "count": 2
                    }
                ],
                "areas": [
                    {
                        "pk": 9945,
                        "name": "Noord-Brabant",
                        "count": 1
                    },
                    {
                        "pk": 11468,
                        "name": "Utrecht",
                        "count": 1
                    }
                ],
                "districts": [
                    {
                        "pk": 23692,
                        "name": "Gemeente Goirle",
                        "count": 1
                    }
                ]
            }
        }

    **Example request (without search query)**:

    .. sourcecode:: http

        GET /api/vo/city/ HTTP/1.1
        Host: vocrm.net
        Vo-Org-Ua-Token: voorguatoken
        Accept: application/json

    **Example response (without search query)**:

    .. sourcecode:: http

        HTTP/1.1 400 Bad Request
        Vary: Accept, Cookie
        Allow: GET,HEAD,OPTIONS
        Content-Type: application/json

        {"search": "Length of search query must be > 1"}

    **Example request (forbidden)**:

    .. sourcecode:: http

        GET /api/vo/city/?city=abc HTTP/1.1
        Host: vocrm.net
        Accept: application/json

    **Example response (forbidden)**:

    .. sourcecode:: http

        HTTP/1.1 403 Forbidden
        Vary: Accept, Cookie
        Allow: GET,HEAD,OPTIONS
        Content-Type: application/json

        {"detail": "Учетные данные не были предоставлены."}

    :query string city: search by name of the city

    :query string country: filter by name of the country, full match, case sensitive
    :query string area: filter by name of the area, full match, case sensitive
    :query string district: filter by name of the district, full match, case sensitive

    :query string country_id: filter by ``id`` of the country
    :query int area_id: filter by ``id`` of the area
    :query int district_id: filter by ``id`` of the district

    :statuscode 200: no error
    :statuscode 400: bad request
    :statuscode 403: forbidden


Home group
----------


List of home groups
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. http:get:: /api/vo/home_groups/

    List of the active home groups

    **Example request**:

    .. sourcecode:: http

        GET /api/vo/home_groups/?department_id=8&only_fields=id,title,leader&only_fields=locality,language,directions HTTP/1.1
        Host: vocrm.net
        Vo-Org-Ua-Token: voorguatoken
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept, Cookie
        Allow: GET,HEAD,OPTIONS
        Content-Type: application/json

        [
            {
                "id": 1234,
                "directions": [
                    {
                        "code": "dir1",
                        "title": "first"
                    },
                    {
                        "code": "other",
                        "title": "second"
                    }
                ],
                "language": "ua",
                "leader": {
                    "id": 987,
                    "last_name": "last",
                    "first_name": "first",
                    "middle_name": "other"
                },
                "locality": {
                    "id": 1432169,
                    "city": "Севан",
                    "country": "Армения"
                },
                "title": "last first 8"
            },
            ...
        ]


    **Example request (forbidden)**:

    .. sourcecode:: http

        GET /api/vo/home_groups/ HTTP/1.1
        Host: vocrm.net
        Accept: application/json

    **Example response (forbidden)**:

    .. sourcecode:: http

        HTTP/1.1 403 Forbidden
        Vary: Accept, Cookie
        Allow: GET,HEAD,OPTIONS
        Content-Type: application/json

        {"detail": "Учетные данные не были предоставлены."}

    :query string only_fields: list of required fields
    :query int department_id: filter by ``id`` of the department

    :statuscode 200: no error
    :statuscode 403: forbidden


Proposals
---------



Create new proposal
~~~~~~~~~~~~~~~~~~~

.. http:post:: /api/proposal/create/

    Create new proposal. All fields are optional.

    **Example request**:

    .. sourcecode:: http

        POST /api/proposal/create/ HTTP/1.1
        Host: vocrm.net
        Accept: application/json
        content-type: application/json
        content-length: 366

        {
            "first_name": "first",
            "last_name": "last",
            "sex": "female",
            "born_date": "2000-02-04",
            "locality": 22,
            "city": "City name",
            "country": "Country name",
            "type": "full",
            "email": "someaddress@gmail.com",
            "phone_number": "+380998887766",
            "leader_name": "Leader Name Ivanovich",
            "age_group": "80+",
            "gender_group": "some group",
            "geo_location": "some data",
            "directions": ["meni", "drugoi", "interes"]
        }


    **Example response (Good request)**:

    .. sourcecode:: http

        HTTP/1.1 201 Created
        Vary: Accept, Cookie
        Allow: POST, OPTIONS
        Content-Type: application/json

        {
            "first_name": "first",
            "last_name": "last",
            "sex": "female",
            "born_date": "04.02.2000",
            "locality": 22,
            "city": "City name",
            "country": "Country name",
            "email": "someaddress@gmail.com",
            "phone_number": "+380998887766",
            "type": "full",
            "leader_name": "Leader Name Ivanovich",
            "age_group": "80+",
            "gender_group": "some group",
            "geo_location": "some data",
            "directions": [
                "meni",
                "drugoi",
                "interes"
            ]
        }

    **Example response (invalid locality id)**:

    .. sourcecode:: http

        HTTP/1.1 400 Bad Request
        Vary: Accept, Cookie
        Allow: POST, OPTIONS
        Content-Type: application/json

        {
            "locality": [
                "Недопустимый первичный ключ \"2246246262\" - объект не существует."
            ]
        }

    **Example request (forbidden)**:

    .. sourcecode:: http

        GET /api/proposal/create/ HTTP/1.1
        Host: vocrm.net
        Accept: application/json

    **Example response (forbidden)**:

    .. sourcecode:: http

        HTTP/1.1 403 Forbidden
        Vary: Accept, Cookie
        Allow: GET,HEAD,OPTIONS
        Content-Type: application/json

        {"detail": "Учетные данные не были предоставлены."}

    :form first_name: first name, max length == 30
    :form last_name: last name, max length == 150
    :form sex: sex of the user, one of (``male``, ``female``)
    :form born_date: born date of the user, format ``YYYY-MM-DD``
    :form locality: id of the city, **deprecated**
    :form city: string, max length == 120
    :form country: string, max length == 120
    :form type: type of the proposal, one of (``short``, ``full``)
    :form email: email of the user, max length == 250
    :form phone_number: phone number of the user, max length == 23
    :form leader_name: name of the leader, max length == 255
    :form age_group: string, max length == 255
    :form gender_group: string, max length == 255
    :form geo_location: string, max length == 255
    :form directions: list of the directions, don't validated on the server, max length of the elements == 60

    :reqheader Content-Type: ``application/json``

    :statuscode 201: success create
    :statuscode 403: forbidden
    :statuscode 400: bad request



List of proposals
~~~~~~~~~~~~~~~~~

.. http:get:: /api/proposal/

    List of the proposals. Pagination by 30 items. Ordering by date_created.

    ``raw_data`` — body of the request

    **Example request**:

    .. sourcecode:: http

        GET /api/proposal/ HTTP/1.1
        Host: vocrm.net
        Vo-Org-Ua-Token: voorguatoken
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept, Cookie
        Allow: GET,HEAD,OPTIONS
        Content-Type: application/json

        {
            "count": 16,
            "next": null,
            "previous": null,
            "results": [
                {
                    "first_name": "first",
                    "last_name": "last",
                    "sex": "unknown",
                    "born_date": "04.02.2040",
                    "locality": 22,
                    "city": "citycity",
                    "country": "Country name",
                    "email": "someaddress@gmail.com",
                    "phone_number": "+380998887766",
                    "type": "other",
                    "leader_name": "Leader Name Ivanovich",
                    "age_group": "80+",
                    "gender_group": "some group",
                    "geo_location": "some data",
                    "directions": [
                        "meni",
                        "drugoi",
                        "interes",
                    ],
                    "raw_data": {
                        "sex": "girl",
                        "city": "citycity",
                        "type": "incorrect",
                        "email": "someaddress@gmail.com",
                        "country": "Country name",
                        "locality": 22,
                        "age_group": "80+",
                        "born_date": "2040-02-04",
                        "last_name": "last",
                        "directions": [
                            "meni",
                            "drugoi",
                            "interes",
                        ],
                        "first_name": "first",
                        "leader_name": "Leader Name Ivanovich",
                        "gender_group": "some group",
                        "geo_location": "some data",
                        "phone_number": "+380998887766"
                    },
                    "created_at": "2018-06-16T08:59:52.745889Z"
                },
                ...
            ]
        }

    **Example request (forbidden)**:

    .. sourcecode:: http

        GET /api/proposal/ HTTP/1.1
        Host: vocrm.net
        Accept: application/json

    **Example response (forbidden)**:

    .. sourcecode:: http

        HTTP/1.1 403 Forbidden
        Vary: Accept, Cookie
        Allow: GET,HEAD,OPTIONS
        Content-Type: application/json

        {"detail": "Учетные данные не были предоставлены."}

    :query int page: page number

    :query string sex: filter by gender, one of (``male``, ``female``, ``unknown``)
    :query string type: filter by type, one of (``full``, ``short``, ``other``)
    :query string created_from: filter by datetime of created, UTC, format:
        ``YYYY-MM-DD HH:mm:SS`` or ``YYYY-MM-DD HH:mm``
    :query string created_to: filter by datetime of created, UTC, format:
            ``YYYY-MM-DD HH:mm:SS`` or ``YYYY-MM-DD HH:mm``
    :query string search_fio: search by ``first_name`` or ``last_name``
    :query string search_email: search by ``email``
    :query string search_phone_number: search by ``phone_number``
    :query string search_city: search by ``city``
    :query string search_country: search by ``country``
    :query string search: search by ``leader_name``, ``age_group``,
                                    ``gender_group``, ``geo_location``
    :query string ordering: order by one of
        (``first_name``, ``last_name``, ``born_date``, ``country``, ``city``,
         ``phone_number``, ``email``, ``sex``, ``type``),
         may be multible, e.g. ``?ordering=type,-sex``


    :statuscode 200: no error
    :statuscode 403: forbidden


Users
-----


List of the messengers
~~~~~~~~~~~~~~~~~~~~~~

.. http:get:: /api/vo/messengers/

    List of the messengers.

    **Example request**:

    .. sourcecode:: http

        GET /api/vo/messengers/ HTTP/1.1
        Host: vocrm.net
        Vo-Org-Ua-Token: voorguatoken
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept, Cookie
        Allow: GET,HEAD,OPTIONS
        Content-Type: application/json

        [
            {
                "id": 2,
                "code": "telegram",
                "title": "Telegram",
                "icon": null
            },
            {
                "id": 3,
                "code": "skype",
                "title": "Skype",
                "icon": null
            },
            {
                "id": 1,
                "code": "viber",
                "title": "Viber",
                "icon": null
            }
        ]

    **Example request (forbidden)**:

    .. sourcecode:: http

        GET /api/vo/messengers/ HTTP/1.1
        Host: vocrm.net
        Accept: application/json

    **Example response (forbidden)**:

    .. sourcecode:: http

        HTTP/1.1 403 Forbidden
        Vary: Accept, Cookie
        Allow: GET,HEAD,OPTIONS
        Content-Type: application/json

        {"detail": "Учетные данные не были предоставлены."}

    :statuscode 200: no error
    :statuscode 403: forbidden


User information
~~~~~~~~~~~~~~~~

.. http:get:: /api/vo/users/<user_id>/

    User information

    **Example request**:

    .. sourcecode:: http

        GET /api/vo/users/444/ HTTP/1.1
        Host: vocrm.net
        Vo-Org-Ua-Token: voorguatoken
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept, Cookie
        Allow: GET,HEAD,OPTIONS
        Content-Type: application/json

        {
            "first_name": "Myname",
            "last_name": "Yourname",
            "middle_name": "",
            "image": "https://s3.eu-central-1.amazonaws.com/bucketname/folders/filename.png",
            "phone_number": "+380669992233",
            "extra_phone_numbers": [
                "380996665544",
                "156464564846"
            ],
            "email": "best@mail.address",
            "locality": {
                "id": 4910,
                "name": "Киев",
                "country_name": "Украина",
                "area_name": "Киевская область",
                "district_name": "місто Київ"
            },
            "address": "ул. Blablabla, 42",
            "church": {
                "id": 11111,
                "title": "my church"
            },
            "home_group": {
                "id": 22222,
                "title": "my home group"
            },
            "master": {
                "id": 66666,
                "title": "Last First Middle"
            },
            "repentance_date": "22.02.2002,
            "hierarchy": {
                "id": 8,
                "title": "Старший епископ",
                "level": 60
            }
        }

    **Example request (forbidden)**:

    .. sourcecode:: http

        GET /api/vo/users/444/ HTTP/1.1
        Host: vocrm.net
        Accept: application/json

    **Example response (forbidden)**:

    .. sourcecode:: http

        HTTP/1.1 403 Forbidden
        Vary: Accept, Cookie
        Allow: GET,HEAD,OPTIONS
        Content-Type: application/json

        {"detail": "Учетные данные не были предоставлены."}

    **Example request (not found)**:

    .. sourcecode:: http

        GET /api/vo/users/444222/ HTTP/1.1
        Host: vocrm.net
        Vo-Org-Ua-Token: voorguatoken
        Accept: application/json

    **Example response (not found)**:

    .. sourcecode:: http

        HTTP/1.1 404 Not Found
        Vary: Accept, Cookie
        Allow: GET,HEAD,OPTIONS
        Content-Type: application/json

        {"detail": "Не найдено"}

    :>json string first_name: first name of the user, can be empty
    :>json string last_name: last name of the user, can be empty
    :>json string middle_name: middle name of the user, can be empty
    :>json string phone_number: phone number of the user, can be empty
    :>json list extra_phone_numbers: additional phones of the user, can be empty
    :>json string email: email of the user, can be empty
    :>json object locality: city of the user, can be null
    :>json string address: address of the user, can be empty
    :>json object church: church of the user, can be null
    :>json object home_group: home group of the user, can be null
    :>json object master: master of the user, can be null
    :>json string repentance_date: repentance date of the user, can be empty, format: ``DD.MM.YYYY``
    :>json object hierarchy: hierarchy of the user

    :statuscode 200: no error
    :statuscode 403: forbidden
    :statuscode 404: page not found



Master information
~~~~~~~~~~~~~~~~~~

.. http:get:: /api/vo/users/<user_id>/master/

    Information about master of the user.
    If user don't have master (responsible) — it's correct and status_code == 200.

    **Example request**:

    .. sourcecode:: http

        GET /api/vo/users/444/master/ HTTP/1.1
        Host: vocrm.net
        Vo-Org-Ua-Token: voorguatoken
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept, Cookie
        Allow: GET,HEAD,OPTIONS
        Content-Type: application/json

        {
            "id": 66666,
            "first_name": "First",
            "last_name": "Last",
            "middle_name": "Middle",
            "phone_number": "+380994446644",
            "extra_phone_numbers": ["+380446664466", "+380664446644"],
            "email": "master@mail.address",
            "hierarchy": {
                "id": 8,
                "title": "Старший епископ",
                "level": 60
            },
            "messengers": [
                {
                    "code": "telegram",
                    "value": "+38099telegram"
                },
                {
                    "code": "skype",
                    "value": "skype.name.microsoft"
                }
            ]
        }

    **Example response (user don't have master)**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept, Cookie
        Allow: GET,HEAD,OPTIONS
        Content-Type: application/json

        {
            "detail": "У пользователя нет ответственного."
        }

    **Example request (forbidden)**:

    .. sourcecode:: http

        GET /api/vo/users/444/master/ HTTP/1.1
        Host: vocrm.net
        Accept: application/json

    **Example response (forbidden)**:

    .. sourcecode:: http

        HTTP/1.1 403 Forbidden
        Vary: Accept, Cookie
        Allow: GET,HEAD,OPTIONS
        Content-Type: application/json

        {"detail": "Учетные данные не были предоставлены."}

    **Example request (not found)**:

    .. sourcecode:: http

        GET /api/vo/users/444222/master/ HTTP/1.1
        Host: vocrm.net
        Vo-Org-Ua-Token: voorguatoken
        Accept: application/json

    **Example response (not found)**:

    .. sourcecode:: http

        HTTP/1.1 404 Not Found
        Vary: Accept, Cookie
        Allow: GET,HEAD,OPTIONS
        Content-Type: application/json

        {"detail": "Не найдено"}

    :>json int id: id of the master
    :>json string first_name: first name of the master, can be empty
    :>json string last_name: last name of the master, can be empty
    :>json string middle_name: middle name of the master, can be empty
    :>json string phone_number: phone number of the master, can be empty
    :>json list extra_phone_numbers: additional phones of the master, can be empty
    :>json string email: email of the master, can be empty
    :>json object hierarchy: hierarchy of the master
    :>json list messengers: list of the messengers of the master, can be empty
    :>json object messengers[n]: messenger of the master
    :>json string messengers[n].code: code of the messenger, see `List of the messengers`_
    :>json string messengers[n].value: phone number of the messenger, or nickname, username, etc

    :statuscode 200: no error
    :statuscode 403: forbidden
    :statuscode 404: page not found




Update user information
~~~~~~~~~~~~~~~~~~~~~~~

.. http:patch:: /api/vo/users/<user_id>/

    Update user information

    **Example request**:

    .. sourcecode:: http

        PATCH /api/vo/users/444/ HTTP/1.1
        Host: vocrm.net
        Accept: application/json
        content-type: multipart/form-data; boundary=X-VOCRM-BOUNDARY
        content-length: 804

        --X-VOCRM-BOUNDARY
        Content-Disposition: form-data; name="image"; filename="filename.png"
        Content-Type: image/png
        ?PNG
        .
        ..

        --X-INSOMNIA-BOUNDARY
        Content-Disposition: form-data; name="phone_number"
        38(099)666-44-66
        --X-INSOMNIA-BOUNDARY
        Content-Disposition: form-data; name="extra_phone_numbers"
        ["380996665544","156464564846"]
        --X-INSOMNIA-BOUNDARY
        Content-Disposition: form-data; name="email"
        best@mail.address
        --X-INSOMNIA-BOUNDARY--


    **Example response (Good request)**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept, Cookie
        Allow: PATCH, OPTIONS
        Content-Type: application/json

        {
            "image": "https://s3.eu-central-1.amazonaws.com/bucket/folders/filename.png",
            "phone_number": "+380996664466",
            "extra_phone_numbers": [
                "380996665544",
                "156464564846"
            ],
            "email": "best@mail.address"
        }

    **Example request (bad request)**:

    .. sourcecode:: http

        PATCH /api/vo/users/444/ HTTP/1.1
        Host: vocrm.net
        Accept: application/json
        content-type: multipart/form-data; boundary=X-VOCRM-BOUNDARY
        content-length: 104

        --X-INSOMNIA-BOUNDARY
        Content-Disposition: form-data; name="phone_number"
        38(099)
        --X-INSOMNIA-BOUNDARY

    **Example response (invalid phone number)**:

    .. sourcecode:: http

        HTTP/1.1 400 Bad Request
        Vary: Accept, Cookie
        Allow: PATCH, OPTIONS
        Content-Type: application/json

        {
            "phone_number": {
                "message": "The length of the phone number must be at least 10 digits"
            }
        }

    **Example request (forbidden)**:

    .. sourcecode:: http

        GET /api/vo/users/444/ HTTP/1.1
        Host: vocrm.net
        Accept: application/json

    **Example response (forbidden)**:

    .. sourcecode:: http

        HTTP/1.1 403 Forbidden
        Vary: Accept, Cookie
        Allow: GET,HEAD,OPTIONS
        Content-Type: application/json

        {"detail": "Учетные данные не были предоставлены."}

    :form image: user photo, optional
    :form phone_number: user phone number, optional, must be >= 10 digits
    :form extra_phone_number: user additional phone numbers, optional, each must be >= 10 digits,
        format: ``'["firstnumber", "secondnumber", "thirdnumber"]'``
    :form email: user email, optional, correct email address

    :reqheader Content-Type: ``multipart/form-data``

    :statuscode 200: success update
    :statuscode 403: forbidden
    :statuscode 400: bad request
