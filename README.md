
# PykoBot

A Telegram bot created in Python for the purpose of being helpful to crypto-hobbyists

**DISLAIMER**: THIS BOT IS FOR EXPERIMENTAL USE ONLY.
## Functionality

After the `/start` command is given to the bot it will register the user and assign the default cryptocurrencies(_ADA_, _BTC_, _DOGE_) to their watchlist

Here is a list to all other commands and their functions:
- `/update`: receive price updates for the cryptocurrencies in your watchlist every 2 hours
- `/call`: receive a phone call if any of your cryptocurrencies fluctuates in price ±10% in a period of 24hours. **IMPORTANT: send `/start` to @CallMeBot_txtbot in Telegram to enable this functionality**
- `/news`: receive news updates 4 times in a day
- `/add crypto_abbreviation`: add cryptocurrency to your watchlist
- `/remove crypto_abbreviation`: remove cryptocurrency from your watchlist

## Technical stuff

This is an interesting project and I have implemented a few API's into it in order for all commands to work properly:
- The core functionality of the bot is built using [The Telegram Bot API](https://core.telegram.org/bots/api) and the [python-telegram-bot library](https://python-telegram-bot.readthedocs.io/en/stable/#)
- Automated calls to users are made using the [CallMeBot Telegram API](https://www.callmebot.com/telegram-call-api/)
- News are fetched using the [CryptoCompare API](https://min-api.cryptocompare.com/)
- Price info is fetched using the [CryptoCompare API](https://min-api.cryptocompare.com/)

## Set up

In order to run the project create a virtual environment using `python3 -m venv .venv`. After that activate it `source .venv/bin/activate` and install all of the required python packages `pip install -r requirements.txt`.

You will have to provide the required environment variables if you want to run this project locally. These are the following:
* `DB_PASS`: Password for the MongoDB database.
* `DB_USER`: Username for the MongoDB database.
* `API_KEY`: API key for the CryptoCompare API.
* `BOT_API`: API token for the Telegram bot.

## Technical documentation

# utils.py
This module provides various utility functions for interacting with the database and external APIs.

## Functions
### `fetch_users_from_db()`
Fetches all users from the database and populates the `user_dict`, `users_calls`, `users_news`, and `users_updates` dictionaries.

### `get_current_time()`
Returns the current time in the Europe/Sofia timezone.

### `strip_from_bad_chars(str)`
Strips unwanted characters from a string to make it suitable for MarkdownV2 formatting in Telegram messages.

### `get_prices(user)`
Fetches price information for the cryptocurrencies in the user's watchlist via the CryptoCompare API.

### `get_hot_news()`
Fetches the latest cryptocurrency news from the CryptoCompare API.

### `add_user(user, chat)`
Adds a new user to the database and initializes their watchlist with default cryptocurrencies.

### `call_user(username, coin, percentage, direction)`
Sends a call notification to the user via the CallMeBot API.

### `add_coin(coin_to_add, user)`
Adds a cryptocurrency to the user's watchlist and updates the database.

### `remove_coin(coin_to_remove, user)`
Removes a cryptocurrency from the user's watchlist and updates the database.

### `add_to_news_list(user, chat)`
Adds a user to the news subscription list and updates their preferences in the database.

### `add_to_updates_list(user, chat)`
Adds a user to the updates subscription list and updates their preferences in the database.

### `add_to_calls_list(user)`
Adds a user to the calls subscription list and updates their preferences in the database.

# bot.py
This module sets up the Telegram bot, defines command handlers, and manages periodic updates and alerts.

## Global Variables
- `call_list`: A dictionary to keep track of the last time a call was made for each cryptocurrency.
- `telegram_bot_token`: The API token for the Telegram bot, read from environment variables.
- `updater`: The Updater object from the `python-telegram-bot` library.
- `job_queue`: The job queue for scheduling periodic tasks.
- `dispatcher`: The dispatcher for handling commands and messages.

## Command Handlers
### `start(update, context)`
Adds a new user to the list of users and introduces the bot.

### `update(update, context)`
Subscribes the user to message updates on their watchlist cryptocurrencies.

### `call(update, context)`
Subscribes the user to call updates for drastic price changes in their watchlist cryptocurrencies.

### `news(update, context)`
Subscribes the user to news updates four times a day.

### `add_coin_to_list(update, context)`
Adds a cryptocurrency to the user's watchlist.

### `remove_coin_from_list(update, context)`
Removes a cryptocurrency from the user's watchlist.

## Helper Functions
### `fetch_crypto_data(call_possible, username)`
Fetches cryptocurrency data for the user's watchlist and sends updates via Telegram.

### `update_crypto_data_periodically(context)`
Periodic task to update cryptocurrency data and send updates to users.

### `check_for_drastic_changes(context)`
Periodic task to check for drastic price changes and notify users via calls.

### `check_for_hot_news(context)`
Periodic task to fetch and send the latest cryptocurrency news.

### `load_preferences(context)`
Fetches user preferences and starts jobs for each preference.

## Job Scheduling
- `load_preferences`: Runs once at startup to load user preferences and schedule jobs.
- `update_crypto_data_periodically`: Runs every 7200 seconds to update cryptocurrency data.
- `check_for_drastic_changes`: Runs every 81 seconds to check for drastic price changes.
- `check_for_hot_news`: Runs every 21600 seconds to fetch and send news updates.
