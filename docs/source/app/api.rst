List of summit users
~~~~~~~~~~~~~~~~~~~~

.. http:get:: /api/app/summits/<summit_id>/users/[<master_id>]/

    List of the users of summit with id = ``summit_id``.

    **Example request**:

    .. sourcecode:: http

        GET /api/app/summits/7/users/ HTTP/1.1
        Host: vocrm.org
        Accept: application/json

    **Example response (invalid token)**:

    .. sourcecode:: http

        HTTP/1.1 403 Forbidden
        Vary: Accept, Cookie
        Allow: GET,HEAD,OPTIONS
        Content-Type: application/json

        {
            "detail": "Недопустимый токен."
        }

    .. sourcecode:: http

        HTTP/1.1 404 Not Found
        Vary: Accept, Cookie
        Allow: GET,HEAD,OPTIONS
        Content-Type: application/json

        {
            "detail": "Не найдено."
        }

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept, Cookie
        Allow: GET,HEAD,OPTIONS
        Content-Type: application/json

        {
            "profiles": [
                {
                    "id": 18721,
                    "user_id": 13885,
                    "master_id": null,
                    "full_name": "Азиев Амир ",
                    "country": "",
                    "city": "",
                    "phone_number": "",
                    "extra_phone_numbers": null,
                    "master_fio": "",
                    "hierarchy_id": 6,
                    "children": null
                },
                {
                    "id": 21158,
                    "user_id": 12818,
                    "master_id": null,
                    "full_name": "Василиадис Нара Vasiliadis",
                    "country": "Германия",
                    "city": "Wiesbaden",
                    "phone_number": "+491762419115",
                    "extra_phone_numbers": null,
                    "master_fio": "",
                    "hierarchy_id": 1,
                    "children": null
                },
                {
                    "id": 18864,
                    "user_id": 2251,
                    "master_id": null,
                    "full_name": "Прохода Ирина Анатольевна",
                    "country": "Украина",
                    "city": "Киев",
                    "phone_number": "+380675606516",
                    "extra_phone_numbers": null,
                    "master_fio": "",
                    "hierarchy_id": 5,
                    "children": "/api/app/summits/7/users/2251/"
                }
            ],
            "hierarchies": [
                {
                    "id": 9,
                    "title": "Гость",
                    "level": 0
                },
                {
                    "id": 1,
                    "title": "Прихожанин",
                    "level": 0
                },
                {
                    "id": 2,
                    "title": "Лидер",
                    "level": 1
                },
                {
                    "id": 4,
                    "title": "Пастор",
                    "level": 2
                },
                {
                    "id": 11,
                    "title": "Сотник (Отв-й за 5 ячеек)",
                    "level": 2
                },
                {
                    "id": 3,
                    "title": "Сотник",
                    "level": 2
                },
                {
                    "id": 12,
                    "title": "Ответственный Киев",
                    "level": 4
                },
                {
                    "id": 5,
                    "title": "Епископ",
                    "level": 4
                },
                {
                    "id": 8,
                    "title": "Старший епископ",
                    "level": 5
                },
                {
                    "id": 6,
                    "title": "Апостол",
                    "level": 6
                },
                {
                    "id": 7,
                    "title": "Архонт",
                    "level": 7
                }
            ]
        }

    :statuscode 200: no error
    :statuscode 403: not auth
    :statuscode 404: summit does not exist


List of summits
~~~~~~~~~~~~~~~

.. http:get:: /api/app/summits/

    List of summits

    **Example request**:

    .. sourcecode:: http

        GET /api/app/summits/ HTTP/1.1
        Host: vocrm.org
        Accept: application/json


    **Example response (invalid token)**:

    .. sourcecode:: http

        HTTP/1.1 403 Forbidden
        Vary: Accept, Cookie
        Allow: GET,HEAD,OPTIONS
        Content-Type: application/json

        {
            "detail": "Недопустимый токен."
        }

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept, Cookie
        Allow: GET,HEAD,OPTIONS
        Content-Type: application/json

        [
            {
                "title": "Колледж",
                "summits": [
                    {
                        "id": 7,
                        "start_date": "19.06.2017",
                        "end_date": "14.07.2017",
                        "description": "2017"
                    },
                    {
                        "id": 1,
                        "start_date": "04.07.2016",
                        "end_date": "29.07.2016",
                        "description": "2016"
                    }
                ]
            },
            {
                "title": "Четвертое измерение",
                "summits": [
                    {
                        "id": 4,
                        "start_date": "05.12.2016",
                        "end_date": "07.12.2016",
                        "description": "Киев. 5-7 декабря 2016г."
                    },
                    {
                        "id": 2,
                        "start_date": "31.03.2016",
                        "end_date": "02.04.2016",
                        "description": "Киев. Весна 2016г."
                    }
                ]
            },
            {
                "title": "Облако Свидетелей",
                "summits": [
                    {
                        "id": 3,
                        "start_date": "07.10.2016",
                        "end_date": "08.10.2016",
                        "description": ""
                    }
                ]
            },
            {
                "title": "Академия пасторства",
                "summits": [
                    {
                        "id": 5,
                        "start_date": "03.10.2016",
                        "end_date": "25.11.2016",
                        "description": "Седьмой поток"
                    },
                    {
                        "id": 6,
                        "start_date": "06.02.2017",
                        "end_date": "31.03.2017",
                        "description": "Восьмой поток"
                    }
                ]
            }
        ]

    :statuscode 200: no error
    :statuscode 403: not auth

