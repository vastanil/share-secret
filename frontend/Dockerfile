FROM node:18

WORKDIR /app
COPY . .

RUN npm install -g http-server

CMD ["http-server", "-p", "3000"]

