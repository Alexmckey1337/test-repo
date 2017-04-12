**Example response (Good request)**:

.. sourcecode:: http

    HTTP/1.1 201 Created
    Vary: Accept, Cookie
    Allow: POST,OPTIONS
    Content-Type: application/json

    {
      "sum": "153",
      "effective_sum": "189.72",
      "sum_str": "$153",
      "effective_sum_str": "189.72 грн.",
      "currency_sum": {
        "id": 1,
        "name": "Доллар США",
        "code": "usd",
        "short_name": "дол.",
        "symbol": "$"
      },
      "currency_rate": {
        "id": 2,
        "name": "Гривна",
        "code": "uah",
        "short_name": "грн.",
        "symbol": "₴"
      },
      "rate": "1.24",
      "description": "last",
      "created_at": "16.02.2017 15:44",
      "sent_date": "22.02.2000",
      "operation": "*",
      "manager": {
        "id": 13885,
        "first_name": "Bruce",
        "last_name": "Lee",
        "middle_name": ""
      }
    }

**Example response (Bad request 1)**:

.. sourcecode:: http

    HTTP/1.1 400 Bad Request
    Vary: Accept, Cookie
    Allow: POST,OPTIONS
    Content-Type: application/json

    {
      "currency_sum": [
        "Недопустимый первичный ключ \"12\" - объект не существует."
      ]
    }

**Example response (Bad request 2)**:

.. sourcecode:: http

    HTTP/1.1 400 Bad Request
    Vary: Accept, Cookie
    Allow: POST,OPTIONS
    Content-Type: application/json

    {
      "rate": [
        "Убедитесь что в числе не больше 3 знаков в дробной части."
      ]
    }

**Example response (Bad request 3)**:

.. sourcecode:: http

    HTTP/1.1 404 Not Found
    Vary: Accept, Cookie
    Allow: POST,OPTIONS
    Content-Type: application/json

    {
      "detail": "Не найдено."
    }

:form sum: sum of payment, integer, **required**
:form rate: rate of ``sum`` -> ``effective_sum``, decimal,
            format ``123.456`` or ``123.45`` or ``123.4`` or ``123``, default == 1
:form operation: one of (``*``, ``/``), ``*`` => effective_sum = sum * rate,
                                        ``/`` => effective_sum = sum / rate
:form description: description for payment, optional
:form currency: currency_id of ``sum``, default like as currency of purpose of the payment
:form sent_date: date of payment, format ``2015-03-24``, default == today

:reqheader Content-Type: one of ``application/x-www-form-urlencoded``,
                         ``application/json``, ``multipart/form-data``

:statuscode 201: create payment
:statuscode 400: bad request
:statuscode 404: purpose of payment don't exist
