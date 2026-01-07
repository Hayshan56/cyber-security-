import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import requests
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from vuln_checker import check_vulnerabilities

class TestVulnChecker(unittest.TestCase):

    @patch('vuln_checker.time.sleep') # Mock sleep to make tests run instantly
    @patch('vuln_checker.requests.get')
    def test_check_vulnerabilities_success_no_key(self, mock_requests_get, mock_sleep):
        """
        Test a successful API call without an API key.
        """
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "vulnerabilities": [{"cve": {"id": "CVE-2021-12345", "descriptions": [{"lang": "en", "value": "Test"}], "metrics": {"cvssMetricV31": [{"cvssData": {"baseScore": 7.5, "baseSeverity": "HIGH"}}]}}}]
        }
        mock_requests_get.return_value = mock_response

        service_info = {'product': 'Apache', 'version': '2.4.41'}

        # Act
        vulnerabilities = check_vulnerabilities(service_info, api_key=None)

        # Assert
        mock_sleep.assert_called_once_with(6.0) # Slower delay without key
        self.assertEqual(len(vulnerabilities), 1)
        self.assertEqual(vulnerabilities[0]['cve_id'], 'CVE-2021-12345')

    @patch('vuln_checker.time.sleep')
    @patch('vuln_checker.requests.get')
    def test_check_vulnerabilities_success_with_key(self, mock_requests_get, mock_sleep):
        """
        Test a successful API call with an API key.
        """
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"vulnerabilities": []}
        mock_requests_get.return_value = mock_response

        service_info = {'product': 'Nginx', 'version': '1.20.1'}
        api_key = 'test-api-key'

        # Act
        check_vulnerabilities(service_info, api_key=api_key)

        # Assert
        mock_sleep.assert_called_once_with(0.6) # Faster delay with key
        # Check that the apiKey header was set correctly
        called_headers = mock_requests_get.call_args[1]['headers']
        self.assertIn('apiKey', called_headers)
        self.assertEqual(called_headers['apiKey'], api_key)

    @patch('vuln_checker.requests.get')
    def test_check_vulnerabilities_api_error(self, mock_requests_get):
        """
        Test check_vulnerabilities when the NVD API returns an HTTP error.
        """
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Server Error")
        mock_requests_get.return_value = mock_response

        service_info = {'product': 'openssh', 'version': '8.2'}

        # Act
        vulnerabilities = check_vulnerabilities(service_info)

        # Assert
        self.assertEqual(len(vulnerabilities), 0)

    def test_check_vulnerabilities_no_product_or_version(self):
        """
        Test that the function returns an empty list if product or version are missing.
        """
        # Act
        results = check_vulnerabilities({'version': '1.0'})
        # Assert
        self.assertEqual(results, [])

if __name__ == '__main__':
    unittest.main()
