FROM cgr.dev/chainguard/node:latest

WORKDIR /app

COPY package.json .

RUN npm install

COPY Logos.jpg .
COPY Experiment.html .
COPY experiment.js .
COPY emails.txt .
COPY keys.txt .

USER root
RUN chmod 666 keys.txt
RUN chmod 666 emails.txt

ENTRYPOINT [ "node", "experiment.js" ]
