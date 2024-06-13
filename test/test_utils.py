import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from pytz import timezone

from src.utils import (
    fetch_users_from_db, get_current_time, strip_from_bad_chars, get_prices,
    get_hot_news, add_user, call_user, add_coin, remove_coin,
    add_to_news_list, add_to_updates_list, add_to_calls_list, user_dict,
    users_calls, users_news, users_updates
)

class TestBotUtils(unittest.TestCase):

    @patch('src.utils.collection.find')
    def test_fetch_users_from_db(self, mock_find):
        mock_find.return_value = [
            {"user": "user1", "coins": ["BTC"], "chat": 123, "updates": True, "calls": True, "news": True},
            {"user": "user2", "coins": ["ETH"], "chat": 456, "updates": False, "calls": False, "news": False},
        ]
        fetch_users_from_db()
        self.assertIn("user1", user_dict)
        self.assertIn("user2", user_dict)
        self.assertIn("user1", users_updates)
        self.assertIn("user1", users_calls)
        self.assertIn(123, users_news)

    def test_get_current_time(self):
        eastern = timezone('Europe/Sofia')
        now = datetime.now(eastern)
        current_time = now.strftime("%H:%M:%S")
        self.assertEqual(get_current_time(), current_time)

    def test_strip_from_bad_chars(self):
        test_str = "Hello [World]!"
        stripped_str = strip_from_bad_chars(test_str)
        self.assertEqual(stripped_str, "Hello\\-\\[World\\]\\!")

    @patch('src.utils.requests.get')
    def test_get_prices(self, mock_get):
        mock_get.return_value.json.return_value = {
            "RAW": {
                "BTC": {"USD": {"PRICE": 50000, "CHANGEPCT24HOUR": 5, "CHANGEPCTHOUR": 0.5}},
                "ETH": {"USD": {"PRICE": 4000, "CHANGEPCT24HOUR": 4, "CHANGEPCTHOUR": 0.4}},
            }
        }
        user_dict["testuser"] = [["BTC", "ETH"], 123]
        prices = get_prices("testuser")
        self.assertEqual(prices["BTC"]["price"], 50000)
        self.assertEqual(prices["ETH"]["price"], 4000)

    @patch('src.utils.requests.get')
    def test_get_hot_news(self, mock_get):
        mock_get.return_value.json.return_value = {"Data": [{"title": "News1", "url": "http://example.com/news1"}]}
        news = get_hot_news()
        self.assertIn("Data", news)

    @patch('src.utils.collection.insert_one')
    @patch('src.utils.fetch_users_from_db')
    def test_add_user(self, mock_fetch_users_from_db, mock_insert_one):
        add_user("new_user", 789)
        mock_insert_one.assert_called_once()
        mock_fetch_users_from_db.assert_called_once()

    @patch('src.utils.requests.get')
    def test_call_user(self, mock_get):
        mock_get.return_value = MagicMock(status_code=200)
        response = call_user("testuser", "BTC", 10, "increased")
        self.assertEqual(response.status_code, 200)

    @patch('src.utils.collection.find_one_and_update')
    def test_add_coin(self, mock_find_one_and_update):
        user_dict["testuser"] = [["BTC"], 123]
        result = add_coin("ETH", "testuser")
        self.assertTrue(result)
        mock_find_one_and_update.assert_called_once()

    @patch('src.utils.collection.find_one_and_update')
    def test_remove_coin(self, mock_find_one_and_update):
        user_dict["testuser"] = [["BTC"], 123]
        result = remove_coin("BTC", "testuser")
        self.assertTrue(result)
        mock_find_one_and_update.assert_called_once()

    @patch('src.utils.collection.find_one_and_update')
    def test_add_to_news_list(self, mock_find_one_and_update):
        add_to_news_list("testuser", 123)
        self.assertIn(123, users_news)
        mock_find_one_and_update.assert_called_once()

    @patch('src.utils.collection.find_one_and_update')
    def test_add_to_updates_list(self, mock_find_one_and_update):
        add_to_updates_list("testuser", 123)
        self.assertIn("testuser", users_updates)
        mock_find_one_and_update.assert_called_once()

    @patch('src.utils.collection.find_one_and_update')
    def test_add_to_calls_list(self, mock_find_one_and_update):
        add_to_calls_list("testuser")
        self.assertIn("testuser", users_calls)
        mock_find_one_and_update.assert_called_once()

if __name__ == '__main__':
    unittest.main()
