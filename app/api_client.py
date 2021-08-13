import requests


def get_tinkoff_currency_rate(iso_default, iso_to):
    url = f"https://api.tinkoff.ru/v1/currency_rates?from={iso_to.upper()}&to={iso_default.upper()}"
    headers = {"Sec-Ch-Ua": "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"90\"", "Sec-Ch-Ua-Mobile": "?0",
                     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
                     "Content-Type": "application/x-www-form-urlencoded", "Accept": "*/*",
                     "Origin": "https://www.tinkoff.ru", "Sec-Fetch-Site": "same-site", "Sec-Fetch-Mode": "cors",
                     "Sec-Fetch-Dest": "empty", "Referer": "https://www.tinkoff.ru/",
                     "Accept-Encoding": "gzip, deflate", "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
                     "Connection": "close"}
    response = requests.get(url, headers=headers)
    import json
    parsed = json.loads(response.text)
    for rate in parsed["payload"]["rates"]:
        if rate["category"] == "SavingAccountTransfers":
            return rate["sell"]
    raise Exception("There is no category \"SavingAccountTransfers\" in tinkoff's response")
