FROM python:3.6

ENV PYTHONUNBUFFERED 1

# Requirements have to be pulled and installed here, otherwise caching won't work
COPY ./ticket_scanner/requirements.txt /requirements.txt

RUN pip install -r /requirements.txt \
    && groupadd -r flask \
    && useradd -r -g flask flask

COPY ./ticket_scanner/app /app
RUN chown -R flask /app

COPY ./compose/scanner/gunicorn.sh /gunicorn.sh
COPY ./compose/scanner/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r//' /entrypoint.sh \
    && sed -i 's/\r//' /gunicorn.sh \
    && chmod +x /entrypoint.sh \
    && chown flask /entrypoint.sh \
    && chmod +x /gunicorn.sh \
    && chown flask /gunicorn.sh

WORKDIR /app

ENTRYPOINT ["/entrypoint.sh"]
