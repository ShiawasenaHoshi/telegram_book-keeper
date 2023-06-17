FROM python:3.10-slim-buster

COPY requirements.txt /tmp/
COPY install-packages.sh /tmp/
RUN /tmp/install-packages.sh

RUN useradd --create-home bot
WORKDIR /home/bot
USER bot

COPY app /home/bot/app/
COPY config.py .
COPY bot.py .
COPY start.py .

# If you are going to use webhooks, generate cert's files, uncomment two lines below and rebuild container
#COPY webhook_cert.pem .
#COPY webhook_pkey.pem .
COPY migrations /home/bot/migrations

CMD [ "python", "start.py" ]