===============
Events REST API
===============




Meetings Report Create
----------------------

    Meetings - is a events that are held by home groups.
    For default Meetings reports create and verification at the beginning of every week.
    Meetings reports created for each HomeGroup objects and each event type.
    Meeting objects may be 3 types:

        -   ``service``
        -   ``home group``
        -   ``night``

    All Meeting objects have a ``Meeting.status`` field, we have three different statuses:

        -   ``in_progress = int(1)``
        -   ``submitted = int(2)``
        -   ``expired = int(3)``

    Meeting reports will be created automatically by python Celery scheduler.
    To create reports in the manual mode ``POST`` required data to next API view:
    If the date field is missing in the POST request, for ``default`` will be set the date ``today``.

    **Example request**:

    .. sourcecode:: http

        POST /api/v1.0/events/home_meetings HTTP/1.1
        Host: vocrm.org
        Accept: application/json

        {
            "home_group": 18,
            "owner": 15160,
            "type": 2,
            "date": "2017-03-04"
        }

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 201 Created
        Allow: GET, POST, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "id": 171,
            "home_group": 18,
            "owner": 15160,
            "type": 2,
            "date": "04.03.2017",
            "total_sum": "0",
            "status": 1
        }




    Immediately, after Meeting report create, his status is ``in_progress = 1``.
    All API list views ``paginated with 30 objects`` per page.
    To ``GET`` all Meeting objects use next API request:

    **Example request (GET all Meeting objects)**:

    .. sourcecode:: http

        GET /api/v1.0/events/home_meetings HTTP/1.1
        Host: vocrm.org
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, POST, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "count": 1,
            "results": [
                {
                    "id": 165,
                    "home_group": {
                        "id": 18,
                        "title": "Домашнаяя Группа №3"
                    },
                    "owner": {
                        "id": 15160,
                        "fullname": "П Ростислав С"
                    },
                    "type": {
                        "id": 1,
                        "code": "service"
                    },
                    "date": "01.04.2017",
                    "status": "submitted",
                    "total_sum": "1500",
                    "phone_number": "093-093-22-22",
                    "visitors_attended": 2,
                    "visitors_absent": 0
                }
            ],
            "links": {
                "next": null,
                "previous": null
            }
        }




Meetings Filters
________________

    **Meetings objects may be filtering by next query params:**

        - query <int> ``status``: filter by status
        - query <int> ``home_group``: filter by home_group
        - query <int> ``department``: filter by owner HomeGroup.church department
        - query <int> ``church``: filter by HomeGroup.church
        - query <int> ``owner``: filter by report owner (home group leader)
        - query <int> ``type``: filter by report type
        - query <string> ``[from_date, to_date]``: filter by range
        - query <int> ``status``: filter by progress status

    **Example request(with all filters)**:

    .. sourcecode:: http

        GET /api/v1.0/events/home_meetings/?status=2&from_date=2016-04-01&to_date=2017-04-28 HTTP/1.1
                                            &home_group=18&owner=15160&type=1&department=1
        Host: vocrm.org
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, POST, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "links": {
                "previous": null,
                "next": null
            },
            "count": 1,
            "results": [
                {
                    "id": 150,
                    "home_group": {
                        "id": 18,
                        "title": "Домашнаяя Группа №3"
                    },
                    "owner": {
                        "id": 15160,
                        "fullname": "П Ростислав С"
                    },
                    "type": {
                        "id": 1,
                        "code": "service"
                    },
                    "date": "01.01.2017",
                    "status": 2,
                    "total_sum": "222",
                    "phone_number": "093-093-22-22",
                    "visitors_attended": 1,
                    "visitors_absent": 1
                }
            ]
        }




Meeting report submit
_____________________

    Before report submit, for default, all Meeting objects ``total_sum`` is 0.
    If report.type is ``service`` field ``total_sum`` always is 0 and can`t be changed.

    For submit Meeting object and change status from ``in_progress = 1`` to ``submitted = 2`` Meeting owner must
    ``POST`` their report with required data and may specify a list of ``meeting visitors``.
    For default Meetings visitors are a members of home group where Meeting owner is a leader.
    To ``GET Meeting.visitors`` use the next API view:

    **Example request**:

    .. sourcecode:: http

        GET api/v1.0/events/home_meetings/<id=158>/visitors HTTP/1.1
        Host: vocrm.org
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        [
            {
                "id": 10717,
                "fullname": "Красная Юлия Евгеньевна"
            },
            {
                "id": 6977,
                "fullname": "Краснова Надежда Васильевна"
            }
        ]

    Before submit Meeting object status automatically changed from ``in_progress = 1`` to ``submitted = 2``.
    For ``submit`` Meeting, client must ``POST`` request with required data to next API view.

    **Required fields for this request:**

        -   <float> ``total_sum``: total sum of money, collected on meeting, required = False, default = 0
        -   <array> ``attends``: array with report about their attended, required = True
        -   <int> ``user``: User object <id>, required = True
        -   <boolean> ``attended``: `True` if visitor attended else `False`, required = False, default = False
        -   <str> ``note``: Meeting owner note about visitors, required = False, default = ''
        -   <datetime> ``date``: date when Meeting was held, required = True

    **All other required fields automatically adds in each Meeting object:**

        -   <int> ``home_group``: Meeting.home_group
        -   <int> ``owner``: Meeting.owner
        -   <int> ``type``: Meeting.type
        -   <int> ``status``: Meeting.status

    **Example request**:

    .. sourcecode:: http

        POST /api/v1.0/events/home_meetings/<id=165>/submit  HTTP/1.1
        Host: vocrm.org
        Accept: application/json
        content-type: application/json

        {
            "id": 165,
            "date": "2017-04-01",
            "total_sum": "1500",
            "attends": [
                {
                    "id": 340,
                    "user": 10717,
                    "attended": true,
                    "note": "Comment"
                },
                {
                    "id": 341,
                    "user": 6977,
                    "attended": true,
                    "note": "Comment"
                }
            ]
        }

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: POST, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "id": 165,
            "home_group": {
                "id": 18,
                "title": "Домашнаяя Группа №3"
            },
            "owner": {
                "id": 15160,
                "fullname": "П Ростислав С"
            },
            "type": {
                "id": 1,
                "code": "service"
            },
            "date": "01.04.2017",
            "status": 2,
            "total_sum": "1500",
            "attends": [
                {
                    "id": 340,
                    "user": 10717,
                    "attended": true,
                    "note": "Comment"
                },
                {
                    "id": 341,
                    "user": 6977,
                    "attended": true,
                    "note": "Comment"
                }
            ]
        }

    Meeting.status changed to ``expired = 3`` automatically.
    When next week started and Meeting report status stayed ``in_progress = 1``





Meeting Report Update
_____________________

    Meetings provide a ``UPDATE`` method only for reports with Meeting.status ``submitted = 2``.
    Fields that can be updated:

        -   ``date`` - date when report was submitted
        -   ``total_sum`` - total sum of donations on event
        -   ``attends['attended']`` - count of visitors attends
        -   ``attends['note']`` - Meeting.owner comment about visitor

    To ``UPDATE`` a Meeting object send request for next API view:

    **Example request**:

    .. sourcecode:: http

        PUT /api/v1.0/events/home_meetings/<id=165> HTTP/1.1
        Host: vocrm.org
        Accept: application/json
        content-type: application/json

        {
            "id": 165,
            "date": "2017-04-01",
            "total_sum": "35000",
            "attends": [
                {
                    "id": 340,
                    "user": 10717,
                    "attended": false,
                    "note": "Update Comment"
                },
                {
                    "id": 341,
                    "user": 6977,
                    "attended": false,
                    "note": "Update Comment"
                }
            ]
        }


    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, PUT, PATCH, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "id": 165,
            "home_group": {
                "id": 18,
                "title": "Домашнаяя Группа №3"
            },
            "owner": {
                "id": 15160,
                "fullname": "П Ростислав С"
            },
            "type": {
                "id": 1,
                "code": "service"
            },
            "date": "01.04.2017",
            "status": 2,
            "total_sum": "35000",
            "attends": [
                {
                    "id": 340,
                    "user": 10717,
                    "attended": false,
                    "note": "Update Comment"
                },
                {
                    "id": 341,
                    "user": 6977,
                    "attended": false,
                    "note": "Update Comment"
                }
            ]
        }

    **Example request (reports with status ``in_progress`` or ``expired``)**:

    .. sourcecode:: http

        GET /api/v1.0/events/home_meetings HTTP/1.1
        Host: vocrm.org
        Accept: application/json
        content-type: application/json

        {
            "id": 166,
            "date": "2017-04-14",
            "total_sum": "15000",
            "attends": []
        }

    **Example response (Bad request)**

    .. sourcecode:: http

        HTTP/1.1 400 Bad Request
        Allow: GET, PUT, PATCH, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        [
            "Невозможно обновить методом UPDATE.
             Отчет - {Отчет ДГ - Домашняя Группа №1 (Ночная Молитва): 14 April 2017}
             еще небыл подан."
        ]




Meetings Statistics
___________________

    Meetings supports ``GET`` statistics API witch consists a summary values for requested query.

    **Meetings statistics contains next data**:

        -   query <int> ``total_visitors``: total Meetings visitors count
        -   query <int> ``total_visits``: count of visitors that attended
        -   query <int> ``total_absent``: count of visitors that was absent
        -   query <float> ``total_donations``: sum of all donations
        -   query <int> ``reports_in_progress``: count of reports with status - ``in_progress = 1``
        -   query <int> ``reports_submitted``: count of reports with status - ``submitted = 1``
        -   query <int> ``reports_expired``: count of reports with status - ``expired = 3``

    **Example request**:

    .. sourcecode:: http

        GET /api/v1.0/events/home_groups/statistics HTTP/1.1
        Host: vocrm.org
        Accept: application/json

    **Example response**

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "total_visitors": 4,
            "total_visits": 1,
            "total_absent": 3,
            "total_donations": "35000",
            "new_repentance": 0,
            "reports_in_progress": 1,
            "reports_submitted": 4,
            "reports_expired": 0
        }



Meetings Statistics Filters
___________________________

    **Meetings reports supports a filters for next query params:**

    -   query <int> ``status``: filter by Meeting status
    -   query <int> ``home_group``: filter by home group
    -   query <int> ``department``: filter by owner department
    -   query <int> ``church``: filter by home group church
    -   query <int> ``owner``: filter by Meeting owner (home group leader)
    -   query <int> ``type``: filter by Meeting type
    -   query <string> ``from_date, to_date``: filter by date range

    **Example response**:

    .. sourcecode:: http

        GET /api/v1.0/events/home_meetings/statistics/?department=1&church=26&home_group=18 HTTP/1.1
                        &owner=15160&type=1&from_date=2016-01-01&to_date=2017-05-05&status
        Host: vocrm.org
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "total_visitors": 4,
            "total_visits": 1,
            "total_absent": 3,
            "total_donations": "35000",
            "new_repentance": 4,
            "reports_in_progress": 0,
            "reports_submitted": 4,
            "reports_expired": 0
        }




Meetings Table Columns
______________________

    **Fields in pagination response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "links": {
                "next": null,
                "previous": null
            },
            "table_columns": {
                "date": {
                    "id": 815433,
                    "ordering_title": "date",
                    "active": true,
                    "number": 1,
                    "editable": false,
                    "title": "Дата создания"
                },
                "home_group": {
                    "id": 815434,
                    "ordering_title": "home_group__title",
                    "active": true,
                    "number": 2,
                    "editable": true,
                    "title": "Домашняя группа"
                },
                "owner": {
                    "id": 815435,
                    "ordering_title": "owner__last_name",
                    "active": true,
                    "number": 3,
                    "editable": true,
                    "title": "Владелец отчета"
                },
                "phone_number": {
                    "id": 815436,
                    "ordering_title": "phone_number",
                    "active": true,
                    "number": 4,
                    "editable": true,
                    "title": "Телефонный номер"
                },
                "type": {
                    "id": 815437,
                    "ordering_title": "type__code",
                    "active": true,
                    "number": 5,
                    "editable": true,
                    "title": "Тип отчета"
                },
                "visitors_attended": {
                    "id": 815438,
                    "ordering_title": "visitors_attended",
                    "active": true,
                    "number": 6,
                    "editable": true,
                    "title": "Присутствовали"
                },
                "visitors_absent": {
                    "id": 815439,
                    "ordering_title": "visitors_absent",
                    "active": true,
                    "number": 7,
                    "editable": true,
                    "title": "Отсутствовали"
                },
                "total_sum": {
                    "id": 815440,
                    "ordering_title": "total_sum",
                    "active": true,
                    "number": 8,
                    "editable": true,
                    "title": "Сумма пожертвований"
                }
            }
        }
