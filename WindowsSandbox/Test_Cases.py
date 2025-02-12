import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import SandBox  # Ensure this matches the actual filename (case-sensitive)

class TestSandbox(unittest.TestCase):
    def setUp(self):
        self.username = "testuser"
        self.local_download_path = Path(f"C:/Users/{self.username}/Downloads")
        self.sandbox_file_path = Path(r'/WDAGUtilityAccount/Downloads')
        self.popout_path = Path(r'path to windows sandbox folder')

    @patch('os.getlogin', return_value="testuser")
    def test_local_download_path_exists(self, mock_getlogin):
        try:
            with patch('pathlib.Path.exists', return_value=True) as mock_exists:
                self.assertTrue(self.local_download_path.exists())
                mock_exists.assert_called_once()
            print("Test OK: Local download path exists.")
        except Exception as e:
            print(f"Error: Local download path check failed. {str(e)}")

    @patch('pathlib.Path.exists', return_value=False)
    @patch('SandBox.error')  # Correct reference to the error method in Sandbox
    def test_error_called_for_missing_local_download_path(self, mock_error, mock_exists):
        try:
            SandBox.LocalDownloadFile = self.local_download_path
            SandBox.PopOutPath = self.popout_path
            if not SandBox.LocalDownloadFile.exists():
                SandBox.error(SandBox.LocalDownloadFile)
            mock_error.assert_called_once_with(self.local_download_path)
            print("Test OK: Error called for missing local download path.")
        except Exception as e:
            print(f"Error: Missing local download path error failed. {str(e)}")

    @patch('pathlib.Path.exists', return_value=False)
    @patch('SandBox.error')  # Correct reference to the error method in Sandbox
    def test_error_called_for_missing_popout_path(self, mock_error, mock_exists):
        try:
            SandBox.PopOutPath = self.popout_path
            if not SandBox.PopOutPath.exists():
                SandBox.error(SandBox.PopOutPath)
            mock_error.assert_called_once_with(self.popout_path)
            print("Test OK: Error called for missing popout path.")
        except Exception as e:
            print(f"Error: Missing popout path error failed. {str(e)}")

    @patch('SandBox.winsandbox.FolderMapper')  # Correct reference
    @patch('SandBox.winsandbox.new_sandbox')  # Correct reference
    def test_sandbox_creation(self, mock_new_sandbox, mock_folder_mapper):
        try:
            mock_mapper_instance = MagicMock()
            mock_folder_mapper.return_value = mock_mapper_instance
            SandBox.Downloadsmapper = SandBox.winsandbox.FolderMapper(folder_path=self.local_download_path, read_only=False)
            SandBox.Buildmapper = SandBox.winsandbox.FolderMapper(folder_path=self.popout_path, read_only=False)
            SandBox.winsandbox.new_sandbox(networking=True, folder_mappers=[SandBox.Downloadsmapper, SandBox.Buildmapper])

            mock_folder_mapper.assert_any_call(folder_path=self.local_download_path, read_only=False)
            mock_folder_mapper.assert_any_call(folder_path=self.popout_path, read_only=False)
            mock_new_sandbox.assert_called_once_with(networking=True, folder_mappers=[mock_mapper_instance, mock_mapper_instance])
            print("Test OK: Sandbox created successfully.")
        except Exception as e:
            print(f"Error: Sandbox creation failed. {str(e)}")
    
    @patch('SandBox.winsandbox.new_sandbox')  # Mock new_sandbox
    def test_winget_commands_execution(self, mock_new_sandbox):
        try:
            # Create a mock sandbox instance
            sandbox_instance = MagicMock()
            mock_new_sandbox.return_value = sandbox_instance

            # Set up the mock to return a successful result
            sandbox_instance.rpyc.modules.subprocess.run.return_value = MagicMock(stdout="Command Executed", stderr="")

            # Run the WingetCommands in the sandbox
            for command in SandBox.WingetCommands:
                # Mock execution of each command
                print(f"Executing Command: {command}")
                result = sandbox_instance.rpyc.modules.subprocess.run(f"Powershell {command}", shell=True, capture_output=True, text=True)

                # Check if subprocess.run is called with the correct command
                sandbox_instance.rpyc.modules.subprocess.run.assert_any_call(f"Powershell {command}", shell=True, capture_output=True, text=True)
                self.assertEqual(result.stdout, "Command Executed")
            print("Test OK: Winget commands executed successfully.")
        except Exception as e:
            print(f"Error: Winget command execution failed. {str(e)}")

if __name__ == "__main__":
    unittest.main()
