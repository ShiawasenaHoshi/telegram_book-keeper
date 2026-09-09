FROM python:3.12-alpine3.20

COPY requirements.txt /tmp/
COPY install-packages.sh /tmp/
RUN /tmp/install-packages.sh

RUN adduser -D bot
WORKDIR /home/bot
USER bot

COPY app /home/bot/app/
COPY config.py .
COPY bot.py .
COPY start.py .
COPY migrations /home/bot/migrations

CMD [ "python", "start.py" ]
