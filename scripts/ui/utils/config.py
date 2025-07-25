"""
Configuration Management

Handles application configuration loading and management.
"""

import os
import yaml
import logging
from dataclasses import dataclass, asdict, field
from typing import Dict, Any, Optional, List
from PyQt5.QtCore import QObject, pyqtSignal


@dataclass
class AppSettings:
    """
    Application settings data structure.
    
    This dataclass holds all configuration settings for the application.
    Provides type-safe configuration management with validation.
    """
    model_backend: str = "ollama"
    model_name: str = "llama3:8b"
    chunk_size: int = 4000
    api_endpoint: str = "http://localhost:11434/api/generate"
    data_directories: Dict[str, str] = field(default_factory=dict)
    ui_preferences: Dict[str, Any] = field(default_factory=dict)
    processing_steps: Dict[int, str] = field(default_factory=dict)
    pdf_files: List[Dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize default values for complex fields and validate settings."""
        if not self.data_directories:
            self.data_directories = {
                'pdf_source': 'data/pdf',
                'txt_output': 'data/txt_input',
                'markdown_output': 'data/markdown',
                'json_output': 'data/json',
                'post_processed_markdown': 'data/post_processed_markdown',
                'output': 'data/output',
                'temp': 'data/temp'
            }
            
        if not self.ui_preferences:
            self.ui_preferences = {
                'window_width': 900,
                'window_height': 600,
                'theme': 'default',
                'auto_refresh': True,
                'show_console': True
            }
            
        if not self.processing_steps:
            self.processing_steps = {
                1: "pdf_segmentation",
                2: "llm_cleaning", 
                3: "post_processing_cleanup",
                4: "post_processing_formatting",
                5: "vtt_conversion"
            }
            
        # Validate settings
        self._validate()
        
    def _validate(self):
        """Validate configuration settings."""
        if self.chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
            
        if not self.model_backend:
            raise ValueError("model_backend cannot be empty")
            
        if not self.model_name:
            raise ValueError("model_name cannot be empty")
            
        if not self.api_endpoint:
            raise ValueError("api_endpoint cannot be empty")
            
        # Validate required directories
        required_dirs = ['pdf_source', 'txt_output', 'markdown_output', 'json_output']
        for dir_key in required_dirs:
            if dir_key not in self.data_directories:
                raise ValueError(f"Required directory '{dir_key}' not configured")
                
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary format."""
        return asdict(self)
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AppSettings':
        """Create AppSettings from dictionary data."""
        return cls(**data)


class ConfigValidationError(Exception):
    """Exception raised when configuration validation fails."""
    pass


class AppConfig(QObject):
    """
    Application configuration manager.
    
    This class handles loading, saving, and managing application configuration
    from YAML files with comprehensive error handling and validation.
    """
    
    # Signals for configuration events
    config_loaded = pyqtSignal()
    config_saved = pyqtSignal()
    config_error = pyqtSignal(str)  # error_message
    
    def __init__(self, config_path: Optional[str] = None, parent=None):
        super().__init__(parent)
        self.settings: Optional[AppSettings] = None
        self.config_path = config_path or self._get_default_config_path()
        self.logger = logging.getLogger(__name__)
        
    def _get_default_config_path(self) -> str:
        """Get the default path to the configuration file."""
        return os.path.abspath(os.path.join(
            os.path.dirname(__file__), 
            '..', '..', '..', 'pipeline_config.yml'
        ))
        
    def _validate_config_file(self, config_data: Dict[str, Any]) -> None:
        """
        Validate the structure of configuration data.
        
        Args:
            config_data: Configuration data to validate
            
        Raises:
            ConfigValidationError: If configuration is invalid
        """
        if not isinstance(config_data, dict):
            raise ConfigValidationError("Configuration must be a dictionary")
            
        # Check for required top-level sections
        required_sections = ['settings', 'directories']
        for section in required_sections:
            if section not in config_data:
                self.logger.warning(f"Missing configuration section: {section}")
                
        # Validate settings section if present
        if 'settings' in config_data:
            settings = config_data['settings']
            if not isinstance(settings, dict):
                raise ConfigValidationError("Settings section must be a dictionary")
                
        # Validate directories section if present  
        if 'directories' in config_data:
            directories = config_data['directories']
            if not isinstance(directories, dict):
                raise ConfigValidationError("Directories section must be a dictionary")
        
    def load_config(self) -> bool:
        """
        Load configuration from YAML file with comprehensive error handling.
        
        Returns:
            True if configuration was loaded successfully
        """
        try:
            if not os.path.exists(self.config_path):
                self.logger.info(f"Configuration file not found: {self.config_path}")
                self.logger.info("Creating default configuration")
                self.settings = AppSettings()
                self.save_config()
                self.config_loaded.emit()
                return True
                
            self.logger.info(f"Loading configuration from: {self.config_path}")
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
                
            if config_data is None:
                raise ConfigValidationError("Configuration file is empty")
                
            # Validate configuration structure
            self._validate_config_file(config_data)
            
            # Extract settings from the loaded configuration
            settings_data = config_data.get('settings', {})
            directories_data = config_data.get('directories', {})
            steps_data = config_data.get('steps', {})
            pdf_files_data = config_data.get('pdf_files', [])
            
            # Convert steps keys to integers if they're strings
            processing_steps = {}
            for key, value in steps_data.items():
                try:
                    processing_steps[int(key)] = value
                except (ValueError, TypeError):
                    self.logger.warning(f"Invalid step key: {key}")
            
            self.settings = AppSettings(
                model_backend=settings_data.get('model_backend', 'ollama'),
                model_name=settings_data.get('model', 'llama3:8b'),
                chunk_size=int(settings_data.get('chunk_size', 4000)),
                api_endpoint=settings_data.get('ollama_api', 'http://localhost:11434/api/generate'),
                data_directories=directories_data,
                ui_preferences=settings_data.get('ui_preferences', {}),
                processing_steps=processing_steps,
                pdf_files=pdf_files_data if isinstance(pdf_files_data, list) else []
            )
            
            self.logger.info("Configuration loaded successfully")
            self.config_loaded.emit()
            return True
            
        except yaml.YAMLError as e:
            error_msg = f"YAML parsing error: {e}"
            self.logger.error(error_msg)
            self.config_error.emit(error_msg)
            self._create_fallback_config()
            return False
            
        except ConfigValidationError as e:
            error_msg = f"Configuration validation error: {e}"
            self.logger.error(error_msg)
            self.config_error.emit(error_msg)
            self._create_fallback_config()
            return False
            
        except Exception as e:
            error_msg = f"Failed to load configuration: {e}"
            self.logger.error(error_msg)
            self.config_error.emit(error_msg)
            self._create_fallback_config()
            return False
            
    def _create_fallback_config(self):
        """Create fallback configuration when loading fails."""
        self.logger.info("Creating fallback configuration")
        self.settings = AppSettings()
        self.config_loaded.emit()
            
    def save_config(self) -> bool:
        """
        Save configuration to YAML file with error handling.
        
        Returns:
            True if configuration was saved successfully
        """
        if not self.settings:
            error_msg = "No settings to save"
            self.logger.error(error_msg)
            self.config_error.emit(error_msg)
            return False
            
        try:
            self.logger.info(f"Saving configuration to: {self.config_path}")
            
            # Load existing config to preserve other sections
            existing_config = {}
            if os.path.exists(self.config_path):
                try:
                    with open(self.config_path, 'r', encoding='utf-8') as f:
                        existing_config = yaml.safe_load(f) or {}
                except Exception as e:
                    self.logger.warning(f"Could not load existing config: {e}")
                    existing_config = {}
                    
            # Update configuration sections
            existing_config.update({
                'settings': {
                    'model_backend': self.settings.model_backend,
                    'model': self.settings.model_name,
                    'chunk_size': self.settings.chunk_size,
                    'ollama_api': self.settings.api_endpoint,
                    'ui_preferences': self.settings.ui_preferences
                },
                'directories': self.settings.data_directories,
                'steps': self.settings.processing_steps,
                'pdf_files': self.settings.pdf_files
            })
            
            # Ensure directory exists
            config_dir = os.path.dirname(self.config_path)
            if config_dir:
                os.makedirs(config_dir, exist_ok=True)
            
            # Create backup of existing config
            if os.path.exists(self.config_path):
                backup_path = f"{self.config_path}.backup"
                try:
                    import shutil
                    shutil.copy2(self.config_path, backup_path)
                    self.logger.debug(f"Created backup: {backup_path}")
                except Exception as e:
                    self.logger.warning(f"Could not create backup: {e}")
            
            # Write configuration
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(existing_config, f, default_flow_style=False, indent=2)
                
            self.logger.info("Configuration saved successfully")
            self.config_saved.emit()
            return True
            
        except PermissionError as e:
            error_msg = f"Permission denied saving configuration: {e}"
            self.logger.error(error_msg)
            self.config_error.emit(error_msg)
            return False
            
        except Exception as e:
            error_msg = f"Failed to save configuration: {e}"
            self.logger.error(error_msg)
            self.config_error.emit(error_msg)
            return False
            
    def get_setting(self, key: str, default=None):
        """
        Get a specific setting value.
        
        Args:
            key: Setting key (dot notation supported, e.g., 'ui_preferences.theme')
            default: Default value if setting not found
            
        Returns:
            Setting value or default
        """
        if not self.settings:
            return default
            
        try:
            value = self.settings
            for part in key.split('.'):
                if hasattr(value, part):
                    value = getattr(value, part)
                elif isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return default
            return value
        except Exception:
            return default
            
    def set_setting(self, key: str, value):
        """
        Set a specific setting value.
        
        Args:
            key: Setting key (dot notation supported)
            value: Value to set
        """
        if not self.settings:
            self.settings = AppSettings()
            
        try:
            # Handle simple keys
            if '.' not in key:
                if hasattr(self.settings, key):
                    setattr(self.settings, key, value)
                return
                
            # Handle nested keys
            parts = key.split('.')
            obj = self.settings
            
            for part in parts[:-1]:
                if hasattr(obj, part):
                    obj = getattr(obj, part)
                elif isinstance(obj, dict):
                    if part not in obj:
                        obj[part] = {}
                    obj = obj[part]
                    
            # Set the final value
            final_key = parts[-1]
            if hasattr(obj, final_key):
                setattr(obj, final_key, value)
            elif isinstance(obj, dict):
                obj[final_key] = value
                
        except Exception as e:
            self.config_error.emit(f"Failed to set setting {key}: {e}")
            
    def get_data_directory(self, dir_type: str) -> str:
        """
        Get a data directory path with validation.
        
        Args:
            dir_type: Type of directory ('pdf_source', 'markdown_output', 'json_output', etc.)
            
        Returns:
            Absolute path to the directory
            
        Raises:
            ValueError: If directory type is not configured
        """
        if not self.settings or not self.settings.data_directories:
            # Return default path
            base_dir = os.path.abspath(os.path.join(
                os.path.dirname(__file__), '..', '..', '..', 'data'
            ))
            return os.path.join(base_dir, dir_type)
            
        if dir_type not in self.settings.data_directories:
            available_dirs = list(self.settings.data_directories.keys())
            raise ValueError(f"Directory type '{dir_type}' not configured. Available: {available_dirs}")
            
        relative_path = self.settings.data_directories[dir_type]
        
        # Convert to absolute path
        if os.path.isabs(relative_path):
            return relative_path
        else:
            base_dir = os.path.abspath(os.path.join(
                os.path.dirname(__file__), '..', '..', '..'
            ))
            return os.path.join(base_dir, relative_path)
            
    def ensure_directories_exist(self) -> bool:
        """
        Ensure all configured directories exist.
        
        Returns:
            True if all directories were created successfully
        """
        if not self.settings or not self.settings.data_directories:
            return False
            
        try:
            for dir_type in self.settings.data_directories:
                dir_path = self.get_data_directory(dir_type)
                os.makedirs(dir_path, exist_ok=True)
                self.logger.debug(f"Ensured directory exists: {dir_path}")
            return True
        except Exception as e:
            error_msg = f"Failed to create directories: {e}"
            self.logger.error(error_msg)
            self.config_error.emit(error_msg)
            return False
            
    def reset_to_defaults(self) -> bool:
        """
        Reset configuration to default values.
        
        Returns:
            True if reset was successful
        """
        try:
            self.logger.info("Resetting configuration to defaults")
            self.settings = AppSettings()
            return self.save_config()
        except Exception as e:
            error_msg = f"Failed to reset configuration: {e}"
            self.logger.error(error_msg)
            self.config_error.emit(error_msg)
            return False
            
    def validate_current_config(self) -> bool:
        """
        Validate the current configuration.
        
        Returns:
            True if configuration is valid
        """
        if not self.settings:
            return False
            
        try:
            # This will raise an exception if validation fails
            self.settings._validate()
            return True
        except Exception as e:
            error_msg = f"Configuration validation failed: {e}"
            self.logger.error(error_msg)
            self.config_error.emit(error_msg)
            return False
            
    def initialize(self) -> bool:
        """
        Initialize the configuration manager.
        
        Returns:
            True if initialization was successful
        """
        success = self.load_config()
        if success:
            # Ensure directories exist after loading config
            self.ensure_directories_exist()
        return success