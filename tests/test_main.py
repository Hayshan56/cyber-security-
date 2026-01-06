import unittest
from unittest.mock import patch, MagicMock
import string
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import generate_password, main

class TestPasswordGenerator(unittest.TestCase):

    def test_generate_password_length(self):
        """
        Test that the generated password has the correct length.
        """
        for length in [8, 16, 32]:
            password = generate_password(length)
            self.assertEqual(len(password), length)

    def test_generate_password_complexity(self):
        """
        Test that the generated password meets complexity requirements.
        """
        password = generate_password(16)
        self.assertTrue(any(c.islower() for c in password))
        self.assertTrue(any(c.isupper() for c in password))
        self.assertTrue(sum(c.isdigit() for c in password) >= 3)
        self.assertTrue(any(c in string.punctuation for c in password))

class TestMainCommands(unittest.TestCase):

    @patch('sys.argv', ['main.py', 'list'])
    @patch('main.getpass.getpass')
    @patch('main.Storage')
    @patch('builtins.print')
    def test_list_command(self, mock_print, mock_storage_class, mock_getpass):
        mock_getpass.return_value = 'master_password'
        mock_storage_instance = MagicMock()
        mock_storage_class.return_value = mock_storage_instance

        test_data = {'google': {'username': 'test'}, 'github': {'username': 'test2'}}
        mock_storage_instance.load.return_value = json.dumps(test_data)

        main()

        mock_storage_class.assert_called_with('master_password')
        mock_storage_instance.load.assert_called_once()
        mock_print.assert_any_call("Stored services:")
        mock_print.assert_any_call("- google")
        mock_print.assert_any_call("- github")

    @patch('sys.argv', ['main.py', 'add', 'google', 'test_user'])
    @patch('main.getpass.getpass')
    @patch('main.Storage')
    @patch('builtins.print')
    def test_add_command(self, mock_print, mock_storage_class, mock_getpass):
        # Simulate entering master password, then password to store
        mock_getpass.side_effect = ['master_password', 'new_password']
        mock_storage_instance = MagicMock()
        mock_storage_class.return_value = mock_storage_instance
        mock_storage_instance.load.return_value = json.dumps({})  # Start with empty store

        main()

        mock_storage_class.assert_called_with('master_password')
        mock_storage_instance.load.assert_called_once()
        expected_data = {'google': {'username': 'test_user', 'password': 'new_password'}}
        mock_storage_instance.save.assert_called_once_with(json.dumps(expected_data))
        mock_print.assert_called_with("Password for google added.")

    @patch('sys.argv', ['main.py', 'get', 'google'])
    @patch('main.getpass.getpass')
    @patch('main.Storage')
    @patch('builtins.print')
    def test_get_command_success(self, mock_print, mock_storage_class, mock_getpass):
        mock_getpass.return_value = 'master_password'
        mock_storage_instance = MagicMock()
        mock_storage_class.return_value = mock_storage_instance

        test_data = {'google': {'username': 'test_user', 'password': 'test_password'}}
        mock_storage_instance.load.return_value = json.dumps(test_data)

        main()

        mock_storage_class.assert_called_with('master_password')
        mock_storage_instance.load.assert_called_once()
        mock_print.assert_any_call("Service: google")
        mock_print.assert_any_call("Username: test_user")
        mock_print.assert_any_call("Password: test_password")

    @patch('sys.argv', ['main.py', 'get', 'google', '-c'])
    @patch('main.pyperclip.copy')
    @patch('main.getpass.getpass')
    @patch('main.Storage')
    @patch('builtins.print')
    def test_get_command_copy(self, mock_print, mock_storage_class, mock_getpass, mock_pyperclip_copy):
        mock_getpass.return_value = 'master_password'
        mock_storage_instance = MagicMock()
        mock_storage_class.return_value = mock_storage_instance

        test_data = {'google': {'username': 'test_user', 'password': 'test_password'}}
        mock_storage_instance.load.return_value = json.dumps(test_data)

        main()

        mock_storage_class.assert_called_with('master_password')
        mock_storage_instance.load.assert_called_once()
        mock_pyperclip_copy.assert_called_once_with('test_password')
        mock_print.assert_called_with("Password for google copied to clipboard.")

    @patch('sys.argv', ['main.py', 'delete', 'google'])
    @patch('main.getpass.getpass')
    @patch('main.Storage')
    @patch('builtins.print')
    def test_delete_command_success(self, mock_print, mock_storage_class, mock_getpass):
        mock_getpass.return_value = 'master_password'
        mock_storage_instance = MagicMock()
        mock_storage_class.return_value = mock_storage_instance

        test_data = {'google': {'username': 'test'}, 'github': {'username': 'test2'}}
        mock_storage_instance.load.return_value = json.dumps(test_data)

        main()

        mock_storage_instance.load.assert_called_once()
        expected_saved_data = json.dumps({'github': {'username': 'test2'}})
        mock_storage_instance.save.assert_called_once_with(expected_saved_data)
        mock_print.assert_called_with("Entry for google deleted.")

    @patch('sys.argv', ['main.py', 'update', 'google', '-u', 'new_user'])
    @patch('main.getpass.getpass')
    @patch('main.Storage')
    @patch('builtins.print')
    def test_update_username(self, mock_print, mock_storage_class, mock_getpass):
        mock_getpass.return_value = 'master_password'
        mock_storage_instance = MagicMock()
        mock_storage_class.return_value = mock_storage_instance

        test_data = {'google': {'username': 'old_user', 'password': 'old_password'}}
        mock_storage_instance.load.return_value = json.dumps(test_data)

        main()

        mock_storage_instance.load.assert_called_once()
        expected_data = {'google': {'username': 'new_user', 'password': 'old_password'}}
        mock_storage_instance.save.assert_called_once_with(json.dumps(expected_data))
        mock_print.assert_called_with("Entry for google updated.")

    @patch('sys.argv', ['main.py', 'update', 'google', '-p'])
    @patch('main.getpass.getpass')
    @patch('main.Storage')
    @patch('builtins.print')
    def test_update_password(self, mock_print, mock_storage_class, mock_getpass):
        mock_getpass.side_effect = ['master_password', 'new_password']
        mock_storage_instance = MagicMock()
        mock_storage_class.return_value = mock_storage_instance

        test_data = {'google': {'username': 'old_user', 'password': 'old_password'}}
        mock_storage_instance.load.return_value = json.dumps(test_data)

        main()

        mock_storage_instance.load.assert_called_once()
        expected_data = {'google': {'username': 'old_user', 'password': 'new_password'}}
        mock_storage_instance.save.assert_called_once_with(json.dumps(expected_data))
        mock_print.assert_called_with("Entry for google updated.")

    @patch('sys.argv', ['main.py', 'update', 'google', '-u', 'new_user', '-p'])
    @patch('main.getpass.getpass')
    @patch('main.Storage')
    @patch('builtins.print')
    def test_update_both(self, mock_print, mock_storage_class, mock_getpass):
        mock_getpass.side_effect = ['master_password', 'new_password']
        mock_storage_instance = MagicMock()
        mock_storage_class.return_value = mock_storage_instance

        test_data = {'google': {'username': 'old_user', 'password': 'old_password'}}
        mock_storage_instance.load.return_value = json.dumps(test_data)

        main()

        mock_storage_instance.load.assert_called_once()
        expected_data = {'google': {'username': 'new_user', 'password': 'new_password'}}
        mock_storage_instance.save.assert_called_once_with(json.dumps(expected_data))
        mock_print.assert_called_with("Entry for google updated.")

    @patch('sys.argv', ['main.py', 'update', 'google'])
    @patch('builtins.print')
    def test_update_no_flags(self, mock_print):
        main()
        mock_print.assert_called_with("Error: Please specify a new username with -u or prompt for a new password with -p.")


if __name__ == '__main__':
    unittest.main()
