FROM python:3.6

ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install gettext ttf-freefont -y
# Requirements have to be pulled and installed here, otherwise caching won't work
COPY ./requirements /requirements

RUN pip install -r /requirements/production.txt \
    && groupadd -r django \
    && useradd -r -g django django

COPY . /app
RUN chown -R django /app

COPY ./docker/gunicorn.sh /gunicorn.sh
COPY ./docker/daphne.sh /daphne.sh
COPY ./docker/asgi_worker.sh /asgi_worker.sh
COPY ./docker/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r//' /entrypoint.sh \
    && sed -i 's/\r//' /gunicorn.sh \
    && sed -i 's/\r//' /daphne.sh \
    && sed -i 's/\r//' /asgi_worker.sh \
    && chmod +x /entrypoint.sh \
    && chown django /entrypoint.sh \
    && chmod +x /gunicorn.sh \
    && chown django /gunicorn.sh \
    && chmod +x /daphne.sh \
    && chown django /daphne.sh \
    && chmod +x /asgi_worker.sh \
    && chown django /asgi_worker.sh

WORKDIR /app

ENTRYPOINT ["/entrypoint.sh"]
