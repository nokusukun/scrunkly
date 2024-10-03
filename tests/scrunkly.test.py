import unittest
from unittest.mock import patch, call
from src import scrunkly


class TestScrunkly(unittest.TestCase):

    @patch('subprocess.run')
    def test_script_execution(self, mock_run):
        script_map = {
            "test_script": "echo 'Test Script Running'"
        }
        with patch('sys.argv', ['script.py', 'test_script']):
            scrunkly.scripts(script_map)

        mock_run.assert_called_once_with("echo 'Test Script Running'", shell=True)

    @patch('subprocess.run')
    def test_sub_script_execution(self, mock_run):
        script_map = {
            "setup": ["install", "start"],
            "install": "echo 'Installing...'",
            "start": "echo 'Starting...'",
        }
        with patch('sys.argv', ['script.py', 'setup']):
            scrunkly.scripts(script_map)

        mock_run.assert_has_calls([call("echo 'Installing...'", shell=True),
                                   call("echo 'Starting...'", shell=True)])

    def test_self_referencing_script(self):
        script_map = {
            "self_ref": "self_ref"
        }
        with patch('sys.argv', ['script.py', 'self_ref']):
            with self.assertRaises(Exception) as context:
                scrunkly.scripts(script_map)
            self.assertEqual(str(context.exception), "Cannot call self-referencing script")

    @patch('subprocess.run')
    def test_callable_script(self, mock_run):
        def custom_function(*args):
            print(f"Custom function called with args: {args}")

        script_map = {
            "custom_func": custom_function
        }

        with patch('sys.argv', ['script.py', 'custom_func']):
            with patch('builtins.print') as mock_print:
                scrunkly.scripts(script_map)

        mock_print.assert_called_with('Custom function called with args: ()')

    @patch('subprocess.run')
    def test_callable_with_args(self, mock_run):
        def custom_function(arg1, arg2):
            print(f"Custom function called with args: {arg1}, {arg2}")

        script_map = {
            "custom_func": custom_function
        }

        with patch('sys.argv', ['script.py', 'custom_func', 'arg1', 'arg2']):
            with patch('builtins.print') as mock_print:
                scrunkly.scripts(script_map)

        mock_print.assert_called_with('Custom function called with args: arg1, arg2')

    @patch('subprocess.run')
    def test_script_with_args(self, mock_run):
        script_map = {
            "test_script_with_args": "echo 'Args: {} {}'"
        }
        with patch('sys.argv', ['script.py', 'test_script_with_args', 'arg1', 'arg2']):
            scrunkly.scripts(script_map)

        mock_run.assert_called_once_with("echo 'Args: arg1 arg2'", shell=True)


if __name__ == '__main__':
    unittest.main()
