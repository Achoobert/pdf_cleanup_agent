"""
Unit tests for configuration management system.

Tests the AppConfig and AppSettings classes for proper configuration
loading, saving, validation, and error handling.
"""

import os
import sys
import tempfile
import shutil
import yaml
import unittest
from unittest.mock import patch, MagicMock

# Add the scripts directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ui.utils.config import AppConfig, AppSettings, ConfigValidationError


class TestAppSettings(unittest.TestCase):
    """Test cases for AppSettings dataclass."""
    
    def test_default_initialization(self):
        """Test that AppSettings initializes with correct defaults."""
        settings = AppSettings()
        
        self.assertEqual(settings.model_backend, "ollama")
        self.assertEqual(settings.model_name, "llama3:8b")
        self.assertEqual(settings.chunk_size, 4000)
        self.assertEqual(settings.api_endpoint, "http://localhost:11434/api/generate")
        
        # Check default directories
        expected_dirs = {
            'pdf_source': 'data/pdf',
            'txt_output': 'data/txt_input',
            'markdown_output': 'data/markdown',
            'json_output': 'data/json',
            'post_processed_markdown': 'data/post_processed_markdown',
            'output': 'data/output',
            'temp': 'data/temp'
        }
        self.assertEqual(settings.data_directories, expected_dirs)
        
        # Check default UI preferences
        expected_ui = {
            'window_width': 900,
            'window_height': 600,
            'theme': 'default',
            'auto_refresh': True,
            'show_console': True
        }
        self.assertEqual(settings.ui_preferences, expected_ui)
        
        # Check default processing steps
        expected_steps = {
            1: "pdf_segmentation",
            2: "llm_cleaning", 
            3: "post_processing_cleanup",
            4: "post_processing_formatting",
            5: "vtt_conversion"
        }
        self.assertEqual(settings.processing_steps, expected_steps)
        
    def test_custom_initialization(self):
        """Test AppSettings with custom values."""
        custom_dirs = {
            'pdf_source': 'custom/pdf',
            'txt_output': 'custom/txt',
            'markdown_output': 'custom/md',
            'json_output': 'custom/json',
            'output': 'custom/output'
        }
        custom_ui = {'window_width': 1200, 'theme': 'dark'}
        
        settings = AppSettings(
            model_backend="openai",
            model_name="gpt-4",
            chunk_size=2000,
            data_directories=custom_dirs,
            ui_preferences=custom_ui
        )
        
        self.assertEqual(settings.model_backend, "openai")
        self.assertEqual(settings.model_name, "gpt-4")
        self.assertEqual(settings.chunk_size, 2000)
        
        # Custom directories should be used
        self.assertIn('pdf_source', settings.data_directories)
        self.assertEqual(settings.data_directories['pdf_source'], 'custom/pdf')
        
    def test_validation_positive_chunk_size(self):
        """Test that chunk_size must be positive."""
        with self.assertRaises(ValueError) as context:
            AppSettings(chunk_size=0)
        self.assertIn("chunk_size must be positive", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            AppSettings(chunk_size=-100)
        self.assertIn("chunk_size must be positive", str(context.exception))
        
    def test_validation_empty_fields(self):
        """Test validation of required fields."""
        with self.assertRaises(ValueError) as context:
            AppSettings(model_backend="")
        self.assertIn("model_backend cannot be empty", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            AppSettings(model_name="")
        self.assertIn("model_name cannot be empty", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            AppSettings(api_endpoint="")
        self.assertIn("api_endpoint cannot be empty", str(context.exception))
        
    def test_validation_required_directories(self):
        """Test validation of required directories."""
        incomplete_dirs = {'pdf_source': 'data/pdf'}  # Missing required directories
        
        with self.assertRaises(ValueError) as context:
            AppSettings(data_directories=incomplete_dirs)
        self.assertIn("Required directory", str(context.exception))
        
    def test_to_dict(self):
        """Test conversion to dictionary."""
        settings = AppSettings(model_backend="test", chunk_size=1000)
        result = settings.to_dict()
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['model_backend'], "test")
        self.assertEqual(result['chunk_size'], 1000)
        
    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            'model_backend': 'test',
            'model_name': 'test-model',
            'chunk_size': 1000,
            'api_endpoint': 'http://test.com'
        }
        
        settings = AppSettings.from_dict(data)
        self.assertEqual(settings.model_backend, 'test')
        self.assertEqual(settings.model_name, 'test-model')
        self.assertEqual(settings.chunk_size, 1000)


class TestAppConfig(unittest.TestCase):
    """Test cases for AppConfig class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, 'test_config.yml')
        self.config = AppConfig(config_path=self.config_path)
        
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_initialization(self):
        """Test AppConfig initialization."""
        self.assertIsNone(self.config.settings)
        self.assertEqual(self.config.config_path, self.config_path)
        
    def test_load_config_file_not_exists(self):
        """Test loading config when file doesn't exist."""
        result = self.config.load_config()
        
        self.assertTrue(result)
        self.assertIsNotNone(self.config.settings)
        self.assertIsInstance(self.config.settings, AppSettings)
        self.assertTrue(os.path.exists(self.config_path))
        
    def test_load_config_valid_file(self):
        """Test loading valid configuration file."""
        config_data = {
            'settings': {
                'model_backend': 'openai',
                'model': 'gpt-4',
                'chunk_size': 2000,
                'ollama_api': 'http://test.com/api'
            },
            'directories': {
                'pdf_source': 'test/pdf',
                'txt_output': 'test/txt',
                'markdown_output': 'test/md',
                'json_output': 'test/json'
            },
            'steps': {
                '1': 'step1',
                '2': 'step2'
            },
            'pdf_files': [
                {'name': 'test.pdf', 'path': 'test/test.pdf'}
            ]
        }
        
        with open(self.config_path, 'w') as f:
            yaml.dump(config_data, f)
            
        result = self.config.load_config()
        
        self.assertTrue(result)
        self.assertEqual(self.config.settings.model_backend, 'openai')
        self.assertEqual(self.config.settings.model_name, 'gpt-4')
        self.assertEqual(self.config.settings.chunk_size, 2000)
        self.assertEqual(self.config.settings.data_directories['pdf_source'], 'test/pdf')
        self.assertEqual(self.config.settings.processing_steps[1], 'step1')
        self.assertEqual(len(self.config.settings.pdf_files), 1)
        
    def test_load_config_empty_file(self):
        """Test loading empty configuration file."""
        with open(self.config_path, 'w') as f:
            f.write('')
            
        result = self.config.load_config()
        
        self.assertFalse(result)
        self.assertIsNotNone(self.config.settings)  # Fallback config created
        
    def test_load_config_invalid_yaml(self):
        """Test loading invalid YAML file."""
        with open(self.config_path, 'w') as f:
            f.write('invalid: yaml: content: [')
            
        result = self.config.load_config()
        
        self.assertFalse(result)
        self.assertIsNotNone(self.config.settings)  # Fallback config created
        
    def test_save_config_success(self):
        """Test successful configuration saving."""
        self.config.settings = AppSettings(model_backend='test')
        
        result = self.config.save_config()
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.config_path))
        
        # Verify saved content
        with open(self.config_path, 'r') as f:
            saved_data = yaml.safe_load(f)
            
        self.assertEqual(saved_data['settings']['model_backend'], 'test')
        
    def test_save_config_no_settings(self):
        """Test saving when no settings are available."""
        result = self.config.save_config()
        
        self.assertFalse(result)
        
    def test_save_config_permission_error(self):
        """Test saving with permission error."""
        self.config.settings = AppSettings()
        
        # Create a directory where the file should be (causes permission error)
        os.makedirs(self.config_path, exist_ok=True)
        
        result = self.config.save_config()
        
        self.assertFalse(result)
        
    def test_get_setting(self):
        """Test getting specific settings."""
        self.config.settings = AppSettings(model_backend='test')
        
        self.assertEqual(self.config.get_setting('model_backend'), 'test')
        self.assertEqual(self.config.get_setting('nonexistent', 'default'), 'default')
        self.assertEqual(self.config.get_setting('ui_preferences.theme'), 'default')
        
    def test_set_setting(self):
        """Test setting specific settings."""
        self.config.settings = AppSettings()
        
        self.config.set_setting('model_backend', 'new_backend')
        self.assertEqual(self.config.settings.model_backend, 'new_backend')
        
        self.config.set_setting('ui_preferences.theme', 'dark')
        self.assertEqual(self.config.settings.ui_preferences['theme'], 'dark')
        
    def test_get_data_directory(self):
        """Test getting data directory paths."""
        self.config.settings = AppSettings()
        
        pdf_dir = self.config.get_data_directory('pdf_source')
        self.assertTrue(pdf_dir.endswith('data/pdf'))
        
        # Test invalid directory type
        with self.assertRaises(ValueError):
            self.config.get_data_directory('nonexistent')
            
    def test_ensure_directories_exist(self):
        """Test directory creation."""
        self.config.settings = AppSettings()
        
        # Mock the directory paths to use temp directory
        test_dirs = {
            'pdf_source': os.path.join(self.temp_dir, 'pdf'),
            'output': os.path.join(self.temp_dir, 'output')
        }
        self.config.settings.data_directories = test_dirs
        
        result = self.config.ensure_directories_exist()
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(test_dirs['pdf_source']))
        self.assertTrue(os.path.exists(test_dirs['output']))
        
    def test_reset_to_defaults(self):
        """Test resetting configuration to defaults."""
        self.config.settings = AppSettings(model_backend='custom')
        
        result = self.config.reset_to_defaults()
        
        self.assertTrue(result)
        self.assertEqual(self.config.settings.model_backend, 'ollama')  # Default value
        
    def test_validate_current_config(self):
        """Test configuration validation."""
        self.config.settings = AppSettings()
        self.assertTrue(self.config.validate_current_config())
        
        # Test invalid config
        self.config.settings.chunk_size = -1
        self.assertFalse(self.config.validate_current_config())
        
    def test_initialize(self):
        """Test configuration initialization."""
        result = self.config.initialize()
        
        self.assertTrue(result)
        self.assertIsNotNone(self.config.settings)
        
    def test_signals_emitted(self):
        """Test that appropriate signals are emitted."""
        config_loaded_emitted = False
        config_saved_emitted = False
        config_error_emitted = False
        
        def on_config_loaded():
            nonlocal config_loaded_emitted
            config_loaded_emitted = True
            
        def on_config_saved():
            nonlocal config_saved_emitted
            config_saved_emitted = True
            
        def on_config_error(msg):
            nonlocal config_error_emitted
            config_error_emitted = True
            
        self.config.config_loaded.connect(on_config_loaded)
        self.config.config_saved.connect(on_config_saved)
        self.config.config_error.connect(on_config_error)
        
        # Test load signal
        self.config.load_config()
        self.assertTrue(config_loaded_emitted)
        
        # Test save signal
        self.config.save_config()
        self.assertTrue(config_saved_emitted)
        
        # Test error signal (by trying to load invalid YAML)
        with open(self.config_path, 'w') as f:
            f.write('invalid: yaml: [')
        self.config.load_config()
        self.assertTrue(config_error_emitted)


class TestConfigValidationError(unittest.TestCase):
    """Test cases for ConfigValidationError exception."""
    
    def test_exception_creation(self):
        """Test that ConfigValidationError can be created and raised."""
        with self.assertRaises(ConfigValidationError) as context:
            raise ConfigValidationError("Test error message")
            
        self.assertEqual(str(context.exception), "Test error message")


if __name__ == '__main__':
    # Set up logging to reduce noise during tests
    import logging
    logging.getLogger().setLevel(logging.CRITICAL)
    
    unittest.main()