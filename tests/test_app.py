import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

class TestWebApp(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    def test_index_page_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Network Vulnerability Scanner', response.data)

    @patch('app.run_full_scan.delay')
    def test_scan_route_starts_task(self, mock_delay):
        """Test that the /scan route correctly starts a Celery task."""
        # Arrange
        mock_task = MagicMock()
        mock_task.id = 'test-task-id'
        mock_delay.return_value = mock_task

        # Act
        response = self.client.post('/scan', data={'target': '127.0.0.1', 'api_key': 'test-key'})

        # Assert
        self.assertEqual(response.status_code, 302) # Should redirect
        mock_delay.assert_called_once_with('127.0.0.1', 'test-key')
        self.assertIn('/scan-in-progress/test-task-id/127.0.0.1', response.location)

    @patch('app.run_full_scan.AsyncResult')
    def test_scan_status_route(self, mock_async_result):
        """Test the /status route for a running task."""
        # Arrange
        mock_task = MagicMock()
        mock_task.state = 'PROGRESS'
        mock_async_result.return_value = mock_task

        # Act
        response = self.client.get('/status/test-task-id')

        # Assert
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data['state'], 'PROGRESS')

    @patch('app.run_full_scan.AsyncResult')
    def test_scan_results_route_success(self, mock_async_result):
        """Test the /results route when a task has succeeded."""
        # Arrange
        mock_task = MagicMock()
        mock_task.state = 'SUCCESS'
        # Mock the task result
        mock_task.get.return_value = {
            80: {'service': 'http', 'product': 'Apache', 'version': '2.4.41', 'vulnerabilities': []}
        }
        # Mock the request object to get the target
        mock_task.request.args = ('127.0.0.1',)
        mock_async_result.return_value = mock_task

        # Act
        response = self.client.get('/results/test-task-id')

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Scan Results for 127.0.0.1', response.data)
        self.assertIn(b'Apache', response.data)

if __name__ == '__main__':
    unittest.main()
