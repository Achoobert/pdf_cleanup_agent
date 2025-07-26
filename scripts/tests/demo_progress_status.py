#!/usr/bin/env python3
"""
Demo script for Progress and Status Management

This script demonstrates the enhanced progress indicators and status management
system implemented for task 11.
"""

import sys
import os
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtCore import QTimer, pyqtSignal

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from scripts.ui.utils.status_manager import StatusManager, StatusLevel, ProgressType
from scripts.ui.components.progress_widgets import ProgressPanel
from scripts.ui.components.right_panel import RightPanel


class ProgressDemo(QMainWindow):
    """Demo window for progress and status management."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Progress and Status Management Demo")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create right panel with status management
        self.right_panel = RightPanel()
        self.right_panel.initialize()
        layout.addWidget(self.right_panel)
        
        # Add demo buttons
        self.setup_demo_buttons(layout)
        
        # Demo timers
        self.demo_timer = QTimer()
        self.demo_timer.timeout.connect(self.update_demo_progress)
        self.demo_progress_id = None
        self.demo_progress_value = 0
        
    def setup_demo_buttons(self, layout):
        """Setup demo buttons."""
        # Status message demos
        info_btn = QPushButton("Add Info Message")
        info_btn.clicked.connect(lambda: self.add_demo_status("Info message", "info"))
        layout.addWidget(info_btn)
        
        success_btn = QPushButton("Add Success Message")
        success_btn.clicked.connect(lambda: self.add_demo_status("Success message", "success"))
        layout.addWidget(success_btn)
        
        warning_btn = QPushButton("Add Warning Message")
        warning_btn.clicked.connect(lambda: self.add_demo_status("Warning message", "warning"))
        layout.addWidget(warning_btn)
        
        error_btn = QPushButton("Add Error Message")
        error_btn.clicked.connect(lambda: self.add_demo_status("Error message", "error"))
        layout.addWidget(error_btn)
        
        # Progress demos
        progress_btn = QPushButton("Start Progress Demo")
        progress_btn.clicked.connect(self.start_progress_demo)
        layout.addWidget(progress_btn)
        
        busy_btn = QPushButton("Start Busy Demo")
        busy_btn.clicked.connect(self.start_busy_demo)
        layout.addWidget(busy_btn)
        
        # Clear button
        clear_btn = QPushButton("Clear All Messages")
        clear_btn.clicked.connect(self.clear_all_messages)
        layout.addWidget(clear_btn)
        
    def add_demo_status(self, message: str, level: str):
        """Add a demo status message."""
        self.right_panel.add_status_message(
            message, 
            getattr(StatusLevel, level.upper()),
            "Demo",
            persistent=False
        )
        
    def start_progress_demo(self):
        """Start a progress demonstration."""
        if self.demo_progress_id:
            return  # Already running
            
        self.demo_progress_id = self.right_panel.start_progress_indicator(
            "Demo Progress Operation",
            ProgressType.DETERMINATE,
            100,
            "Starting demo..."
        )
        
        self.demo_progress_value = 0
        self.demo_timer.start(200)  # Update every 200ms
        
    def update_demo_progress(self):
        """Update demo progress."""
        if not self.demo_progress_id:
            return
            
        self.demo_progress_value += 5
        
        if self.demo_progress_value <= 100:
            message = f"Processing step {self.demo_progress_value // 10 + 1}..."
            self.right_panel.update_progress_indicator(
                self.demo_progress_id,
                current=self.demo_progress_value,
                message=message
            )
        else:
            # Finish progress
            self.right_panel.finish_progress_indicator(
                self.demo_progress_id,
                "Demo completed successfully!"
            )
            self.demo_timer.stop()
            self.demo_progress_id = None
            
            # Add completion message
            self.add_demo_status("Progress demo completed", "success")
            
    def start_busy_demo(self):
        """Start a busy indicator demonstration."""
        busy_id = self.right_panel.start_busy_indicator(
            "Demo Busy Operation",
            "Processing in background..."
        )
        
        # Auto-finish after 3 seconds
        QTimer.singleShot(3000, lambda: self.finish_busy_demo(busy_id))
        
    def finish_busy_demo(self, busy_id: str):
        """Finish busy demo."""
        self.right_panel.finish_busy_indicator(busy_id)
        self.add_demo_status("Busy demo completed", "success")
        
    def clear_all_messages(self):
        """Clear all status messages."""
        self.right_panel.clear_all_status_messages()
        
    def closeEvent(self, event):
        """Handle window close."""
        self.demo_timer.stop()
        self.right_panel.cleanup()
        event.accept()


def main():
    """Run the progress demo."""
    app = QApplication(sys.argv)
    
    # Create and show demo window
    demo = ProgressDemo()
    demo.show()
    
    print("Progress and Status Management Demo")
    print("===================================")
    print("Features demonstrated:")
    print("- Status messages with different severity levels")
    print("- Auto-dismissing messages with configurable timeouts")
    print("- Determinate progress indicators with real-time updates")
    print("- Indeterminate busy indicators for long-running operations")
    print("- Visual feedback with appropriate styling")
    print("- Centralized status management system")
    print("\nClick the buttons to test different features!")
    
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())