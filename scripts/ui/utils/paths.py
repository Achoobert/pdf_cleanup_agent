"""
Path Management Utilities

Provides centralized path management for the application.
"""

import os
from typing import Dict


class PathManager:
    """
    Centralized path management for the application.
    
    This class provides methods to get various paths used throughout
    the application in a consistent manner.
    """
    
    def __init__(self):
        self._base_dir = self._get_base_directory()
        self._data_dir = os.path.join(self._base_dir, 'data')
        self._scripts_dir = os.path.join(self._base_dir, 'scripts')
        
    def _get_base_directory(self) -> str:
        """Get the base application directory."""
        return os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', '..', '..'
        ))
        
    @property
    def base_dir(self) -> str:
        """Get the base application directory."""
        return self._base_dir
        
    @property
    def data_dir(self) -> str:
        """Get the data directory."""
        return self._data_dir
        
    @property
    def scripts_dir(self) -> str:
        """Get the scripts directory."""
        return self._scripts_dir
        
    def get_data_subdir(self, subdir: str) -> str:
        """
        Get a subdirectory within the data directory.
        
        Args:
            subdir: Subdirectory name
            
        Returns:
            Absolute path to the subdirectory
        """
        return os.path.join(self._data_dir, subdir)
        
    def get_pdf_dir(self) -> str:
        """Get the PDF data directory."""
        return self.get_data_subdir('pdf')
        
    def get_markdown_dir(self) -> str:
        """Get the markdown data directory."""
        return self.get_data_subdir('markdown')
        
    def get_json_dir(self) -> str:
        """Get the JSON data directory."""
        return self.get_data_subdir('json')
        
    def get_output_dir(self) -> str:
        """Get the output data directory."""
        return self.get_data_subdir('output')
        
    def get_temp_dir(self) -> str:
        """Get the temporary data directory."""
        return self.get_data_subdir('temp')
        
    def get_prompts_dir(self) -> str:
        """Get the prompts directory."""
        return os.path.join(self._base_dir, 'prompts')
        
    def get_config_file(self) -> str:
        """Get the main configuration file path."""
        return os.path.join(self._base_dir, 'pipeline_config.yml')
        
    def get_script_path(self, script_name: str) -> str:
        """
        Get the path to a script file.
        
        Args:
            script_name: Name of the script file
            
        Returns:
            Absolute path to the script
        """
        return os.path.join(self._scripts_dir, script_name)
        
    def get_ui_script_path(self, script_name: str) -> str:
        """
        Get the path to a UI script file.
        
        Args:
            script_name: Name of the UI script file
            
        Returns:
            Absolute path to the UI script
        """
        return os.path.join(self._scripts_dir, 'ui', script_name)
        
    def get_venv_python(self) -> str:
        """
        Get the path to the virtual environment Python executable.
        
        Returns:
            Path to Python executable (venv if available, system otherwise)
        """
        venv_python = os.path.join(self._base_dir, 'venv', 'bin', 'python')
        if os.path.exists(venv_python):
            return venv_python
        
        # Fallback to system Python
        import sys
        return sys.executable
        
    def ensure_directory_exists(self, path: str) -> bool:
        """
        Ensure a directory exists, creating it if necessary.
        
        Args:
            path: Directory path to ensure exists
            
        Returns:
            True if directory exists or was created successfully
        """
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except Exception:
            return False
            
    def get_all_data_directories(self) -> Dict[str, str]:
        """
        Get all data directories as a dictionary.
        
        Returns:
            Dictionary mapping directory names to paths
        """
        return {
            'pdf': self.get_pdf_dir(),
            'markdown': self.get_markdown_dir(),
            'json': self.get_json_dir(),
            'output': self.get_output_dir(),
            'temp': self.get_temp_dir()
        }
        
    def ensure_all_data_directories(self) -> bool:
        """
        Ensure all data directories exist.
        
        Returns:
            True if all directories exist or were created successfully
        """
        directories = self.get_all_data_directories()
        success = True
        
        for name, path in directories.items():
            if not self.ensure_directory_exists(path):
                success = False
                
        return success