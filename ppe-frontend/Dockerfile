FROM node:20.11.0 AS build

WORKDIR /web-ui

COPY package.json package-lock.json ./
RUN npm i

COPY . ./

RUN npx quasar build

CMD ["npx", "quasar", "dev"]