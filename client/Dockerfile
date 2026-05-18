FROM node:20.18.1-alpine AS build

WORKDIR /app

ENV NODE_ENV=development
ENV NPM_CONFIG_PRODUCTION=false

COPY package.json ./

RUN npm config set registry https://registry.npmjs.org/
RUN npm install --legacy-peer-deps --include=dev --no-audit --no-fund --fetch-retries=5 --fetch-timeout=120000

COPY . .

ARG VITE_API_URL=http://localhost
ENV VITE_API_URL=$VITE_API_URL

RUN ./node_modules/.bin/tsc -b && ./node_modules/.bin/vite build

FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]