import requests
from pytz import timezone
from datetime import datetime
import pymongo
import urllib.parse
import os

password_db = urllib.parse.quote_plus(os.environ['DB_PASS'])
user_db = urllib.parse.quote_plus(os.environ['DB_USER'])

client = pymongo.MongoClient(
    f"mongodb+srv://{user_db}:{password_db}@pykocluster0.iicmhy2.mongodb.net/?retryWrites=true&w=majority&appName=PykoCluster0")
db = client["pykoDB"]
collection = db["users"]

# keep store of all users using the bot and their watchlists
user_dict = {}

# keep store of all the users subscribed to calls/updates/news
users_calls = []
users_news = []
users_updates = {}

eastern = timezone('Europe/Sofia')


# fetch all of the users from the database
def fetch_users_from_db():
    data = collection.find()
    if data:
        for user in data:
            user_dict[user["user"]] = [user["coins"], user["chat"]]

            if user["updates"]:
                users_updates[user["user"]] = user["chat"]
            if user["calls"]:
                users_calls.append(user["user"])
            if user["news"]:
                users_news.append(user["chat"])


# fetch the current time(EEST)
def get_current_time():
    now = datetime.now(eastern)
    current_time = now.strftime("%H:%M:%S")
    return current_time


# strip article title from bad characters so it can be passed to MarkdownV2 in Telegram API
def strip_from_bad_chars(str):
    return str.translate(str.maketrans({" ": r"\-",
                                        "-": r"\-",
                                        "]": r"\]",
                                        "\\": r"\\",
                                        "^": r"\^",
                                        "$": r"\$",
                                        "*": r"\*",
                                        ".": r"\.",
                                        "_": r"\_",
                                        "[": r"\[",
                                        "(": r"\(",
                                        ")": r"\)",
                                        "~": r"\~",
                                        "`": r"\`",
                                        ">": r"\>",
                                        "+": r"\+",
                                        "=": r"\=",
                                        "|": r"\|",
                                        "{": r"\{",
                                        "}": r"\}",
                                        "!": r"\!",
                                        "#": r"\#"}))


# fetch price info for the currencies in the user's watchlist via the CryptoCompare API
def get_prices(user):
    crypto_data = requests.get(
        "https://min-api.cryptocompare.com/data/pricemultifull?fsyms={}&tsyms=USD&api_key={}".format(
            ",".join(user_dict[user][0]), os.environ.get("API_KEY"))).json()["RAW"]

    data = {}
    for i in crypto_data:
        data[i] = {
            "coin": i,
            "price": crypto_data[i]["USD"]["PRICE"],
            "change_day": crypto_data[i]["USD"]["CHANGEPCT24HOUR"],
            "change_hour": crypto_data[i]["USD"]["CHANGEPCTHOUR"]
        }

    return data


# fetch news from the CryptoCompare API
def get_hot_news():
    request = requests.get(
        "https://min-api.cryptocompare.com/data/v2/news/?lang=EN")
    response = request.json()
    return response


# add user to user_dict and the database and assign the default cryptocurrencies to them
def add_user(user, chat):
    fetch_users_from_db()
    if user not in user_dict.keys():
        document = {"user": user, "chat": chat, "coins": ["ADA", "BTC", "DOGE"], "updates": False, "calls": False, "news": False}
        collection.insert_one(document)
        fetch_users_from_db()


# call the user via the CallMeBot API
def call_user(username, coin, percentage, direction):
    requests.get(
        f"http://api.callmebot.com/start.php?user=@{username}&text={coin}+has+{direction}+in+price+by+{percentage:.3f}+percent+today&lang=en-US-Standard-E&rpt=2")


# add coin to the user's watchlist and update the database accordingly
def add_coin(coin_to_add, user):
    if coin_to_add not in user_dict[user][0]:
        user_dict[user][0].append(coin_to_add)
        collection.find_one_and_update({"user": user}, {"$addToSet": {"coins": coin_to_add}})
        return True
    else:
        return False


# remove coin from the user's watchlist and update the database accordingly
def remove_coin(coin_to_remove, user):
    if coin_to_remove in user_dict[user][0]:
        user_dict[user][0].remove(coin_to_remove)
        collection.find_one_and_update({"user": user}, {"$pullAll": {"coins": [coin_to_remove]}})
        return True
    else:
        return False


# add user to local news list + update the user's preferences in the db
def add_to_news_list(user, chat):
    users_news.append(chat)
    collection.find_one_and_update({"user": user}, {"$set": {"news": True}})


# add user to local updates list + update the user's preferences in the db
def add_to_updates_list(user, chat):
    users_updates[user] = chat
    collection.find_one_and_update({"user": user}, {"$set": {"updates": True}})


# add user to local call list + update the user's preferences in the db
def add_to_calls_list(user):
    users_calls.append(user)
    collection.find_one_and_update({"user": user}, {"$set": {"calls": True}})
