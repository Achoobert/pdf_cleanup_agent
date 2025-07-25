#!/usr/bin/env python3
"""
Configuration Management Example

Demonstrates how to use the AppConfig and AppSettings classes
for configuration management in the PDF Cleanup Agent.
"""

import sys
import os

# Add the scripts directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ui.utils.config import AppConfig, AppSettings


def main():
    """Demonstrate configuration management usage."""
    print("PDF Cleanup Agent - Configuration Management Example")
    print("=" * 55)
    
    # Initialize configuration manager
    config = AppConfig()
    
    # Connect to signals for demonstration
    config.config_loaded.connect(lambda: print("✓ Configuration loaded successfully"))
    config.config_saved.connect(lambda: print("✓ Configuration saved successfully"))
    config.config_error.connect(lambda msg: print(f"✗ Configuration error: {msg}"))
    
    # Initialize (loads existing config or creates default)
    print("\n1. Initializing configuration...")
    success = config.initialize()
    print(f"   Initialization {'succeeded' if success else 'failed'}")
    
    # Display current settings
    print("\n2. Current configuration:")
    if config.settings:
        print(f"   Model Backend: {config.settings.model_backend}")
        print(f"   Model Name: {config.settings.model_name}")
        print(f"   Chunk Size: {config.settings.chunk_size}")
        print(f"   API Endpoint: {config.settings.api_endpoint}")
        print(f"   Data Directories: {len(config.settings.data_directories)} configured")
        
    # Demonstrate getting specific settings
    print("\n3. Getting specific settings:")
    theme = config.get_setting('ui_preferences.theme', 'unknown')
    window_width = config.get_setting('ui_preferences.window_width', 800)
    print(f"   UI Theme: {theme}")
    print(f"   Window Width: {window_width}")
    
    # Demonstrate setting values
    print("\n4. Modifying settings:")
    config.set_setting('ui_preferences.theme', 'dark')
    config.set_setting('ui_preferences.window_width', 1200)
    print("   Updated theme to 'dark' and window width to 1200")
    
    # Demonstrate directory management
    print("\n5. Directory management:")
    try:
        pdf_dir = config.get_data_directory('pdf_source')
        print(f"   PDF Source Directory: {pdf_dir}")
        
        # Ensure directories exist
        if config.ensure_directories_exist():
            print("   ✓ All directories ensured to exist")
        else:
            print("   ✗ Failed to create some directories")
            
    except ValueError as e:
        print(f"   ✗ Directory error: {e}")
    
    # Demonstrate validation
    print("\n6. Configuration validation:")
    if config.validate_current_config():
        print("   ✓ Configuration is valid")
    else:
        print("   ✗ Configuration validation failed")
    
    # Save configuration
    print("\n7. Saving configuration:")
    if config.save_config():
        print("   ✓ Configuration saved to file")
    else:
        print("   ✗ Failed to save configuration")
    
    # Demonstrate creating custom settings
    print("\n8. Creating custom settings:")
    custom_settings = AppSettings(
        model_backend="openai",
        model_name="gpt-4",
        chunk_size=2000,
        api_endpoint="https://api.openai.com/v1"
    )
    print(f"   Custom settings created with {custom_settings.model_backend} backend")
    
    # Convert to/from dictionary
    print("\n9. Dictionary conversion:")
    settings_dict = custom_settings.to_dict()
    print(f"   Settings converted to dict with {len(settings_dict)} keys")
    
    restored_settings = AppSettings.from_dict(settings_dict)
    print(f"   Settings restored from dict: {restored_settings.model_backend}")
    
    print("\n" + "=" * 55)
    print("Configuration management example completed!")


if __name__ == '__main__':
    main()