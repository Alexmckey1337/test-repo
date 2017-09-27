FROM node:latest

WORKDIR /app

RUN npm install -g gulp bower webpack

COPY ./.bowerrc /app
COPY ./bower.json /app
COPY ./gulpfile.js /app
COPY ./.babelrc /app
COPY ./webpack.config.js /app
COPY ./package.json /app/package.json

RUN npm install
RUN bower install --config.interactive=false --allow-root

COPY ./src /app/src

CMD ["npm", "run", "build"]
