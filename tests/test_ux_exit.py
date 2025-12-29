
import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Path fix
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mocking modules that require root or hardware access BEFORE importing tui_app
sys.modules['modules.optimizer'] = MagicMock()
sys.modules['modules.gaming'] = MagicMock()

# Setup psutil mock with realistic values needed by dashboard.py
mock_psutil = MagicMock()
mock_psutil.cpu_percent.return_value = 10.0
mock_psutil.virtual_memory.return_value.percent = 50.0
mock_psutil.swap_memory.return_value.percent = 20.0
mock_psutil.disk_usage.return_value.percent = 60.0
mock_psutil.net_io_counters.return_value.bytes_sent = 1000
mock_psutil.net_io_counters.return_value.bytes_recv = 1000
mock_psutil.process_iter.return_value = [] # Return empty list for processes

sys.modules['psutil'] = mock_psutil

from src.ui.tui_app import OptimizerApp

class TestExitConfirmation(unittest.TestCase):
    @patch('src.ui.tui_app.KeyListener')
    @patch('src.ui.tui_app.Live')
    @patch('src.ui.tui_app.Confirm')
    @patch('src.ui.tui_app.Console')
    def test_exit_confirmation_yes(self, mock_console, mock_confirm, mock_live, mock_keylistener):
        """Test that exit works when confirmed"""

        # Setup mocks
        app = OptimizerApp()

        # Mock KeyListener context manager and get_key
        mock_listener_instance = MagicMock()
        mock_keylistener.return_value.__enter__.return_value = mock_listener_instance

        # Simulate '0' key press then stop loop
        mock_listener_instance.get_key.side_effect = ['0']

        # Simulate User saying YES to confirmation
        mock_confirm.ask.return_value = True

        # Run the app (should break loop after '0')
        app.run()

        # Verify Confirm.ask was called
        mock_confirm.ask.assert_called_once()
        self.assertIn("Çıkmak", mock_confirm.ask.call_args[0][0])

        # Verify Live was stopped before asking
        mock_live_instance = mock_live.return_value.__enter__.return_value
        mock_live_instance.stop.assert_called()

    @patch('src.ui.tui_app.KeyListener')
    @patch('src.ui.tui_app.Live')
    @patch('src.ui.tui_app.Confirm')
    @patch('src.ui.tui_app.Console')
    def test_exit_confirmation_no(self, mock_console, mock_confirm, mock_live, mock_keylistener):
        """Test that exit is cancelled when not confirmed"""

        # Setup mocks
        app = OptimizerApp()

        # Mock KeyListener context manager
        mock_listener_instance = MagicMock()
        mock_keylistener.return_value.__enter__.return_value = mock_listener_instance

        # Simulate '0' key press, then '0' again (to test loop continues)
        mock_listener_instance.get_key.side_effect = ['0', '0']
        mock_confirm.ask.side_effect = [False, True]

        app.run()

        # Confirm.ask should be called twice
        self.assertEqual(mock_confirm.ask.call_count, 2)

        # Live should be started again after first No
        mock_live_instance = mock_live.return_value.__enter__.return_value
        self.assertTrue(mock_live_instance.start.called)

if __name__ == '__main__':
    unittest.main()
