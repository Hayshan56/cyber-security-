import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from storage import Storage

class TestStorage(unittest.TestCase):

    def setUp(self):
        """
        Set up a clean environment for each test.
        """
        self.master_password = "test_password"
        self.test_filepath = "test_passwords.json.encrypted"
        self.storage = Storage(self.master_password, filepath=self.test_filepath)

    def tearDown(self):
        """
        Clean up created files after each test.
        """
        if os.path.exists(self.test_filepath):
            os.remove(self.test_filepath)

    def test_save_and_load(self):
        """
        Test that data can be saved to and loaded from a file.
        """
        data_to_save = '{"service": {"username": "user", "password": "password"}}'
        self.storage.save(data_to_save)
        loaded_data = self.storage.load()
        self.assertEqual(data_to_save, loaded_data)

    def test_load_nonexistent_file(self):
        """
        Test that loading from a nonexistent file returns None.
        """
        # Ensure the file does not exist before loading
        if os.path.exists(self.test_filepath):
            os.remove(self.test_filepath)
        loaded_data = self.storage.load()
        self.assertIsNone(loaded_data)

    def test_decryption_with_wrong_password(self):
        """
        Test that decryption fails with an incorrect master password.
        """
        data_to_save = "some data"
        self.storage.save(data_to_save)

        wrong_storage = Storage("wrong_password", filepath=self.test_filepath)
        loaded_data = wrong_storage.load()
        self.assertIsNone(loaded_data)


if __name__ == '__main__':
    unittest.main()
