FROM node:argon

WORKDIR /app

RUN npm install -g gulp bower

COPY ./.bowerrc /app
COPY ./bower.json /app
COPY ./gulpfile.js /app
COPY ./package.json /app/package.json

RUN npm install
RUN bower install --config.interactive=false --allow-root

COPY ./src /app/src

CMD ["gulp", "scripts", "less", "font"]
