import aiohttp
import asyncio
import argparse
from datetime import date, datetime, timedelta
import json
import os

API_URL = "https://api.privatbank.ua/p24api/exchange_rates"


async def fetch_exchange_rates(session, date_str):
    # Функція для виконання HTTP-запиту до API та отримання курсів валют на обрану дату
    params = {
        'json': 'true',
        'date': date_str,
    }

    async with session.get(API_URL, params=params) as response:
        data = await response.json()
        return data


async def get_currency_rates_for_days(days):
    # Функція для отримання курсів валют для кількох днів
    async with aiohttp.ClientSession() as session:
        tasks = []

        for i in range(days):
            current_date = date.today() - timedelta(days=i)
            date_str = current_date.strftime("%d.%m.%Y")

            task = fetch_exchange_rates(session, date_str)
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        return results


def save_to_json(data, days):
    # Функція для збереження результатів у файл JSON
    current_date = date.today().strftime("%Y-%m-%d")
    filename = f"exchange_rates_{current_date}_{days}days.json"
    filepath = os.path.join("results", filename)

    os.makedirs("results", exist_ok=True)

    with open(filepath, 'w') as json_file:
        json.dump(data, json_file, indent=2)

    print(f"Results saved to {filepath}")


def parse_args():
    # Функція для обробки введених аргументів з командного рядка
    parser = argparse.ArgumentParser(description='Get currency exchange rates from PrivatBank API.')

    # Додаємо параметр для вказання кількості днів або конкретної дати та параметр для валют
    parser.add_argument('days', metavar='days', nargs='?', default=None, type=int, help='Number of days or specific date in the format "YYYY-MM-DD"')
    parser.add_argument('--currency', metavar='currency', nargs='+', type=str, help='List of currencies to retrieve exchange rates for')

    return parser.parse_args()


def main():
    print("Enter the number of days or a specific date for which to display the exchange rate:")
    days_input = input()
    print("Enter a list of currencies (space-separated) to retrieve exchange rates for:")
    currency_input = input().split()

    args = parse_args()

    if args.days is None:
        args.days = days_input
    if args.currency is None:
        args.currency = currency_input

    if isinstance(args.days, str):
        try:
            args.days = int(args.days)
        except ValueError:
            print("Error: Please enter a valid number of days.")
            return

    if args.days > 10:
        print("Error: Number of days should not exceed 10.")
        return

    loop = asyncio.get_event_loop()
    exchange_rates = loop.run_until_complete(get_currency_rates_for_days(args.days))

    formatted_results = []

    for i, rates in enumerate(exchange_rates):
        current_date = date.today() - timedelta(days=i)
        date_str = current_date.strftime("%d.%m.%Y")

        formatted_result = {
            date_str: {}
        }

        for currency in args.currency:
            formatted_result[date_str][currency] = {
                'sale': None,
                'purchase': None
            }

        for rate in rates['exchangeRate']:
            if rate['currency'] in args.currency:
                formatted_result[date_str][rate['currency']]['sale'] = rate['saleRateNB']
                formatted_result[date_str][rate['currency']]['purchase'] = rate['purchaseRateNB']

        formatted_results.append(formatted_result)

    save_to_json(formatted_results, args.days)
    print(formatted_results)


if __name__ == "__main__":
    main()