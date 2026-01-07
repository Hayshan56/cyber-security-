import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path to allow imports from scanner
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scanner import scan_target

class TestScanner(unittest.TestCase):

    @patch('scanner.nmap.PortScanner')
    def test_scan_target_success(self, mock_port_scanner_class):
        """
        Test the scan_target function with a successful scan result containing open ports.
        """
        # Arrange
        mock_scanner_instance = MagicMock()
        mock_port_scanner_class.return_value = mock_scanner_instance

        target_ip = '127.0.0.1'
        # This is a simulated structure of the nmap scan result
        mock_scan_result = {
            target_ip: {
                'tcp': {
                    22: {'state': 'open', 'name': 'ssh', 'product': 'OpenSSH', 'version': '8.2p1'},
                    80: {'state': 'open', 'name': 'http', 'product': 'Apache httpd', 'version': '2.4.41'},
                    443: {'state': 'closed', 'name': 'https', 'product': '', 'version': ''} # This closed port should be ignored
                }
            }
        }

        # Configure the mock to behave like the real nmap object
        mock_scanner_instance.all_hosts.return_value = [target_ip]
        # Make the mock instance subscriptable like a dictionary to access results
        mock_scanner_instance.__getitem__.side_effect = mock_scan_result.__getitem__

        # Act
        results = scan_target(target_ip)

        # Assert
        mock_scanner_instance.scan.assert_called_once_with(target_ip, arguments='-sV -T4')
        expected_results = {
            22: {'service': 'ssh', 'product': 'OpenSSH', 'version': '8.2p1'},
            80: {'service': 'http', 'product': 'Apache httpd', 'version': '2.4.41'}
        }
        self.assertEqual(results, expected_results)

    @patch('scanner.nmap.PortScanner')
    def test_scan_target_host_down(self, mock_port_scanner_class):
        """
        Test the scan_target function for a case where the host appears to be down.
        """
        # Arrange
        mock_scanner_instance = MagicMock()
        mock_port_scanner_class.return_value = mock_scanner_instance
        target_ip = '127.0.0.1'

        # Simulate the host being down by returning an empty list of hosts
        mock_scanner_instance.all_hosts.return_value = []

        # Act
        results = scan_target(target_ip)

        # Assert
        self.assertIsNone(results)

    @patch('scanner.nmap.PortScanner')
    def test_scan_target_no_open_tcp_ports(self, mock_port_scanner_class):
        """
        Test the scan_target function when a host is up but has no open TCP ports.
        """
        # Arrange
        mock_scanner_instance = MagicMock()
        mock_port_scanner_class.return_value = mock_scanner_instance
        target_ip = '127.0.0.1'

        # Simulate a result with no 'tcp' key
        mock_scan_result = {
            target_ip: {
                'udp': { 53: {'state': 'open'} }
            }
        }
        mock_scanner_instance.all_hosts.return_value = [target_ip]
        mock_scanner_instance.__getitem__.side_effect = mock_scan_result.__getitem__

        # Act
        results = scan_target(target_ip)

        # Assert
        self.assertEqual(results, {})

if __name__ == '__main__':
    unittest.main()
