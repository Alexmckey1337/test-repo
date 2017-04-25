===============
Events REST API
===============

Meetings (default reports for home groups)
------------------------------------------


Meetings Creating
-----------------

    For default Meetings objects create and verification every week.
    Meeting objects may be 3 types: ``home group``, ``night`` and ``service``.
    Meetings reports create in begin of the week for every HomeGroup and for three Meeting.types.

    All Meeting objects have a `Meeting.status` field, we have three different statuses:
    ``in_progress = 1``, ``submitted = 2`` and ``expired = 3``.

    Immediately, after Meeting report create, his status is `in_progress = 1`.
    All list API views `paginated with 30 objects` per page.

    To ``GET`` all Meeting objects use next API request:

    **Example request (GET all types of Meeting objects)**:

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
            "id": 157,
            "home_group": {
                "id": 18,
                "title": "Домашнаяя Группа №3"
            },
            "owner": {
                "id": 15160,
                "fullname": "П Ростислав С"
            },
            "type": {
                "id": 2,
                "code": "home"
            },
            "date": "07.08.2017",
            "status": 2,
            "total_sum": "10000",
            "phone_number": "093-093-22-22",
            "visitors_attended": 0,
            "visitors_absent": 2
        },
        {
            "id": 155,
            "home_group": {
                "id": 18,
                "title": "Домашнаяя Группа №3"
            },
            "owner": {
                "id": 15160,
                "fullname": "П Ростислав С"
            },
            "type": {
                "id": 3,
                "code": "night"
            },
            "date": "03.03.2003",
            "status": 2,
            "total_sum": "1543",
            "phone_number": "093-093-22-22",
            "visitors_attended": 1,
            "visitors_absent": 1
        }



Meetings Filters
________________

    Meetings objects may be `filtered` by next query params:

    :query int status: filter by ``status``
    :query int home_group: filter by ``home_group``
    :query int owner: filter by report ``owner`` (home group leader)
    :query int type: filter by report ``type``
    :query str [from_date, to_date]: filter by selected ``date`` range
    :query int department: filter by owner HomeGroup.church ``department``
    :query int status: filter by progress ``status``

    **Example request(with all filters)**:

    .. sourcecode:: http

        GET  HTTP/1.1 /api/v1.0/events/home_meetings/?status=2&from_date=2016-04-01&to_date=2017-04-28&home_group=18&owner=15160&type=1&department=1
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

    When Meeting creating, all objects for default contain a next data:

    **Example of Meetings object (with status `in_progress = 1`)**:

    .. sourcecode:: http

        HTTP/1.1 201 Created
        Allow: GET, POST, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "id": 158,
            "home_group": 18,
            "owner": 15160,
            "type": 2,
            "date": "18.04.2017",
            "status": 1,
            "total_sum": "0"
        }

    For submit Meeting object and change status from ``in_progress`` to ``submitted`` Meeting owner must
    ``POST`` report with required params and may specify a list of meeting visitors.
    For default Meetings.visitors are a members of home group where Meeting.owner is a leader.

    To `GET Meeting.visitors` use the next API view:

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


    For submit Meeting send ``POST`` request with required params to next API view.
    Before submit Meeting object status automatically changed from ``in_progress = 1`` to ``submitted = 2``.

    Required fields for this request:

    :decimal total_sum: ``total sum`` of money, collected on meeting, required = False, default = 0
    :array visitors: array with report about their ``attended``, required = True
    :int user: User object ``id``, required = True
    :boolean attended: ``True`` if visitor attended else ``False``, required = False, default = False
    :str note: Meeting owner ``note`` about visitors, required = False, default = ''
    :datetime date: ``date`` when Meeting was held, required = True

    **Example request**:

    .. sourcecode:: http

        POST /api/v1.0/events/home_meetings/<id=158>/submit  HTTP/1.1
        Host: vocrm.org
        Accept: application/json
        content-type: application/json

        {
            "id": 158,
            "date": "2017-04-20",
            "total_sum": "50000",
            "visitors": [
                {
                    "attends": [
                        {
                            "user": 10717,
                            "attended": true,
                            "note": "Present"
                        }
                    ]
                },
                {
                    "attends": [
                        {
                            "user": 6977,
                            "attended": true,
                            "note": "Not visited"
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
            "id": 160,
            "home_group": {
                "id": 18,
                "title": "Домашнаяя Группа №3"
            },
            "owner": {
                "id": 15160,
                "fullname": "П Ростислав С"
            },
            "type": {
                "id": 3,
                "code": "night"
            },
            "date": "25.04.2017",
            "status": 2,
            "total_sum": "50000",
            "attends": [
                {
                    "id": 332,
                    "user": 10717,
                    "attended": true,
                    "note": "Present"
                },
                {
                    "id": 333,
                    "user": 6977,
                    "attended": true,
                    "note": "Not visited"
                }
            ]
        }

    Meeting.status changed to ``expired = 3`` automatically.
    When next week started and Meeting report `status` stayed ``in_progress = 1``



Meetings Statistics
___________________

    Meetings supports `GET` statistics API witch consists a summary values for requested query.

    ``Meetings statistics`` contains next data:

    :int total_visitors: ``total visitors count`` in all Meetings on requested params
    :int total_visits: count of Meeting visitors that ``attended``
    :int total_absent: count of Meeting visitors that was ``absent``
    :int reports_in_progress: count of Meetings reports with ``status = in_progress = 1``
    
