import os
import telegram
import time
from telegram.ext import Updater, CommandHandler
from utils import (get_prices, add_coin, remove_coin, users_calls,
                  add_to_updates_list, add_to_calls_list, add_to_news_list,
                  users_updates, users_news, fetch_users_from_db, call_user,
                  get_current_time, get_hot_news, strip_from_bad_chars, add_user)


fetch_users_from_db()
telegram_bot_token = os.environ['BOT_API']
updater = Updater(token=telegram_bot_token, use_context=True)
job_queue = updater.job_queue
dispatcher = updater.dispatcher

# Keep store of the last time a call was made to the user for each of the currencies
call_list = {}

# Add user to list of users and introduce bot
def start(update, context):
    add_user(update.message.from_user.username, update.effective_chat.id)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=("Welcome to PykoBot!! I will update you on the latest prices for selected "
                                   "cryptocurrencies and alert you when significant price changes occur! I will "
                                   "also send you some hot news at certain times in the day!\n\n▶️ Type /add "
                                   "<i>currency name</i> to add currencies to watchlist\n▶️ Type /remove "
                                   "<i>currency name</i> to remove currencies to watchlist\n▶️ Type /updates to "
                                   "receive updates for the currencies in your watchlist\n▶️ Type /news to receive "
                                   "news updates 4 times in the day\n▶️ Type /call to receive a call if one of the "
                                   "currencies in your watchlist experiences a price change of ±10% in 24h\n\nInitial "
                                   "currencies in watchlist are: BTC, ADA, DOGE"),
                             parse_mode='html')


# Subscribe the user to message updates on the crypto in their watchlist. Updates are sent every 7200 seconds(2 h)
def update(update, context):
    user = update.message.from_user.username
    chat = update.effective_chat.id
    if user not in users_updates.keys():
        add_to_updates_list(user, chat)
        context.bot.send_message(chat_id=chat,
                                 text='✅ You will now be updated on the latest prices of your selected crypto')

        # Add a job to the job_queue which will repeat itself every 7200 seconds
        context.job_queue.run_repeating(update_crypto_data_periodically,
                                        interval=7200,
                                        first=1,
                                        context=[chat, user])
    else:
        context.bot.send_message(chat_id=chat,
                                 text='❌ You are already subscribed to the updates list')


# Subscribe the user to call updates on the crypto in their watchlist. Check for drastic fluctuations in price every 81 seconds(requirement for the API through which the calls are made)
def call(update, context):
    user = update.message.from_user.username
    chat = update.effective_chat.id
    if user not in users_calls:
        add_to_calls_list(user)
        context.bot.send_message(chat_id=chat,
                                 text='✅ You will now get calls if there is a drastic change in price in one of your selected crypto')

        # Add a job to the job queue which will repeat itself every 81 seconds
        context.job_queue.run_repeating(check_for_drastic_changes,
                                        interval=81,
                                        first=1,
                                        context=user)
    else:
        context.bot.send_message(chat_id=chat,
                                 text='❌ You are already subscribed to the calls list')


# Subscribe the user to news updates 4 times in the day(every 6 hours). News are fetched through the CryptoCompare
def news(update, context):
    user = update.message.from_user.username
    chat = update.effective_chat.id
    if chat not in users_news:
        add_to_news_list(user, chat)
        context.bot.send_message(chat_id=chat,
                                 text='✅ You will now get news updates 4 times a day')

        # Add a job to the job queue which will repeat itself every 21600 seconds
        context.job_queue.run_repeating(check_for_hot_news,
                                        interval=21600,
                                        first=1,
                                        context=chat)
    else:
        context.bot.send_message(chat_id=chat,
                                 text='❌ You are already subscribed to the news list')


# Add a currency to the user's watchlist
def add_coin_to_list(update, context):
    user = update.message.from_user.username
    chat = update.effective_chat.id

    if len(context.args) > 0:
        for coin in context.args:
            attempt_to_add = add_coin(coin, user)
            if attempt_to_add:
                context.bot.send_message(chat_id=chat,
                                         text=f"✅ Successfully added {coin} to list of currencies")
            else:
                context.bot.send_message(chat_id=chat,
                                         text=f"❌ Failed to add {coin} to list of currencies. Check coin name")
    else:
        context.bot.send_message(chat_id=chat,
                                 text="🤔 What currency do you want to add to watchlist?")


# Remove a currency from the user's watchlist
def remove_coin_from_list(update, context):
    user = update.message.from_user.username
    chat = update.effective_chat.id
    if len(context.args) > 0:
        for coin in context.args:
            attempt_to_remove = remove_coin(coin, user)
            if attempt_to_remove:
                context.bot.send_message(chat_id=chat,
                                         text=f"✅ Successfully removed {coin} from list of currencies")
            else:
                context.bot.send_message(chat_id=chat,
                                         text=f"❌ Failed to remove {coin} to list of currencies. Check coin name")
    else:
        context.bot.send_message(chat_id=chat,
                                 text="🤔 What currency do you want to remove from watchlist?")


# Fetch info about the cryptocurrencies in the user's watchlist
def fetch_crypto_data(call_possible: False, username):
    timestamp = get_current_time()
    message = f"⌚ Timestamp: {timestamp}\n\n"

    crypto_data = get_prices(username)
    for i in crypto_data:
        coin = crypto_data[i]["coin"]
        price = crypto_data[i]["price"]
        change_day = crypto_data[i]["change_day"]
        change_hour = crypto_data[i]["change_hour"]
        day_emoji = '📈' if change_day > 0 else '📉'
        hour_emoji = '📈' if change_hour > 0 else '📉'
        message += f"🪙 Coin: {coin}\n🚀 Price: ${price:,.2f}\n{hour_emoji} Hour Change: {change_hour:.3f}%\n{day_emoji} Day Change: {change_day:.3f}%\n\n"

        # Call the user if the price of a currency has changed by ±10% over a 24h period
        if call_possible:
            current_time = int(time.time())
            if change_day > 9:
                if coin not in call_list.keys():
                    call_list[coin] = current_time
                    call_user(username, coin, change_day, 'increased')
                    return
                elif current_time - call_list[coin] > 86400:
                    call_user(username, coin, change_day, 'increased')
                    call_list[coin] = current_time
                    return
            elif change_day < -9:
                if coin not in call_list.keys():
                    call_user(username, coin, change_day, 'decreased')
                    call_list[coin] = current_time
                    return
                elif current_time - call_list[coin] > 86400:
                    call_user(username, coin, change_day, 'decreased')
                    call_list[coin] = current_time
                    return
    return message


def update_crypto_data_periodically(context: telegram.ext.CallbackContext):
    context_list = context.job.context
    message = fetch_crypto_data(False, context_list[1])
    context.bot.send_message(chat_id=context_list[0], text=message)


def check_for_drastic_changes(context: telegram.ext.CallbackContext):
    fetch_crypto_data(True, context.job.context)


def check_for_hot_news(context: telegram.ext.CallbackContext):
    json_response = get_hot_news()
    news = json_response['Data']
    message = f'🗞️ Your news at: {get_current_time()}\n\n'
    for i in range(5):
        article = news[i]
        url = article['url']
        title = strip_from_bad_chars(article['title'])
        headline = f'➡️ [{title}]({url})'
        message += f'{headline}\n\n'
    context.bot.send_message(chat_id=context.job.context,
                             text=message,
                             parse_mode='MarkdownV2',
                             disable_web_page_preview=True)


# Fetch the preferences for all of the users and start jobs for each preference
def load_preferences(context: telegram.ext.CallbackContext):
    for chat in users_news:
        context.job_queue.run_repeating(check_for_hot_news,
                                        interval=21600,
                                        first=1,
                                        context=chat)
    for username in users_calls:
        context.job_queue.run_repeating(check_for_drastic_changes,
                                        interval=81,
                                        first=1,
                                        context=username)
    for username, chat in users_updates.items():
        context.job_queue.run_repeating(update_crypto_data_periodically,
                                        interval=7200,
                                        first=1,
                                        context=[chat, username])


# Assign a command handler for each command
start_handler = CommandHandler("start", start)
update_handler = CommandHandler("update", update)
news_handler = CommandHandler("news", news)
call_handler = CommandHandler("call", call)
add_handler = CommandHandler("add", add_coin_to_list, pass_args=True)
remove_handler = CommandHandler("remove", remove_coin_from_list, pass_args=True)


# Add all the handlers to the dispatcher
dispatcher.add_handler(start_handler)
dispatcher.add_handler(update_handler)
dispatcher.add_handler(add_handler)
dispatcher.add_handler(remove_handler)
dispatcher.add_handler(call_handler)
dispatcher.add_handler(news_handler)


job_queue.run_once(load_preferences, when=0)
updater.start_polling()
updater.idle()
