FROM node:lts-slim as frontend_build

WORKDIR /bpapp

COPY ./frontend/package.json .

RUN yarn install && yarn cache clean

COPY ./frontend .

COPY ./secrets/.frontend.env .env

RUN yarn run build --verbose

FROM nginx:stable as frontend_prod

COPY ./config/docker/frontend/nginx.conf /etc/nginx/nginx.conf

WORKDIR /usr/share/nginx/html

RUN rm -rf ./*

COPY --from=frontend_build /bpapp/build/ ./

ENTRYPOINT [ "nginx", "-g", "daemon off;" ]
