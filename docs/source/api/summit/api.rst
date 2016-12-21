===============
Summit REST API
===============

Summit
------

.. http:get:: /api/v1.0/summit/(int:summit_id)/

   Information about ``Summit`` with id = ``summit_id``.

   **Example request**:

   .. sourcecode:: http

      GET /api/v1.0/summit/4/ HTTP/1.1
      Host: vocrm.org
      Accept: application/json

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept, Cookie
      Allow: GET,HEAD,OPTIONS
      Content-Type: application/json

      {
        "id": 4,
        "start_date": "14.11.2016",
        "end_date": "14.11.2016",
        "title": "Колледж",
        "description": "star wars",
        "lessons": [
          5,
          6,
          7
        ],
        "club_name": "",
        "full_cost": "0",
        "special_cost": null
      }

   **Example response (Not Found)**:

   .. sourcecode:: http

      HTTP/1.1 404 Not Found
      Vary: Accept, Cookie
      Allow: GET,HEAD,OPTIONS
      Content-Type: application/json

      {
        "detail": "Не найдено."
      }

   :reqheader Accept: the response content type depends on
                          :mailheader:`Accept` header
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 200: no error
       :statuscode 404: there's no summit


.. http:get:: /api/v1.0/summit/

   List of summits (order by ``-start_date`` desc). Pagination by 30 summits per page.

   **Example request**:

   .. sourcecode:: http

      GET /api/v1.0/summit/ HTTP/1.1
      Host: vocrm.org
      Accept: application/json

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept, Cookie
      Allow: GET,HEAD,OPTIONS
      Content-Type: application/json

      {
        "count": 2,
        "next": null,
        "previous": null,
        "results": [
          {
            "id": 4,
            "start_date": "14.11.2016",
            "end_date": "14.11.2016",
            "title": "Колледж",
            "description": "star wars",
            "lessons": [
              5,
              6,
              7
            ],
            "club_name": "",
            "full_cost": "0",
            "special_cost": null
          },
          {
            "id": 3,
            "start_date": "07.10.2016",
            "end_date": "08.10.2016",
            "title": "Облако Свидетелей",
            "description": "",
            "lessons": [
              8,
              9,
              10
            ],
            "club_name": "",
            "full_cost": "0",
            "special_cost": null
          }
        ]
      }

   :query int page: page number (one of ``int`` or ``last``). default is 1
   :query int type: filter by ``summit_type_id``
   :reqheader Accept: the response content type depends on
                                :mailheader:`Accept` header
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 200: no error


.. http:get:: /api/v1.0/summit/(int:summit_id)/lessons/

   List of the lessons of ``Summit`` with ``id = summit_id``.

   **Example request**:

   .. sourcecode:: http

      GET /api/v1.0/summit/4/lessons/ HTTP/1.1
      Host: vocrm.org
      Accept: application/json

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept, Cookie
      Allow: GET,HEAD,OPTIONS
      Content-Type: application/json

      [
        {
          "summit": 4,
          "name": "1",
          "viewers": []
        },
        {
          "summit": 4,
          "name": "11",
          "viewers": []
        },
        {
          "summit": 4,
          "name": "111",
          "viewers": []
        }
      ]

   **Example response (Not Found)**:

   .. sourcecode:: http

      HTTP/1.1 404 Not Found
      Vary: Accept, Cookie
      Allow: GET,HEAD,OPTIONS
      Content-Type: application/json

      {
        "detail": "Не найдено."
      }

   :reqheader Accept: the response content type depends on
                                      :mailheader:`Accept` header
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 200: no error
       :statuscode 404: there's no summit


.. http:post:: /api/v1.0/summit/(int:summit_id)/add_lesson/

   Create new lesson for ``Summit`` with ``id = summit_id``.
   Name of the lesson must be unique for summit.

   **Example request**:

   .. sourcecode:: http

      POST /api/v1.0/summit/4/add_lesson/ HTTP/1.1
      Host: vocrm.org
      Accept: application/json
      content-type: application/x-www-form-urlencoded
      content-length: 10

      name=test4

   **Example response (Good request)**:

   .. sourcecode:: http

      HTTP/1.1 201 Created
      Vary: Accept, Cookie
      Allow: POST,OPTIONS
      Content-Type: application/json

      {
        "summit": 4,
        "name": "test4",
        "viewers": []
      }

   **Example response (Bad request 1)**:

   .. sourcecode:: http

      HTTP/1.1 400 Bad Request
      Vary: Accept, Cookie
      Allow: POST,OPTIONS
      Content-Type: application/json

      {
        "non_field_errors": [
          "Поля name, summit должны производить массив с уникальными значениями."
        ]
      }

   **Example response (Bad request 2)**:

   .. sourcecode:: http

      HTTP/1.1 400 Bad Request
      Vary: Accept, Cookie
      Allow: POST,OPTIONS
      Content-Type: application/json

      {
        "summit": [
          "Недопустимый первичный ключ "4" - объект не существует."
        ]
      }

   :form name: lesson name
       :reqheader Accept: the response content type depends on
                                            :mailheader:`Accept` header
   :reqheader Content-Type: one of ``application/x-www-form-urlencoded``,
                            ``application/json``, ``multipart/form-data``
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 201: lesson created
       :statuscode 400: bad request — summit don't exist or pair ``(summit, lesson.name)`` not unique
   :statuscode 404: there's no summit


.. http:get:: /api/v1.0/summit/(int:summit_id)/consultants/

   List of the consultants of ``Summit`` with ``id = summit_id``.

   **Example request**:

   .. sourcecode:: http

      GET /api/v1.0/summit/4/consultants/ HTTP/1.1
      Host: vocrm.org
      Accept: application/json

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept, Cookie
      Allow: GET,HEAD,OPTIONS
      Content-Type: application/json

      [
        {
          "id": 13659,
          "role": 20,
          "user": {
            "id": 13337,
            "fullname": "Ivanov Ivan Ivanovich"
          }
        },
        {
          "id": 13665,
          "role": 20,
          "user": {
            "id": 13350,
            "fullname": "Super Mario Brother"
          }
        }
      ]

   **Example response (Not Found)**:

   .. sourcecode:: http

      HTTP/1.1 404 Not Found
      Vary: Accept, Cookie
      Allow: GET,HEAD,OPTIONS
      Content-Type: application/json

      {
        "detail": "Не найдено."
      }

   :reqheader Accept: the response content type depends on
                                            :mailheader:`Accept` header
   :resheader Content-Type: this depends on :mailheader:`Accept`
                            header of request
   :statuscode 200: no error
       :statuscode 404: there's no summit


.. http:post:: /api/v1.0/summit/(int:summit_id)/add_consultant/

   Set visitor of ``Summit`` as ``Consultant`` on this summit.
   Only ``Supervisor`` of ``Summit`` can set consultants.

   **Example request**:

   .. sourcecode:: http

      POST /api/v1.0/summit/4/add_consultant/ HTTP/1.1
      Host: vocrm.org
      Accept: application/json
      content-type: application/x-www-form-urlencoded
      content-length: 14

      anket_id=13659

   **Example response (Good request)**:

   .. sourcecode:: http

      HTTP/1.1 201 Created
      Vary: Accept, Cookie
      Allow: POST,OPTIONS
      Content-Type: application/json

      {
        "consultant_id": "13659",
        "action": "added",
        "summit_id": 4
      }

   **Example response (Bad request 1)**:

   .. sourcecode:: http

      HTTP/1.1 400 Bad Request
      Vary: Accept, Cookie
      Allow: POST,OPTIONS
      Content-Type: application/json

      {
        "result": "Выбранная анкета не соответствует данному саммиту."
      }

   **Example response (Bad request 2)**:

   .. sourcecode:: http

      HTTP/1.1 404 Not Found
      Vary: Accept, Cookie
      Allow: POST,OPTIONS
      Content-Type: application/x-www-form-urlencoded

      {
        "detail": "Не найдено."
      }

   **Example response (Bad request 3)**:

   .. sourcecode:: http

      HTTP/1.1 403 Forbidden
      Vary: Accept, Cookie
      Allow: POST,OPTIONS
      Content-Type: application/x-www-form-urlencoded

      {
        "result": "У вас нет прав для добавления консультантов."
      }

   :form anket_id: visitor id
       :reqheader Accept: the response content type depends on
                                                  :http:header:`Accept` header
   :reqheader Content-Type: one of ``application/x-www-form-urlencoded``,
                            ``application/json``, ``multipart/form-data``
   :resheader Content-Type: this depends on :http:header:`Accept`
                            header of request
   :statuscode 201: created consultant
       :statuscode 404: there's no summit
       :statuscode 400: bad request — selected summit don't have anket with id = ``anket_id``
   :statuscode 403: current user is not ``Supervisor`` of this summit


.. http:post:: /api/v1.0/summit/(int:summit_id)/del_consultant/

   Set visitor of ``Summit`` as ``Visitor`` on this summit.
   Only ``Supervisor`` of ``Summit`` can delete consultants.

   **Example request**:

   .. sourcecode:: http

      POST /api/v1.0/summit/4/del_consultant/ HTTP/1.1
      Host: vocrm.org
      Accept: application/json
      content-type: application/x-www-form-urlencoded
      content-length: 14

      anket_id=13659

   **Example response (Good request)**:

   .. sourcecode:: http

      HTTP/1.1 201 Created
      Vary: Accept, Cookie
      Allow: POST,OPTIONS
      Content-Type: application/json

      {
        "consultant_id": "13659",
        "action": "removed",
        "summit_id": 4
      }

   **Example response (Bad request 1)**:

   .. sourcecode:: http

      HTTP/1.1 400 Bad Request
      Vary: Accept, Cookie
      Allow: POST,OPTIONS
      Content-Type: application/json

      {
        "result": "Выбранная анкета не соответствует данному саммиту."
      }

   **Example response (Bad request 2)**:

   .. sourcecode:: http

      HTTP/1.1 404 Not Found
      Vary: Accept, Cookie
      Allow: POST,OPTIONS
      Content-Type: application/x-www-form-urlencoded

      {
        "detail": "Не найдено."
      }

   **Example response (Bad request 3)**:

   .. sourcecode:: http

      HTTP/1.1 403 Forbidden
      Vary: Accept, Cookie
      Allow: POST,OPTIONS
      Content-Type: application/x-www-form-urlencoded

      {
        "result": "У вас нет прав для удаления консультантов."
      }

   :form anket_id: visitor id
       :reqheader Accept: the response content type depends on
                                                        :http:header:`Accept` header
   :reqheader Content-Type: one of ``application/x-www-form-urlencoded``,
                            ``application/json``, ``multipart/form-data``
   :resheader Content-Type: this depends on :http:header:`Accept`
                            header of request
   :statuscode 201: created consultant
       :statuscode 404: there's no summit
       :statuscode 400: bad request — selected summit don't have anket with id = ``anket_id``
   :statuscode 403: current user is not ``Supervisor`` of this summit
