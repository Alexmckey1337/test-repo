===============
Events REST API
===============

Meetings (default reports for home groups)
------------------------------------------


Meetings Creating
-----------------

    For default Meetings objects create and verification every week.
    Meetings reports created in begin of the week for every Home Group objects for different types of meetings.
    Meeting objects may be 3 types: ``home group``, ``night`` and ``service``.

    All Meeting objects have a ``Meeting.status`` field, we have three different statuses:
    ``in_progress = 1``, ``submitted = 2`` and ``expired = 3``.

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

    Meetings objects may be `filtered` by next query params:

    .. sourcecode:: http

    :query <int> status: filter by ``status``
    :query <int> home_group: filter by ``home_group``
    :query <int> department: filter by owner HomeGroup.church ``department``
    :query <int> church: filter by ``HomeGroup.church``
    :query <int> owner: filter by report ``owner`` (home group leader)
    :query <int> type: filter by report ``type``
    :query <str> [from_date, to_date]: filter by selected ``date`` range
    :query <int> status: filter by progress ``status``

    **Example request(with all filters)**:

    .. sourcecode:: http

        GET /api/v1.0/events/home_meetings/?status=2&from_date=2016-04-01&to_date=2017-04-28&home_group=18&owner=15160&type=1&department=1 HTTP/1.1
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
    If report.type is ``service`` field `total_sum always is 0` and not editable.
    When Meeting create his status - ``in_progress = 1`` and contain next data:

    **Example of Meetings object (with status `in_progress`)**:

    .. sourcecode:: http

        HTTP/1.1 201 Created
        Allow: GET, POST, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "id": 165,
            "home_group": 18,
            "owner": 15160,
            "type": 1,
            "date": "18.04.2017",
            "status": 1,
            "total_sum": "0"
        }

    For submit Meeting object and change status from ``in_progress = 1`` to ``submitted = 2`` Meeting.owner must
    ``POST`` their report with required data and may specify a list of ``meeting visitors``.
    For default Meetings.visitors are a members of home group where Meeting.owner is a leader.

    To ``GET Meeting.visitors`` use the next API view:

    **Example request**:

    .. sourcecode:: http

        GET api/v1.0/events/home_meetings/<id=158>/visitors  HTTP/1.1
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
    For ``submit`` Meeting client must ``POST`` request with required data to next API view.

    Required fields for this request:

    :<float> total_sum: ``total sum`` of money, collected on meeting, required = False, default = 0
    :<array> visitors: array with report about their ``attended``, required = True
    :<int> user: User object ``id``, required = True
    :<boolean> attended: ``True`` if visitor attended else ``False``, required = False, default = False
    :<str> note: Meeting owner ``note`` about visitors, required = False, default = ''
    :<datetime> date: ``date`` when Meeting was held, required = True

    All other fields gets automatically:

    :<int> home_group: ``Meeting.home_group``
    :<int> owner: ``Meeting.owner``
    :<int> type: ``Meeting.type``
    :<int> status: ``Meeting.status``


    **Example request**:

    .. sourcecode:: http

        POST /api/v1.0/events/home_meetings/<id=158>/submit  HTTP/1.1
        Host: vocrm.org
        Accept: application/json
        content-type: application/json

        {
            "id": 165,
            "date": "2017-04-01",
            "total_sum": "1500",
            "visitors": [
                {
                    "attends": [
                        {
                            "user": 10717,
                            "attended": true,
                            "note": "Comment"
                        }
                    ]
                },
                {
                    "attends": [
                        {
                            "user": 6977,
                            "attended": true,
                            "note": "Comment"
                        }
                    ]
                }
            ]
        }

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 201 Created
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
    When next week started and Meeting report `status` stayed ``in_progress = 1``





Meeting Report Update
_____________________

    Meetings provide a ``UPDATE`` method `only` for reports with Meeting.status ``submitted = 2``.
    Fields that can be ``update``: `date`, 'total_sum', 'attends.attended', 'attends.note'.

    To update a Meeting object send request for next API view:

    **Example request**:

    .. sourcecode:: http

        UPDATE /api/v1.0/events/home_meetings/<id=165> HTTP/1.1
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

        HTTP/1.1 201 Created
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

    **Example request (with Meeting status - `in_progress = 1` or `expired = 3`**:

    .. sourcecode:: http

        UPDATE /api/v1.0/events/home_meetings HTTP/1.1
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
            Отчет - {Отчет ДГ - Домашняя Группа №1 (Ночная Молитва): 14 April 2017} еще небыл подан."
        ]




Meetings Statistics
___________________

    Meetings supports `GET` statistics API witch consists a summary values for requested query.

    ``Meetings statistics`` contains next data:

    :int total_visitors: ``total visitors count`` in `all Meetings on requested params`
    :int total_visits: count of Meeting visitors that ``attended``
    :int total_absent: count of Meeting visitors that was ``absent``
    :decemal total_donations: sum of all Meetings ``donations``
    :int reports_in_progress: count of Meetings reports with status - ``in_progress = 1``
    :int reports_submitted: count of Meetings reports with status - ``submitted = 1``
    :int reports_expired: count of Meetings reports with status - ``expired = 3``

    **Example request**:

    .. sourcecode:: http

        GET /api/v1.0/events/home_groups/statistics HTTP/1.1
        Host: vocrm.org
        Accept: application/json

    **Example response**

    .. sourcecode:: http

        GET HTTP/1.1 200 OK
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

    Meetings reports supports a ``filters`` for next query params:

    :query <int> status: filter by ``status``
    :query <int> home_group: filter by ``home_group``
    :query <int> department: filter by owner HomeGroup.church ``department``
    :query <int> church: filter by ``HomeGroup.church``
    :query <int> owner: filter by ``owner`` (home group leader)
    :query <int> type: filter by ``type``
    :query <str> [from_date, to_date]: filter by selected ``date`` range
    :query <int> status: filter by progress ``status``

    **Example response**:

    .. sourcecode:: http

        GET HTTP/1.1 /api/v1.0/http://127.0.0.1:8000/api/v1.0/events/home_meetings/statistics/?department=1&church=26&home_group=18&owner=15160&type=1&from_date=2016-01-01&to_date=2017-05-05&status=2
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
