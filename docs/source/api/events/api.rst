===============
Events REST API
===============



Meetings Report Create
----------------------

    Meetings - is a events that are held by home groups.
    For default Meetings reports create and verification at the beginning of every week.
    Meetings reports created for each HomeGroup objects and each event type.
    ``Meeting objects`` may be ``three types``:

        -   ``service``
        -   ``home group``
        -   ``night``

    All Meeting objects have a ``Meeting.status`` field, we have ``three different statuses``:

        -   ``in_progress = int(1)``
        -   ``submitted = int(2)``
        -   ``expired = int(3)``

    ``Meeting reports`` will be ``created automatically`` by python Celery scheduler.
    To create reports in the manual mode ``POST`` required data to next API view:
    If the date field is missing in the POST request, for ``default`` will be set the date ``today``.

    If HomeGroup leader have a reports with status ``expired = int(3)``
    he don`t may fill reports with another statuses. He must submit first all expired reports.
    The following field is responsible for this:

        -   ``can_submit``: True if MeetingReport owner can submit report, else False.
        -   ``cant_submit_cause``: message to user, why report can't be submit.
        For default - because he have reports with status ``expired``.


    **Example request**:

    .. sourcecode:: http

        POST /api/v1.0/events/home_meetings HTTP/1.1
        Host: vocrm.org
        Content-Type: application/json
        Vary: Accept

        {
            "home_group": 24,
            "owner": 15188,
            "type": 2,
            "date": "2017-07-03"
        }

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 201 Created
        Allow: GET, POST, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "id": 306,
            "home_group": 24,
            "owner": 15188,
            "type": 2,
            "date": "03.07.2017",
            "total_sum": "0",
            "status": 1,
            "can_submit": true,
            "cant_submit_cause": ""
        }


    Immediately, after Meeting report create, his status is ``in_progress = 1``.
    All API list views ``paginated with 30 objects`` per page.
    To ``GET`` all Meeting objects use next API request:

    **Example request (GET all Meeting objects)**:

    .. sourcecode:: http

        GET /api/v1.0/events/home_meetings/ HTTP/1.1
        Host: vocrm.org
        Accept: application/json


    **Example response:**

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, POST, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
        "result": [
            {
                "id": 306,
                "home_group": {
                    "id": 24,
                    "title": "Домашняя Группа №2"
                },
                "owner": {
                    "id": 15188,
                    "fullname": "  test12345"
                },
                "type": {
                    "id": 2,
                    "code": "home",
                    "name": "Домашняя Группа"
                },
                "date": "03.07.2017",
                "total_sum": "0",
                "status": "in_progress",
                "can_submit": true,
                "cant_submit_cause": "",
                "phone_number": "",
                "visitors_attended": 0,
                "visitors_absent": 0,
                "link": "/events/home/reports/306/"
            },
            {
                "id": 305,
                "home_group": {
                    "id": 23,
                    "title": "Домашняя Группа №1"
                },
                "owner": {
                    "id": 15192,
                    "fullname": "  test1234"
                },
                "type": {
                    "id": 1,
                    "code": "service",
                    "name": "Воскресное Служение"
                },
                "date": "15.06.2017",
                "total_sum": "0",
                "status": "submitted",
                "can_submit": true,
                "cant_submit_cause": "",
                "phone_number": "",
                "visitors_attended": 0,
                "visitors_absent": 0,
                "link": "/events/home/reports/305/"
            }]
        }

    ``link`` - it is a link to created object.



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
        - query <string> ``search_title``: search by ``id``, ``home_group.title``, ``leader.fio``
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
                    "visitors_absent": 1,
                    "can_submit": true,
                    "cant_submit_cause": ""
                }
            ]
        }




Meeting Report Submit
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
        Allow: GET, POST, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "links": {
                "next": null,
                "previous": null
            },
            "results": [
                {
                    "user_id": 1,
                    "fullname": "Аккаунт Технический №1",
                    "spiritual_level": "Junior",
                    "phone_number": "+38099664224"
                },
                {
                    "user_id": 4,
                    "fullname": "Аккаунт Технический №4",
                    "spiritual_level": "Baby",
                    "phone_number": ""
                },
                {
                    "user_id": 10,
                    "fullname": "Аккаунт Технический №10",
                    "spiritual_level": "Baby",
                    "phone_number": ""
                },
                {
                    "user_id": 9,
                    "fullname": "Аккаунт Технический №9",
                    "spiritual_level": "Baby",
                    "phone_number": ""
                },
                {
                    "user_id": 5,
                    "fullname": "Аккаунт Технический №5",
                    "spiritual_level": "Baby",
                    "phone_number": ""
                }
            ]
        }

    Before submit Meeting object status automatically changed from ``in_progress = 1`` to ``submitted = 2``.
    For ``submit`` Meeting, client must ``POST`` request with required data to next API view.

    The ``date`` field is ``limited to a week`` when the report was created.

    **Fillable fields for this request:**

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

        POST /api/v1.0/events/home_meetings/306/submit/  HTTP/1.1
        Host: vocrm.org
        Accept: application/json
        Content-type: application/json

        {
            "attends": [
                  {
                    "user_id": 1,
                    "attended": true,
                    "note": "Present"
                  },
                  {
                    "user_id": 4,
                    "attended": true,
                    "note": "Not visited"
                  },
                  {
                    "user_id": 10,
                    "attended": true,
                    "note": "Not visited"
                  },
                  {
                    "user_id": 9,
                    "attended": true,
                    "note": "Not visited"
                  },
                  {
                    "user_id": 5,
                    "attended": true,
                    "note": "Not visited"
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
            "message": "Отчет Домашней Группы успешно подан."
        }

    **Example created object**

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: POST, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "id": 307,
            "home_group": {
                "id": 24,
                "title": "Домашняя Группа №2"
            },
            "owner": {
                "id": 15188,
                "fullname": "  test12345"
            },
            "type": {
                "id": 2,
                "code": "home",
                "name": "Домашняя Группа"
            },
            "date": "10.07.2017",
            "total_sum": "0",
            "status": 2,
            "can_submit": true,
            "cant_submit_cause": "",
            "attends": [
                {
                    "id": 414,
                    "user_id": 1,
                    "fullname": "Аккаунт Технический №1",
                    "spiritual_level": "Junior",
                    "attended": true,
                    "note": "Present",
                    "phone_number": "+38099664224"
                },
                {
                    "id": 415,
                    "user_id": 4,
                    "fullname": "Аккаунт Технический №4",
                    "spiritual_level": "Baby",
                    "attended": true,
                    "note": "Not visited",
                    "phone_number": ""
                },
                {
                    "id": 416,
                    "user_id": 10,
                    "fullname": "Аккаунт Технический №10",
                    "spiritual_level": "Baby",
                    "attended": true,
                    "note": "Not visited",
                    "phone_number": ""
                },
                {
                    "id": 417,
                    "user_id": 9,
                    "fullname": "Аккаунт Технический №9",
                    "spiritual_level": "Baby",
                    "attended": true,
                    "note": "Not visited",
                    "phone_number": ""
                },
                {
                    "id": 418,
                    "user_id": 5,
                    "fullname": "Аккаунт Технический №5",
                    "spiritual_level": "Baby",
                    "attended": true,
                    "note": "Not visited",
                    "phone_number": ""
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
    The ``date`` field is ``limited to a week`` when the report was created.

    **Example request**:

    .. sourcecode:: http

        PUT /api/v1.0/events/home_meetings/<id=165> HTTP/1.1
        Host: vocrm.org
        Accept: application/json
        content-type: application/json

        {
            "date": "2017-07-04",
            "total_sum": "35000",
            "attends": [
                {
                    "id": 409,
                    "user_id": 1,
                    "attended": false,
                    "note": "Update Comment"
                },
                {
                    "id": 410,
                    "user_id": 4,
                    "attended": false,
                    "note": "Update Comment"
                },
                {
                    "id": 411,
                    "user_id": 10,
                    "attended": false,
                    "note": "Update Comment"
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
            "message": "Отчет Домашней Группы успешно изменен."
        }


    **Example updated object**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, PUT, PATCH, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "id": 306,
            "home_group": {
                "id": 24,
                "title": "Домашняя Группа №2"
            },
            "owner": {
                "id": 15188,
                "fullname": "  test12345"
            },
            "type": {
                "id": 2,
                "code": "home",
                "name": "Домашняя Группа"
            },
            "date": "04.07.2017",
            "total_sum": "35000",
            "status": 2,
            "can_submit": true,
            "cant_submit_cause": "",
            "attends": [
                {
                    "id": 412,
                    "user_id": 9,
                    "fullname": "Аккаунт Технический №9",
                    "spiritual_level": "Baby",
                    "attended": true,
                    "note": "Not visited",
                    "phone_number": ""
                },
                {
                    "id": 413,
                    "user_id": 5,
                    "fullname": "Аккаунт Технический №5",
                    "spiritual_level": "Baby",
                    "attended": true,
                    "note": "Not visited",
                    "phone_number": ""
                },
                {
                    "id": 409,
                    "user_id": 1,
                    "fullname": "Аккаунт Технический №1",
                    "spiritual_level": "Junior",
                    "attended": false,
                    "note": "Update Comment",
                    "phone_number": "+38099664224"
                },
                {
                    "id": 410,
                    "user_id": 4,
                    "fullname": "Аккаунт Технический №4",
                    "spiritual_level": "Baby",
                    "attended": false,
                    "note": "Update Comment",
                    "phone_number": ""
                },
                {
                    "id": 411,
                    "user_id": 10,
                    "fullname": "Аккаунт Технический №10",
                    "spiritual_level": "Baby",
                    "attended": false,
                    "note": "Update Comment",
                    "phone_number": ""
                }
            ]
        }


    **Example request (reports with status ``in_progress`` or ``expired``)**:

    .. sourcecode:: http

        GET /api/v1.0/events/home_meetings/306 HTTP/1.1
        Host: vocrm.org
        Accept: application/json
        content-type: application/json

        {
            "date": "2017-07-03",
            "total_sum": "22222",
            "attends": []
        }

    **Example response (Bad request)**

    .. sourcecode:: http

        HTTP/1.1 400 Bad Request
        Allow: GET, PUT, PATCH, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "detail": "Невозможно обновить методом UPDATE.
                        Отчет - {Отчет ДГ - Домашняя Группа №2 (Домашняя Группа): 15 June 2017} еще небыл подан."
        }



Meetings Statistics
___________________

    Meetings supports ``GET`` statistics API witch consists a summary values for requested query.

    **Meetings statistics contains next data**:

        -   query <int> ``total_visitors``: total Meetings visitors count
        -   query <int> ``total_visits``: count of visitors that attended
        -   query <int> ``total_absent``: count of visitors that was absent
        -   query <float> ``total_donations``: sum of all donations
        -   query <int> ``reports_in_progress``: count of reports with status - ``in_progress = 1``
        -   query <int> ``reports_submitted``: count of reports with status - ``submitted = 2``
        -   query <int> ``reports_expired``: count of reports with status - ``expired = 3``

    **Example request**:

    .. sourcecode:: http

        GET /api/v1.0/events/home_meetings/statistics HTTP/1.1
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




Meetings Filters
________________

    Filters works in statistics and object lists views.
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

        GET /api/v1.0/events/home_meetings/statistics/?department=1&home_group=23&owner=15192 HTTP/1.1
                        &type=2&status=2&from_date=2016-01-01&to_date=2017-10-10
        Host: vocrm.org
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "total_visitors": 5,
            "total_visits": 1,
            "total_absent": 4,
            "total_donations": "1200",
            "new_repentance": 4,
            "reports_in_progress": 0,
            "reports_submitted": 1,
            "reports_expired": 0
        }




Meetings Table Columns
______________________

    **Fields in paginated response**:

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
                    "title": "Лидер Домашней Группы"
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




Visitors Table Columns, api/v1.0/events/home_meetings/<int(id)>/visitors
------------------------------------------------------------------------

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept


        {
            "table_columns": {
                "attended": {
                    "ordering_title": "attended",
                    "active": true,
                    "editable": true,
                    "title": "Присутствие",
                    "number": 1,
                    "id": 815441
                },
                "user": {
                    "ordering_title": "user__last_name",
                    "active": true,
                    "editable": false,
                    "title": "ФИО",
                    "number": 2,
                    "id": 815442
                },
                "spiritual_level": {
                    "ordering_title": "user__last_name",
                    "active": true,
                    "editable": true,
                    "title": "Духовный Уровень",
                    "number": 3,
                    "id": 815443
                },
                "phone_number": {
                    "ordering_title": "user__phone_number",
                    "active": true,
                    "editable": true,
                    "title": "Телефонный номер",
                    "number": 4,
                    "id": 815444
                },
                "note": {
                    "ordering_title": "note",
                    "active": true,
                    "editable": true,
                    "title": "Комментарий",
                    "number": 5,
                    "id": 815445
                }
            }
        }





Church Reports Create
_____________________

    Church Report - is a report that are submitted by pastor of the Church.
    Church reports created ``automatically`` to every Church ``every week at monday`` by django Celery scheduler.
    All Church Reports have a ``ChurchReport.status`` field, we have three different statuses:

    -   ``in_progress = int(1)``
    -   ``submitted = int(2)``
    -   ``expired = int(3)``

    When report created his status is ``in_progress``.
    To create report in manual mode - ``POST`` required data to next API view:
    If not ``date, today`` will be ``set automatically``.
    ``link`` - link to objects.

    **Example request**:

    .. sourcecode:: http

        POST /api/v1.0/events/church_reports/  HTTP/1.1
        Host: vocrm.org
        Content-Type: application/json
        Vary: Accept

        {
            "pastor": 15160,
            "church": 18
        }

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 201 Created
        Allow: GET, POST, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "id": 62,
            "pastor": 15160,
            "church": 18,
            "date": "03.07.2017",
            "status": 1,
            "link": "/events/church/reports/62/",
            "total_peoples": 0,
            "total_new_peoples": 0,
            "total_repentance": 0,
            "total_tithe": "0",
            "total_donations": "0",
            "total_pastor_tithe": "0",
            "currency_donations": "",
            "transfer_payments": "0.0",
            "can_submit": true,
            "cant_submit_cause": "",
            "comment": ""
        }




Church Report Submit
--------------------

    The ``date`` field is ``limited to a week`` when the report was created.
    For submit Meeting object and change status from ``in_progress = 1`` to ``submitted = 2`` Pastor of the Church
    must ``POST`` their ``report`` with required data to next ``API url``:

    **Fillable fields for this request:**

        -   <datetime> ``date``: Date of the Church meeting, ``required = True``
        -   <int> ``total_peoples``: Total people on meeting, ``required = True``
        -   <int> ``total_repentance``: Total new repentance, ``required = True``
        -   <float> ``total_tithe``: Total sum of tithe, ``required = True``
        -   <float> ``total_donations``: Total sun of donations, ``required = True``
        -   <float> ``total_pastor_tithe``: Sum of Pastor tithe, ``required = True``
        -   <str> ``currency_donations``: Total donations in any currency, ``required = False``

    **All other required fields automatically adds in each Meeting object:**

        -   <int> ``church``: ChurchReport.church
        -   <int> ``pastor``: ChurchReport.pastor
        -   <int> ``status``: ChurchReport.status, will be changed to ``submitted = 2``


    **Example request**:

    .. sourcecode:: http

        POST /api/v1.0/events/church_reports/<id=60>/submit  HTTP/1.1
        Allow: POST, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "date": "2017-07-04",
            "total_peoples": 200,
            "total_new_peoples": 20,
            "total_repentance": 10,
            "total_tithe": 20000,
            "total_donations": 10000,
            "total_pastor_tithe": 3000,
            "currency_donations": "20 euro, 30$",
            "comment": ""
        }

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: POST, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "message": "Отчет Церкви успешно подан."
        }


    **Example created object**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: POST, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "id": 60,
            "pastor": {
                "id": 10,
                "fullname": "Аккаунт Технический №10"
            },
            "church": {
                "id": 25,
                "title": "Курлык Курлык"
            },
            "date": "04.07.2017",
            "status": 2,
            "link": "/events/church/reports/60/",
            "total_peoples": 200,
            "total_new_peoples": 20,
            "total_repentance": 10,
            "total_tithe": "20000",
            "total_donations": "10000",
            "total_pastor_tithe": "3000",
            "currency_donations": "20 euro, 30$",
            "transfer_payments": "0.0",
            "can_submit": true,
            "cant_submit_cause": "",
            "comment": ""
        }

    ``transfer_payments`` - automatic calculated on client and send to server.
    Meeting.status changed to ``expired = 3`` automatically,
    when next week started and Meeting report status stayed ``in_progress = 1``




Church Report Update
--------------------

    Church Reports provide a ``UPDATE`` method only for reports with Meeting.status ``submitted = 2``.
    The ``date`` field is ``limited to a week`` when the report was created.
    Fields that can be updated:

        -   ``date``
        -   ``total_peoples``
        -   ``total_new_peoples``
        -   ``total_repentance``
        -   ``total_tithe``
        -   ``total_donations``
        -   ``total_pastor_tithe``
        -   ``currency_donations``
        -   ``comment``

    To ``UPDATE`` a Church Report object send request for next API view:

    **Example request**:

    .. sourcecode:: http

        PUT /api/v1.0/events/church_reports/<id=60> HTTP/1.1
        Host: vocrm.org
        Accept: application/json
        Content-type: application/json

        {
            "date": "02.07.2017",
            "link": "/events/church/reports/60/",
            "total_peoples": 333,
            "total_new_peoples": 33,
            "total_repentance": 3,
            "total_tithe": "3333",
            "total_donations": "3333",
            "total_pastor_tithe": "333",
            "currency_donations": "33 dollars",
            "comment": "three three"
        }


    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, PUT, PATCH, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "message": "Отчет Церкви успешно обновлен."
        }


    **Example updated object**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, PUT, PATCH, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "id": 60,
            "pastor": 10,
            "church": 25,
            "date": "06.07.2017",
            "status": 2,
            "link": "/events/church/reports/60/",
            "total_peoples": 333,
            "total_new_peoples": 33,
            "total_repentance": 3,
            "total_tithe": "3333",
            "total_donations": "3333",
            "total_pastor_tithe": "333",
            "currency_donations": "33 dollars",
            "transfer_payments": "0.0",
            "can_submit": true,
            "cant_submit_cause": "",
            "comment": "three three"
        }




Church Reports Filters
----------------------

    Filters works in statistics and object lists views.
    **Church_reports supports a filters for next query params:**

    -   query <int> ``status``: filter by Meeting status
    -   query <int> ``church``: filter by home group
    -   query <int> ``department``: filter by owner department
    -   query <int> ``church``: filter by home group church
    -   query <int> ``pastor``: filter by Meeting owner (home group leader)
    -   query <string> ``from_date, to_date``: filter by date range

    **Example response**:

    .. sourcecode:: http

        GET /api/v1.0/events/church_reports/?status=2&church=18&department=1&pastor=15160  HTTP/1.1
                        &master_tree=15160&from_date=2017-06-03&to_date=2017-06-27
        Host: vocrm.org
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "id": 60,
            "pastor": {
                "id": 10,
                "fullname": "Аккаунт Технический №10"
            },
            "church": {
                "id": 25,
                "title": "Курлык Курлык"
            },
            "date": "06.07.2017",
            "status": 2,
            "link": "/events/church/reports/60/",
            "total_peoples": 333,
            "total_new_peoples": 33,
            "total_repentance": 3,
            "total_tithe": "3333",
            "total_donations": "3333",
            "total_pastor_tithe": "333",
            "currency_donations": "33 dollars",
            "transfer_payments": "0.0",
            "can_submit": true,
            "cant_submit_cause": "",
            "comment": "three three"
        }



Church Reports Statistics
_________________________

    Meetings supports ``GET`` statistics API witch consists a summary values for requested query.

    **Meetings statistics contains next data**:

        -   query <int> ``total_peoples``
        -   query <int> ``total_new_peoples``
        -   query <int> ``total_repentance``
        -   query <float> ``total_tithe``
        -   query <float> ``total_donations``
        -   query <float> ``total_transfer_payments``
        -   query <float> ``total_pastor_tithe``

    **Example request**:

    .. sourcecode:: http

        GET /api/v1.0/events/church_reports/statistics  HTTP/1.1
        Host: vocrm.org
        Accept: application/json

    **Example response**

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "total_peoples": 20000,
            "total_new_peoples": 2000,
            "total_repentance": 1000,
            "total_tithe": "20000000",
            "total_donations": "1000000",
            "total_transfer_payments": "20",
            "total_pastor_tithe": "300000"
        }

    Also Church Reports statistics support filters by query params.

    **Example request**:

    .. sourcecode:: http

        GET http://127.0.0.1:8000/api/v1.0/events/church_reports/statistics/?status=2&church=18  HTTP/1.1
            &department=1&pastor=15160&master_tree=15160&from_date=2017-06-03&to_date=2017-06-27
        Host: vocrm.org
        Accept: application/json


    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Allow: GET, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept

        {
            "total_peoples": 20000,
            "total_new_peoples": 2000,
            "total_repentance": 1000,
            "total_tithe": "20000000",
            "total_donations": "1000000",
            "total_transfer_payments": "20",
            "total_pastor_tithe": "300000"
        }



Church Reports Table Columns
----------------------------

    **Fields in paginated response**:

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
                    "title": "Лидер Домашней Группы"
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



Celery tasks functions:
-----------------------

    -   ``create_new_meetings()`` - create new HomeMeeting objects for all ``active`` Home Groups.

    -   ``meetings_to_expired()`` - change status to ``expired = 3`` for all expired Meeting reports.

    -   ``create_church_reports()`` - create new ChurchReport objects for all ``is_open`` Churches.

    -   ``church_reports_to_expire()`` - change status to ``expired = 3`` for all expired Church reports.
