import requests
from twilio.rest import Client

VIRTUAL_TWILIO_NUMBER = "YOUR_VIRTUAL_TWILIO_NUMBER"
VERIFIED_NUMBER = "YOUR_VERIFIED_NUMBER"

STOCK_NAME = "STOCK_TICKER_SYMBOL, i.e TSLA"
COMPANY_NAME = "Example: Tesla Inc"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

STOCK_API_KEY = "YOUR_STOCK_API_KEY"
NEWS_API_KEY = "YOUR_NEWS_API_KEY"

TWILIO_SID = 'YOUR_TWILIO_SID'
TWILIO_AUTH_TOKEN = "YOUR_TWILIO_AUTH_TOKEN"

stock_parameters = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK_NAME,
    "apikey": STOCK_API_KEY,
}

news_parameters = {
    "apiKey": NEWS_API_KEY,
    "q": COMPANY_NAME,
}

# Gets yesterday and the day before yesterday's closing stock price.
response = requests.get(url=STOCK_ENDPOINT, params=stock_parameters)
response.raise_for_status()
stock_data = response.json()["Time Series (Daily)"]

dates = [key for (key, value) in stock_data.items()]
yesterday_closing = float(stock_data[dates[0]]["4. close"])
day_before_closing = float(stock_data[dates[1]]["4. close"])

# Works out the difference, positive difference and percentage difference between the two prices.
difference = round(yesterday_closing - day_before_closing, 2)
positive_difference = round(abs(yesterday_closing - day_before_closing), 2)
percentage_difference = round((positive_difference / yesterday_closing) * 100, 3)

# Allocates the correct symbol to up_down based on how the stock price moved within a day.
up_down = None
if difference > 0:
    up_down = "🔺"
else:
    up_down = "🔻"

# If the percentage difference is greater than 5, the program will retrieve articles relating to the COMPANY_NAME
# using the news API
if percentage_difference > 5:
    news_response = requests.get(url=NEWS_ENDPOINT, params=news_parameters)
    news_response.raise_for_status()
    # Utilises Python's split operator to create a list containing the first three articles.
    news_data = news_response.json()["articles"][:3]

    # Uses list comprehension to create two new lists for the articles' headlines and descriptions.
    headlines = [headline["title"] for headline in news_data]
    descriptions = [description["description"] for description in news_data]

    # Sends a separate text message for each article using Twilio
    for x in range(0, len(headlines)):
        client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
        message = client.messages \
            .create(
            body=f"{STOCK_NAME} {up_down}{percentage_difference}% \n"
                 f"Headline: {headlines[x]} \n"
                 f"Brief: {descriptions[x]}",
            from_=f'{VIRTUAL_TWILIO_NUMBER}',
            to=f'{VERIFIED_NUMBER}'
        )
