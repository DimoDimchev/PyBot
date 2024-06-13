import unittest
from unittest.mock import patch, MagicMock
from src.bot import start, call, news, add_coin_to_list, remove_coin_from_list

class TestTelegramBot(unittest.TestCase):
    @patch('src.bot.add_user')
    @patch('my_module.telegram.Bot.send_message')
    def test_start(self, mock_send_message, mock_add_user):
        update = MagicMock()
        context = MagicMock()
        start(update, context)
        mock_add_user.assert_called_once()
        mock_send_message.assert_called_once()

    @patch('src.bot.add_to_updates_list')
    @patch('src.bot.telegram.Bot.send_message')
    def test_update(self, mock_send_message, mock_add_to_updates_list):
        update = MagicMock()
        context = MagicMock()
        update.message.from_user.username = 'testuser'
        update.effective_chat.id = '1234'
        context.job_queue.run_repeating = MagicMock()
        update(update, context)
        mock_add_to_updates_list.assert_called_once_with('testuser', '1234')
        mock_send_message.assert_called_once()

    @patch('src.bot.add_to_calls_list')
    @patch('src.bot.telegram.Bot.send_message')
    def test_call(self, mock_send_message, mock_add_to_calls_list):
        update = MagicMock()
        context = MagicMock()
        update.message.from_user.username = 'testuser'
        update.effective_chat.id = '1234'
        context.job_queue.run_repeating = MagicMock()
        call(update, context)
        mock_add_to_calls_list.assert_called_once_with('testuser')
        mock_send_message.assert_called_once()

    @patch('src.bot.add_to_news_list')
    @patch('src.bot.telegram.Bot.send_message')
    def test_news(self, mock_send_message, mock_add_to_news_list):
        update = MagicMock()
        context = MagicMock()
        update.message.from_user.username = 'testuser'
        update.effective_chat.id = '1234'
        context.job_queue.run_repeating = MagicMock()
        news(update, context)
        mock_add_to_news_list.assert_called_once_with('testuser', '1234')
        mock_send_message.assert_called_once()

    @patch('src.bot.add_coin')
    @patch('src.bot.telegram.Bot.send_message')
    def test_add_coin_to_list(self, mock_send_message, mock_add_coin):
        update = MagicMock()
        context = MagicMock()
        update.message.from_user.username = 'testuser'
        update.effective_chat.id = '1234'
        context.args = ['BTC']
        mock_add_coin.return_value = True
        add_coin_to_list(update, context)
        mock_add_coin.assert_called_once_with('BTC', 'testuser')
        mock_send_message.assert_called_once()

    @patch('src.bot.remove_coin')
    @patch('src.bot.telegram.Bot.send_message')
    def test_remove_coin_from_list(self, mock_send_message, mock_remove_coin):
        update = MagicMock()
        context = MagicMock()
        update.message.from_user.username = 'testuser'
        update.effective_chat.id = '1234'
        context.args = ['BTC']
        mock_remove_coin.return_value = True
        remove_coin_from_list(update, context)
        mock_remove_coin.assert_called_once_with('BTC', 'testuser')
        mock_send_message.assert_called_once()

if __name__ == '__main__':
    unittest.main()
