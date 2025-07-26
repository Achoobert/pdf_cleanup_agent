"""
Progress Widgets

Enhanced progress indicator widgets for the PDF Cleanup Agent.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QProgressBar, QPushButton, QFrame, QScrollArea,
                             QSizePolicy, QGroupBox)
from PyQt5.QtCore import pyqtSignal, QTimer, Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont
from typing import Dict, Optional, List
import math

from .base_component import BaseComponent
from ..utils.status_manager import ProgressInfo, ProgressType, BusyIndicator, StatusMessage, StatusLevel
from ..styles.app_styles import get_app_styles


class AnimatedProgressBar(QProgressBar):
    """
    Enhanced progress bar with smooth animations and visual effects.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTextVisible(True)
        self._apply_theme()
        
        # Animation for smooth progress updates
        self.animation = QPropertyAnimation(self, b"value")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
    
    def _apply_theme(self):
        """Apply theme-aware styling."""
        styles = get_app_styles()
        self.setStyleSheet(styles.PROGRESS_BAR)
        
        # Also set minimum height programmatically
        self.setMinimumHeight(25)
        
    def setValueAnimated(self, value: int):
        """Set progress value with smooth animation."""
        self.animation.setStartValue(self.value())
        self.animation.setEndValue(value)
        self.animation.start()


class PulsingProgressBar(QWidget):
    """
    Pulsing progress bar for indeterminate progress.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(20)
        self.pulse_value = 0
        self.pulse_direction = 1
        
        # Timer for pulsing animation
        self.pulse_timer = QTimer()
        self.pulse_timer.timeout.connect(self._update_pulse)
        self.pulse_timer.start(50)  # 20 FPS
        
    def _update_pulse(self):
        """Update pulse animation."""
        self.pulse_value += self.pulse_direction * 5
        if self.pulse_value >= 100:
            self.pulse_direction = -1
        elif self.pulse_value <= 0:
            self.pulse_direction = 1
        self.update()
        
    def paintEvent(self, event):
        """Custom paint event for pulsing effect."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        styles = get_app_styles()
        
        # Background
        painter.setBrush(QBrush(QColor(styles.COLORS['background_alt'])))
        painter.setPen(QPen(QColor(styles.COLORS['border']), 2))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 8, 8)
        
        # Pulsing bar
        alpha = int(255 * (self.pulse_value / 100.0))
        color = QColor(styles.COLORS['primary'])
        color.setAlpha(alpha)
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.NoPen)
        
        bar_rect = self.rect().adjusted(3, 3, -3, -3)
        painter.drawRoundedRect(bar_rect, 6, 6)
        
    def cleanup(self):
        """Stop the pulse timer."""
        self.pulse_timer.stop()


class BusySpinner(QWidget):
    """
    Spinning busy indicator widget.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(24, 24)
        self.angle = 0
        
        # Timer for spinning animation
        self.spin_timer = QTimer()
        self.spin_timer.timeout.connect(self._update_spin)
        self.spin_timer.start(100)  # 10 FPS
        
    def _update_spin(self):
        """Update spinning animation."""
        self.angle = (self.angle + 30) % 360
        self.update()
        
    def paintEvent(self, event):
        """Custom paint event for spinning effect."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        styles = get_app_styles()
        
        # Move to center
        painter.translate(self.width() / 2, self.height() / 2)
        painter.rotate(self.angle)
        
        # Draw spinning arcs
        pen = QPen(QColor(styles.COLORS['primary']), 3, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(pen)
        
        for i in range(8):
            alpha = int(255 * (i / 8.0))
            color = QColor(styles.COLORS['primary'])
            color.setAlpha(alpha)
            pen.setColor(color)
            painter.setPen(pen)
            
            painter.drawLine(0, -8, 0, -12)
            painter.rotate(45)
            
    def cleanup(self):
        """Stop the spin timer."""
        self.spin_timer.stop()


class ProgressWidget(BaseComponent):
    """
    Individual progress widget showing progress information.
    """
    
    # Signals
    cancel_requested = pyqtSignal(str)  # progress_id
    
    def __init__(self, progress_info: ProgressInfo, parent=None):
        super().__init__(parent)
        self.progress_info = progress_info
        self.progress_bar = None
        self.pulse_bar = None
        self.title_label = None
        self.message_label = None
        self.cancel_button = None
        
    def _setup_ui(self):
        """Setup the progress widget UI."""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Header with title and cancel button
        header_layout = QHBoxLayout()
        
        self.title_label = QLabel(self.progress_info.title)
        self.title_label.setFont(QFont("Arial", 10, QFont.Bold))
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        self.cancel_button = QPushButton("✕")
        self.cancel_button.setFixedSize(20, 20)
        styles = get_app_styles()
        self.cancel_button.setStyleSheet(styles.BUTTON_SMALL_CANCEL)
        self.cancel_button.clicked.connect(self._on_cancel_clicked)
        header_layout.addWidget(self.cancel_button)
        
        layout.addLayout(header_layout)
        
        # Progress indicator
        if self.progress_info.progress_type == ProgressType.DETERMINATE:
            self.progress_bar = AnimatedProgressBar()
            self.progress_bar.setMaximum(self.progress_info.maximum)
            self.progress_bar.setValueAnimated(self.progress_info.current)
            layout.addWidget(self.progress_bar)
        else:
            self.pulse_bar = PulsingProgressBar()
            layout.addWidget(self.pulse_bar)
        
        # Message label
        self.message_label = QLabel(self.progress_info.message)
        self.message_label.setFont(QFont("Arial", 9))
        self.message_label.setStyleSheet(styles.MESSAGE_LABEL)
        self.message_label.setWordWrap(True)
        layout.addWidget(self.message_label)
        
        # Style the widget
        self._apply_widget_theme()
        
    def _setup_connections(self):
        """Setup signal connections."""
        pass  # Connections handled in _setup_ui
        
    def _apply_widget_theme(self):
        """Apply theme-aware styling to the widget."""
        styles = get_app_styles()
        self.setStyleSheet(f"""
            ProgressWidget {{
                background-color: {styles.COLORS['surface']};
                border: 1px solid {styles.COLORS['border']};
                border-radius: 8px;
                padding: 8px;
                margin: 2px;
            }}
            QLabel {{
                color: {styles.COLORS['text']};
                background-color: transparent;
            }}
        """)
        
        # Update cancel button style
        if self.cancel_button:
            self.cancel_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {styles.COLORS['error']};
                    color: white;
                    border: none;
                    border-radius: 10px;
                    font-size: 12px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {styles.COLORS['error_hover']};
                }}
            """)
    
    def _on_cancel_clicked(self):
        """Handle cancel button click."""
        self.cancel_requested.emit(self.progress_info.id)
        
    def update_progress(self, progress_info: ProgressInfo):
        """Update the progress widget with new information."""
        self.progress_info = progress_info
        
        if self.title_label:
            self.title_label.setText(progress_info.title)
            
        if self.message_label:
            self.message_label.setText(progress_info.message)
            
        if self.progress_bar and progress_info.progress_type == ProgressType.DETERMINATE:
            self.progress_bar.setMaximum(progress_info.maximum)
            self.progress_bar.setValueAnimated(progress_info.current)
            
    def cleanup(self):
        """Cleanup widget resources."""
        if self.pulse_bar:
            self.pulse_bar.cleanup()
        super().cleanup()


class BusyWidget(BaseComponent):
    """
    Widget for displaying busy indicators.
    """
    
    def __init__(self, busy_info: BusyIndicator, parent=None):
        super().__init__(parent)
        self.busy_info = busy_info
        self.spinner = None
        self.operation_label = None
        self.message_label = None
        
    def _setup_ui(self):
        """Setup the busy widget UI."""
        layout = QHBoxLayout()
        self.setLayout(layout)
        
        # Spinner
        self.spinner = BusySpinner()
        layout.addWidget(self.spinner)
        
        # Text layout
        text_layout = QVBoxLayout()
        
        self.operation_label = QLabel(self.busy_info.operation)
        self.operation_label.setFont(QFont("Arial", 10, QFont.Bold))
        text_layout.addWidget(self.operation_label)
        
        if self.busy_info.message:
            self.message_label = QLabel(self.busy_info.message)
            self.message_label.setFont(QFont("Arial", 9))
            styles = get_app_styles()
            self.message_label.setStyleSheet(styles.MESSAGE_LABEL)
            text_layout.addWidget(self.message_label)
            
        layout.addLayout(text_layout)
        layout.addStretch()
        
        # Style the widget
        self._apply_widget_theme()
        
    def _apply_widget_theme(self):
        """Apply theme-aware styling to the widget."""
        styles = get_app_styles()
        warning_bg = styles.COLORS['warning'] if styles.is_dark_mode else '#fff3cd'
        warning_border = styles.COLORS['warning_hover'] if styles.is_dark_mode else '#ffeaa7'
        
        self.setStyleSheet(styles.get_busy_widget_style())
        
    def _setup_connections(self):
        """Setup signal connections."""
        pass
        
    def update_busy(self, busy_info: BusyIndicator):
        """Update the busy widget with new information."""
        self.busy_info = busy_info
        
        if self.operation_label:
            self.operation_label.setText(busy_info.operation)
            
        if self.message_label:
            if busy_info.message:
                self.message_label.setText(busy_info.message)
                self.message_label.show()
            else:
                self.message_label.hide()
                
    def cleanup(self):
        """Cleanup widget resources."""
        if self.spinner:
            self.spinner.cleanup()
        super().cleanup()


class StatusMessageWidget(BaseComponent):
    """
    Widget for displaying status messages with appropriate styling.
    """
    
    # Signals
    message_dismissed = pyqtSignal(str)  # message_id
    
    def __init__(self, status_message: StatusMessage, parent=None):
        super().__init__(parent)
        self.status_message = status_message
        self.message_label = None
        self.dismiss_button = None
        
    def _setup_ui(self):
        """Setup the status message widget UI."""
        layout = QHBoxLayout()
        self.setLayout(layout)
        
        # Message label
        self.message_label = QLabel(self.status_message.message)
        self.message_label.setWordWrap(True)
        self.message_label.setFont(QFont("Arial", 9))
        layout.addWidget(self.message_label)
        
        layout.addStretch()
        
        # Dismiss button (only for non-persistent messages)
        if not self.status_message.persistent:
            self.dismiss_button = QPushButton("✕")
            self.dismiss_button.setFixedSize(16, 16)
            styles = get_app_styles()
            self.dismiss_button.setStyleSheet(styles.BUTTON_SMALL_DISMISS)
            self.dismiss_button.clicked.connect(self._on_dismiss_clicked)
            layout.addWidget(self.dismiss_button)
        
        # Apply styling based on message level
        self._apply_level_styling()
        
    def _setup_connections(self):
        """Setup signal connections."""
        pass  # Connections handled in _setup_ui
        
    def _apply_level_styling(self):
        """Apply styling based on message level."""
        styles = get_app_styles()
        

        
        styles = get_app_styles()
        level_name = self.status_message.level.name.lower()
        self.setStyleSheet(styles.get_status_message_widget_style(level_name))
        
    def _on_dismiss_clicked(self):
        """Handle dismiss button click."""
        self.message_dismissed.emit(self.status_message.id)


class ProgressPanel(BaseComponent):
    """
    Panel for displaying all progress indicators and status messages.
    """
    
    # Signals
    progress_cancelled = pyqtSignal(str)  # progress_id
    status_message_dismissed = pyqtSignal(str)  # message_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.progress_widgets: Dict[str, ProgressWidget] = {}
        self.busy_widgets: Dict[str, BusyWidget] = {}
        self.status_widgets: Dict[str, StatusMessageWidget] = {}
        
        self.progress_scroll_area = None
        self.status_scroll_area = None
        self.progress_container = None
        self.status_container = None
        
    def _setup_ui(self):
        """Setup the progress panel UI."""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Progress indicators section
        progress_group = QGroupBox("Active Operations")
        progress_group.setFont(QFont("Arial", 10, QFont.Bold))
        progress_layout = QVBoxLayout()
        progress_group.setLayout(progress_layout)
        
        # Scroll area for progress widgets
        self.progress_scroll_area = QScrollArea()
        self.progress_scroll_area.setWidgetResizable(True)
        self.progress_scroll_area.setMaximumHeight(200)
        self.progress_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.progress_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.progress_container = QWidget()
        self.progress_container.setLayout(QVBoxLayout())
        self.progress_scroll_area.setWidget(self.progress_container)
        
        progress_layout.addWidget(self.progress_scroll_area)
        layout.addWidget(progress_group)
        
        # Status messages section
        status_group = QGroupBox("Status Messages")
        status_group.setFont(QFont("Arial", 10, QFont.Bold))
        status_layout = QVBoxLayout()
        status_group.setLayout(status_layout)
        
        # Scroll area for status messages
        self.status_scroll_area = QScrollArea()
        self.status_scroll_area.setWidgetResizable(True)
        self.status_scroll_area.setMaximumHeight(150)
        self.status_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.status_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.status_container = QWidget()
        self.status_container.setLayout(QVBoxLayout())
        self.status_scroll_area.setWidget(self.status_container)
        
        status_layout.addWidget(self.status_scroll_area)
        layout.addWidget(status_group)
        
        # Initially hide if no content
        self._update_visibility()
        
    def _setup_connections(self):
        """Setup signal connections."""
        pass
        
    def add_progress_widget(self, progress_info: ProgressInfo):
        """Add a progress widget."""
        if progress_info.id in self.progress_widgets:
            return
            
        widget = ProgressWidget(progress_info)
        widget.initialize()
        widget.cancel_requested.connect(self.progress_cancelled.emit)
        
        self.progress_widgets[progress_info.id] = widget
        if self.progress_container and self.progress_container.layout():
            self.progress_container.layout().addWidget(widget)
        self._update_visibility()
        
    def add_busy_widget(self, busy_info: BusyIndicator):
        """Add a busy widget."""
        if busy_info.id in self.busy_widgets:
            return
            
        widget = BusyWidget(busy_info)
        widget.initialize()
        
        self.busy_widgets[busy_info.id] = widget
        if self.progress_container and self.progress_container.layout():
            self.progress_container.layout().addWidget(widget)
        self._update_visibility()
        
    def add_status_widget(self, status_message: StatusMessage):
        """Add a status message widget."""
        if status_message.id in self.status_widgets:
            return
            
        widget = StatusMessageWidget(status_message)
        widget.initialize()
        widget.message_dismissed.connect(self.status_message_dismissed.emit)
        
        self.status_widgets[status_message.id] = widget
        if self.status_container and self.status_container.layout():
            self.status_container.layout().addWidget(widget)
        self._update_visibility()
        
    def update_progress_widget(self, progress_info: ProgressInfo):
        """Update a progress widget."""
        if progress_info.id in self.progress_widgets:
            self.progress_widgets[progress_info.id].update_progress(progress_info)
            
    def update_busy_widget(self, busy_info: BusyIndicator):
        """Update a busy widget."""
        if busy_info.id in self.busy_widgets:
            self.busy_widgets[busy_info.id].update_busy(busy_info)
            
    def remove_progress_widget(self, progress_id: str):
        """Remove a progress widget."""
        if progress_id in self.progress_widgets:
            widget = self.progress_widgets[progress_id]
            widget.cleanup()
            widget.setParent(None)
            del self.progress_widgets[progress_id]
            self._update_visibility()
            
    def remove_busy_widget(self, busy_id: str):
        """Remove a busy widget."""
        if busy_id in self.busy_widgets:
            widget = self.busy_widgets[busy_id]
            widget.cleanup()
            widget.setParent(None)
            del self.busy_widgets[busy_id]
            self._update_visibility()
            
    def remove_status_widget(self, message_id: str):
        """Remove a status message widget."""
        if message_id in self.status_widgets:
            widget = self.status_widgets[message_id]
            widget.cleanup()
            widget.setParent(None)
            del self.status_widgets[message_id]
            self._update_visibility()
            
    def clear_all_widgets(self):
        """Clear all widgets."""
        # Clear progress widgets
        for widget in self.progress_widgets.values():
            widget.cleanup()
            widget.setParent(None)
        self.progress_widgets.clear()
        
        # Clear busy widgets
        for widget in self.busy_widgets.values():
            widget.cleanup()
            widget.setParent(None)
        self.busy_widgets.clear()
        
        # Clear status widgets
        for widget in self.status_widgets.values():
            widget.cleanup()
            widget.setParent(None)
        self.status_widgets.clear()
        
        self._update_visibility()
        
    def _update_visibility(self):
        """Update panel visibility based on content."""
        has_progress = len(self.progress_widgets) > 0 or len(self.busy_widgets) > 0
        has_status = len(self.status_widgets) > 0
        
        self.setVisible(has_progress or has_status)
        
    def cleanup(self):
        """Cleanup panel resources."""
        self.clear_all_widgets()
        super().cleanup()