"""
Integration tests for configuration management system.

Tests the configuration system with actual project files and structure.
"""

import os
import sys
import tempfile
import shutil
import unittest

# Add the scripts directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ui.utils.config import AppConfig, AppSettings


class TestConfigIntegration(unittest.TestCase):
    """Integration tests for configuration management."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_load_actual_pipeline_config(self):
        """Test loading the actual pipeline_config.yml file."""
        # Get the actual config path
        project_root = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', '..'
        ))
        config_path = os.path.join(project_root, 'pipeline_config.yml')
        
        if not os.path.exists(config_path):
            self.skipTest("pipeline_config.yml not found")
            
        config = AppConfig(config_path=config_path)
        result = config.load_config()
        
        self.assertTrue(result)
        self.assertIsNotNone(config.settings)
        
        # Verify some expected values from the actual config
        self.assertIsInstance(config.settings.chunk_size, int)
        self.assertIsInstance(config.settings.model_name, str)
        self.assertIsInstance(config.settings.data_directories, dict)
        
    def test_directory_creation_with_actual_structure(self):
        """Test directory creation with project-like structure."""
        config_path = os.path.join(self.temp_dir, 'test_config.yml')
        config = AppConfig(config_path=config_path)
        
        # Initialize with default settings
        config.initialize()
        
        # Update directories to use temp directory
        for key in config.settings.data_directories:
            config.settings.data_directories[key] = os.path.join(
                self.temp_dir, 'data', key.replace('_', '/')
            )
            
        # Ensure directories exist
        result = config.ensure_directories_exist()
        self.assertTrue(result)
        
        # Verify directories were created
        for dir_path in config.settings.data_directories.values():
            self.assertTrue(os.path.exists(dir_path))
            
    def test_config_persistence(self):
        """Test that configuration persists across load/save cycles."""
        config_path = os.path.join(self.temp_dir, 'persistence_test.yml')
        
        # Create and configure first instance
        config1 = AppConfig(config_path=config_path)
        config1.initialize()
        
        original_backend = config1.settings.model_backend
        original_chunk_size = config1.settings.chunk_size
        
        # Modify settings
        config1.settings.model_backend = "test_backend"
        config1.settings.chunk_size = 9999
        config1.save_config()
        
        # Create second instance and load
        config2 = AppConfig(config_path=config_path)
        config2.load_config()
        
        # Verify changes persisted
        self.assertEqual(config2.settings.model_backend, "test_backend")
        self.assertEqual(config2.settings.chunk_size, 9999)
        
        # Restore original values
        config2.settings.model_backend = original_backend
        config2.settings.chunk_size = original_chunk_size
        config2.save_config()
        
        # Verify restoration
        config3 = AppConfig(config_path=config_path)
        config3.load_config()
        self.assertEqual(config3.settings.model_backend, original_backend)
        self.assertEqual(config3.settings.chunk_size, original_chunk_size)
        
    def test_error_recovery(self):
        """Test error recovery scenarios."""
        config_path = os.path.join(self.temp_dir, 'error_test.yml')
        
        # Create config with invalid YAML
        with open(config_path, 'w') as f:
            f.write('invalid: yaml: content: [')
            
        config = AppConfig(config_path=config_path)
        
        # Should handle error gracefully and create fallback
        result = config.load_config()
        self.assertFalse(result)  # Load failed
        self.assertIsNotNone(config.settings)  # But fallback was created
        
        # Should be able to save valid config after error
        save_result = config.save_config()
        self.assertTrue(save_result)
        
        # Should be able to load the corrected config
        config2 = AppConfig(config_path=config_path)
        load_result = config2.load_config()
        self.assertTrue(load_result)


if __name__ == '__main__':
    # Set up logging to reduce noise during tests
    import logging
    logging.getLogger().setLevel(logging.CRITICAL)
    
    unittest.main()