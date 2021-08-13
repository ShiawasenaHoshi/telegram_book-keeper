# Book-keeping bot
Convenient book-keeping telegram bot.
- support multicurrency
- multiuser (same budget)
- xlsx-report available
- automatically currency rate update (Tinkoff bank's rates)

# Installation
1) ```git clone https://github.com/ShiawasenaHoshi/book-keeper.git; cd book-keeper```
2) Copy ```.env.example``` to ```.env``` and define TG_TOKEN, TG_ADMIN_ID
3) ```sudo docker-compose build; sudo docker-compose up```

# After update
Type ```/reset``` to refresh menu buttons and prevent errors

# Webhooks
If you want to use webhooks you have to:
1) uncomment and define corresponding variables at .env
2) uncomment webhook's lines at Dockerfile
3) open port 8443 at docker-compose.yml
4) generate certificate ```openssl genrsa -out webhook_pkey.pem 2048; openssl req -new -x509 -days 3650 -key webhook_pkey.pem -out webhook_cert.pem```
5) rebuild container ```sudo docker-compose build```