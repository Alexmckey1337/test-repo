===============
Events REST API
===============

Meetings (default reports for home groups)
------------------------------------------


Meetings Creating
-----------------

    For default Meetings objects was created and verification every week. Meeting objects may be 3 types
     - ``home group``, ``night`` and ``service``. Meetings created for every HomeGroup and for every type.
    For one HomeGroup object we have three Meetings in different types. Same Meetings objects have a ``status``
    field, we have three different statuses - ``in_progress = 1``, ``submitted = 2`` and ``expired = 3``.
    Immediately after Meeting create his status is ``in_progress = 1``.
    To ``GET`` all Meeting objects use next API view:

    **Example request**:

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

    Meetings objects may be filtered by next fields:

    :query int status: filter by ``status``
    :query int home_group: filter by ``home_group``
    :query int owner: filter by report ``owner`` (home group leader)
    :query int type: filter by report ``type``
    :query str [from_date, to_date]: filter by selected ``date`` range
    :query int department: filter by home groups church ``department``
    :query int status: filter by progress ``status``

    **Example request (with all active filters)**:

    .. sourcecode:: http

        GET /api/v1.0/events/home_meetings/?status=2&from_date=2016-04-01&to_date=2017-04-28
                                                    &home_group=18&owner=15160&type=1&department=1  HTTP/1.1
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

    For submit Meeting object and change status from ``in_progress`` to ``submitted`` we need to ``POST``
    report with required params and values. When Meeting created, any objects for default have a next fields:

    **Example object (with ``status = in_progress``)**

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


    To submit report, any home group owner may specify a list of meeting visitors. To ``GET meeting visitors``
    use the next API view:

    **Example request**:

    .. sourcecode:: http

        GET api/v1.0/events/home_meetings/<id=158>/visitors     HTTP/1.1
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


    For submit Meeting send ``POST`` request with required params to next API view. Before submit Meeting object
    status automatically changed from ``in_progress, 1`` to ``submitted, 2``.
    Required fields for this request:
    :decimal total_sum: ``total sum`` of money, collected on meeting, required = False, default = 0.
    :array visitors: array with report about their ``attended``, required = True.
    :int user: User object ``id``, required = True.
    :boolean attended: ``True`` if visitor attended else ``False``, required = False, default = False.
    :str note: Meeting owner ``note`` about visitors, required = False, default = ''.
    :date_field data: ``date`` when meeting was held, required = True

    **Example request**:

    .. sourcecode:: http

        POST /api/v1.0/events/home_meetings/<id=158>/submit     HTTP/1.1
        Host: vocrm.org
        Accept: application/json
        content-type: application/json

        {
            "id": 158,
            "date": "2017-04-20",
            "total_sum": "50000",
            "status": 1,
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

        HTTP 201 Created
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

    Meeting status changed to ``expired = 3`` automatically, when next week started and report Meeting
    status stayed ``in_progress``.



Meetings Statistics
___________________

    To ``GET`` statistics about Meetings.
