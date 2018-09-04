################################################################################
# Build stage 0 `frontend`:
################################################################################
FROM node:latest AS frontend

WORKDIR /app

RUN npm install -g gulp bower webpack

COPY ./.bowerrc /app
COPY ./bower.json /app
RUN bower install --config.interactive=false --allow-root

COPY ./gulpfile.js /app
COPY ./.babelrc /app
COPY ./webpack.config.js /app
COPY ./package.json /app/package.json
COPY ./package-lock.json /app/package-lock.json

RUN npm install

COPY ./src /app/src

RUN npm run build

################################################################################
# Build stage 1
# Copy frontend files
# Build django project
################################################################################
# FROM pypy:3
FROM python:3.6

ENV PYTHONUNBUFFERED 1
ENV DATABASE_URL postgres:///crm_db
ENV DJANGO_SECRET_KEY n1#kwh!wi0+130zd050+$drvmx6q7qxg70)1i4e9ey(zpx0qki

# for pypy3
# RUN apt-get update && apt-get install software-properties-common build-essential gettext ttf-freefont mediainfo ffmpeg libcairo2-dev libjpeg62-turbo-dev libpango1.0-dev libgif-dev build-essential g++ libxml2-dev libxslt1-dev -y

# for python
RUN echo "deb http://ftp.debian.org/debian jessie-backports main" >> /etc/apt/sources.list
RUN apt-get update && apt-get install build-essential gettext ttf-freefont mediainfo ffmpeg -y
# Requirements have to be pulled and installed here, otherwise caching won't work
COPY ./requirements /requirements
COPY ./docs/requirements.txt /docs-requirements.txt

RUN pip install --no-cache-dir -r /docs-requirements.txt \
    && pip install --no-cache-dir -r /requirements/production.txt \
    && groupadd -r django \
    && useradd -r -g django django

COPY . /app
RUN rm -rf /app/{src,bower.json,gulpfile.js,webpack.config.js,package.json}
RUN chown -R django /app

COPY ./CHANGELOG.rst /app/docs/source/
RUN cd /app/docs && sphinx-build -b html -d build/doctrees source build/docs

COPY ./docker/gunicorn.sh /gunicorn.sh
COPY ./docker/gunicorn/conf.py /app/gunicorn/conf.py
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

COPY --from=frontend  /app/public/static /app/public/static
RUN chown -R django /app/public/static

WORKDIR /app

ENTRYPOINT ["/entrypoint.sh"]
