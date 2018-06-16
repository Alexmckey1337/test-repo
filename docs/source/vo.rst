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

        POST /api/vo/proposal/create/ HTTP/1.1
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

        GET /api/vo/proposal/create/ HTTP/1.1
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
