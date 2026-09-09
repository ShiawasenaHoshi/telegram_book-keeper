"""Fixed EUR-base conversion rates for offline DB seed (e2e, local dev without currencyapi).

Values match currencyapi cache format in ExchangeRates: rate to convert from iso to MAIN_CURRENCY.
"""

REFERENCE_RATES = {
    "eur": 1.0,
    "usd": 0.92,
    "rub": 0.010,
    "gbp": 1.16,
    "gel": 0.34,
}
