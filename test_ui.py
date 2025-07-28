#!/usr/bin/env python3
"""
Simple UI test script to check if the interface is working properly.
"""

import sys
import os
from pathlib import Path

# Add scripts to path
project_root = Path(__file__).parent
scripts_path = project_root / "scripts"
sys.path.insert(0, str(scripts_path))

def test_ui():
    """Test the UI components."""
    from PyQt5.QtWidgets import QApplication
    
    # Create Qt application
    app = QApplication(sys.argv)
    
    try:
        # Test importing components
        print("Testing imports...")
        from ui.components.main_window import MainWindow
        from ui.components.right_panel import RightPanel
        from ui.components.left_panel import LeftPanel
        from ui.utils.status_manager import StatusManager
        from ui.styles.app_styles import get_app_styles
        print("All imports successful")
        
        # Test styles
        print("Testing styles...")
        styles = get_app_styles()
        print(f"Styles loaded - Dark mode: {styles.is_dark_mode}")
        
        # Test status manager
        print("Testing status manager...")
        status_manager = StatusManager()
        message_id = status_manager.add_status_message("Test message")
        print(f"Status manager working - Message ID: {message_id}")
        
        # Test right panel
        print("Testing right panel...")
        right_panel = RightPanel()
        right_panel.initialize()
        print("Right panel initialized")
        
        # Test main window
        print("Testing main window...")
        main_window = MainWindow()
        main_window.initialize()
        print("Main window initialized")
        
        # Show the window briefly to test rendering
        print("Showing window for 3 seconds...")
        main_window.show()
        
        # Process events for a moment
        app.processEvents()
        
        # Check if buttons are visible
        if main_window.right_panel and main_window.right_panel.process_button:
            button = main_window.right_panel.process_button
            print(f"Process button found - Text: '{button.text()}', Visible: {button.isVisible()}")
            print(f"   Size: {button.size().width()}x{button.size().height()}")
            print(f"   Position: ({button.x()}, {button.y()})")
        else:
            print("ERROR: Process button not found")
            
        if main_window.right_panel and main_window.right_panel.stop_button:
            button = main_window.right_panel.stop_button
            print(f"Stop button found - Text: '{button.text()}', Visible: {button.isVisible()}")
            print(f"   Size: {button.size().width()}x{button.size().height()}")
            print(f"   Position: ({button.x()}, {button.y()})")
        else:
            print("ERROR: Stop button not found")
        
        # Test status message
        if main_window.right_panel:
            main_window.right_panel.add_status_message("Test UI message", source="TestScript")
            print("Status message added")
        
        # Keep window open for a moment
        import time
        time.sleep(3)
        
        # Cleanup
        main_window.cleanup()
        print("Cleanup completed")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        app.quit()

if __name__ == '__main__':
    print("🧪 PDF Power Converter UI Test")
    print("=" * 40)
    
    success = test_ui()
    
    if success:
        print("\nAll tests passed!")
        sys.exit(0)
    else:
        print("\nSome tests failed!")
        sys.exit(1)