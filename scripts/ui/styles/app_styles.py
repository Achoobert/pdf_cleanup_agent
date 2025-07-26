"""
Application Styles

Centralized styling and theming for the application with dark mode support.
All UI styling is consolidated here for easy maintenance and consistency.
"""

from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QApplication
import sys


class ThemeManager:
    """
    Manages application themes and dark mode detection.
    """
    
    @staticmethod
    def is_dark_mode() -> bool:
        """
        Detect if the system is in dark mode.
        
        Returns:
            True if dark mode is detected, False otherwise
        """
        try:
            # Try to detect system dark mode
            if sys.platform == "darwin":  # macOS
                import subprocess
                result = subprocess.run(
                    ["defaults", "read", "-g", "AppleInterfaceStyle"],
                    capture_output=True,
                    text=True
                )
                return result.returncode == 0 and "Dark" in result.stdout
            elif sys.platform == "win32":  # Windows
                try:
                    import winreg
                    registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
                    key = winreg.OpenKey(registry, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize")
                    value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                    return value == 0
                except:
                    pass
            else:  # Linux
                # Check for common dark theme indicators
                import os
                gtk_theme = os.environ.get('GTK_THEME', '').lower()
                if 'dark' in gtk_theme:
                    return True
                
                # Check Qt application palette
                app = QApplication.instance()
                if app:
                    palette = app.palette()
                    window_color = palette.color(palette.Window)
                    # If window background is darker than middle gray, assume dark mode
                    return window_color.lightness() < 128
                    
        except Exception:
            pass
        
        # Fallback: check Qt application palette
        app = QApplication.instance()
        if app:
            palette = app.palette()
            window_color = palette.color(palette.Window)
            return window_color.lightness() < 128
            
        return False
    
    @staticmethod
    def get_system_colors():
        """
        Get system colors based on current theme.
        
        Returns:
            Dictionary of color values
        """
        app = QApplication.instance()
        if app:
            palette = app.palette()
            return {
                'window': palette.color(palette.Window).name(),
                'window_text': palette.color(palette.WindowText).name(),
                'base': palette.color(palette.Base).name(),
                'text': palette.color(palette.Text).name(),
                'button': palette.color(palette.Button).name(),
                'button_text': palette.color(palette.ButtonText).name(),
                'highlight': palette.color(palette.Highlight).name(),
                'highlight_text': palette.color(palette.HighlightedText).name(),
                'disabled_text': palette.color(palette.Disabled, palette.Text).name(),
            }
        return {}


class AppStyles:
    """
    Centralized styling definitions for the application.
    
    This class provides consistent styling across all UI components.
    All styles are organized by component type for easy maintenance.
    """
    
    def __init__(self):
        """Initialize AppStyles with theme detection."""
        self.is_dark_mode = ThemeManager.is_dark_mode()
        self.system_colors = ThemeManager.get_system_colors()
        self._setup_colors()
        self._setup_status_colors()
    
    def _setup_colors(self):
        """Setup color palette based on current theme."""
        if self.is_dark_mode:
            self.COLORS = {
                'primary': '#0078d4',
                'primary_hover': '#106ebe',
                'primary_pressed': '#005a9e',
                'secondary': '#6c757d',
                'secondary_hover': '#5a6268',
                'success': '#28a745',
                'success_hover': '#218838',
                'warning': '#ffc107',
                'warning_hover': '#e0a800',
                'error': '#dc3545',
                'error_hover': '#c82333',
                'info': '#17a2b8',
                'light': '#495057',
                'dark': '#212529',
                'background': self.system_colors.get('window', '#2b2b2b'),
                'background_alt': '#3c3c3c',
                'surface': self.system_colors.get('base', '#323232'),
                'border': '#555555',
                'border_light': '#666666',
                'text': self.system_colors.get('window_text', '#ffffff'),
                'text_secondary': '#cccccc',
                'text_muted': '#999999',
                'text_disabled': '#666666',
                'selection': self.system_colors.get('highlight', '#0078d4'),
                'selection_text': self.system_colors.get('highlight_text', '#ffffff'),
                # Console colors
                'console_bg': '#1e1e1e',
                'console_text': '#ffffff',
                'console_border': '#cccccc',
            }
        else:
            self.COLORS = {
                'primary': '#0078d4',
                'primary_hover': '#106ebe',
                'primary_pressed': '#005a9e',
                'secondary': '#6c757d',
                'secondary_hover': '#5a6268',
                'success': '#28a745',
                'success_hover': '#218838',
                'warning': '#ffc107',
                'warning_hover': '#e0a800',
                'error': '#dc3545',
                'error_hover': '#c82333',
                'info': '#17a2b8',
                'light': '#f8f9fa',
                'dark': '#343a40',
                'background': self.system_colors.get('window', '#ffffff'),
                'background_alt': '#f8f9fa',
                'surface': self.system_colors.get('base', '#ffffff'),
                'border': '#dee2e6',
                'border_light': '#e9ecef',
                'text': self.system_colors.get('window_text', '#212529'),
                'text_secondary': '#495057',
                'text_muted': '#6c757d',
                'text_disabled': '#6c757d',
                'selection': self.system_colors.get('highlight', '#0078d4'),
                'selection_text': self.system_colors.get('highlight_text', '#ffffff'),
                # Console colors
                'console_bg': '#ffffff',
                'console_text': '#000000',
                'console_border': '#cccccc',
            }
    
    def _setup_status_colors(self):
        """Setup status-specific color schemes."""
        if self.is_dark_mode:
            self.STATUS_COLORS = {
                'success': {
                    'background': '#1a4d2e',
                    'text': '#90ee90',
                    'border': '#2d6a4a'
                },
                'warning': {
                    'background': '#5c4d1a',
                    'text': '#ffd700',
                    'border': '#7a6a2d'
                },
                'error': {
                    'background': '#5c1a1a',
                    'text': '#ff6b6b',
                    'border': '#7a2d2d'
                },
                'info': {
                    'background': '#1a4d5c',
                    'text': '#87ceeb',
                    'border': '#2d6a7a'
                },
                'debug': {
                    'background': '#3c3c3c',
                    'text': '#cccccc',
                    'border': '#555555'
                }
            }
        else:
            self.STATUS_COLORS = {
                'success': {
                    'background': '#d4edda',
                    'text': '#155724',
                    'border': '#c3e6cb'
                },
                'warning': {
                    'background': '#fff3cd',
                    'text': '#856404',
                    'border': '#ffeaa7'
                },
                'error': {
                    'background': '#f8d7da',
                    'text': '#721c24',
                    'border': '#f5c6cb'
                },
                'info': {
                    'background': '#d1ecf1',
                    'text': '#0c5460',
                    'border': '#bee5eb'
                },
                'debug': {
                    'background': '#e2e3e5',
                    'text': '#383d41',
                    'border': '#d6d8db'
                }
            }
    
    # =============================================================================
    # DROP ZONE STYLES
    # =============================================================================
    
    @property
    def DROP_ZONE_NORMAL(self):
        """Get normal drop zone style."""
        return f"""
            QListWidget {{
                border: 2px dashed {self.COLORS['border']};
                border-radius: 5px;
                background-color: {self.COLORS['background_alt']};
                color: {self.COLORS['text']};
                padding: 10px;
            }}
            QListWidget:hover {{
                border-color: {self.COLORS['border_light']};
            }}
        """
    
    @property
    def DROP_ZONE_ACTIVE(self):
        """Get active drop zone style."""
        return f"""
            QListWidget {{
                border: 3px solid {self.COLORS['primary']};
                border-radius: 5px;
                background-color: rgba(0, 120, 212, 0.1);
                color: {self.COLORS['text']};
                padding: 10px;
            }}
        """
    
    # =============================================================================
    # BUTTON STYLES
    # =============================================================================
    
    @property
    def BUTTON_PRIMARY(self):
        """Get primary button style."""
        return f"""
            QPushButton {{
                background-color: {self.COLORS['primary']};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-height: 12px;
            }}
            QPushButton:hover {{
                background-color: {self.COLORS['primary_hover']};
            }}
            QPushButton:pressed {{
                background-color: {self.COLORS['primary_pressed']};
            }}
            QPushButton:disabled {{
                background-color: {self.COLORS['text_disabled']};
                color: {self.COLORS['text_muted']};
            }}
        """
    
    @property
    def BUTTON_SECONDARY(self):
        """Get secondary button style."""
        return f"""
            QPushButton {{
                background-color: {self.COLORS['secondary']};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                min-height: 12px;
            }}
            QPushButton:hover {{
                background-color: {self.COLORS['secondary_hover']};
            }}
            QPushButton:pressed {{
                background-color: #545b62;
            }}
            QPushButton:disabled {{
                background-color: {self.COLORS['text_disabled']};
                color: {self.COLORS['text_muted']};
            }}
        """
    
    @property
    def BUTTON_SUCCESS(self):
        """Get success button style."""
        return f"""
            QPushButton {{
                background-color: {self.COLORS['success']};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                min-height: 12px;
            }}
            QPushButton:hover {{
                background-color: {self.COLORS['success_hover']};
            }}
            QPushButton:pressed {{
                background-color: #1e7e34;
            }}
        """
    
    @property
    def BUTTON_WARNING(self):
        """Get warning button style."""
        warning_text_color = '#212529' if not self.is_dark_mode else '#000000'
        return f"""
            QPushButton {{
                background-color: {self.COLORS['warning']};
                color: {warning_text_color};
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                min-height: 12px;
            }}
            QPushButton:hover {{
                background-color: {self.COLORS['warning_hover']};
            }}
            QPushButton:pressed {{
                background-color: #d39e00;
            }}
        """
    
    @property
    def BUTTON_ERROR(self):
        """Get error button style."""
        return f"""
            QPushButton {{
                background-color: {self.COLORS['error']};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                min-height: 12px;
            }}
            QPushButton:hover {{
                background-color: {self.COLORS['error_hover']};
            }}
            QPushButton:pressed {{
                background-color: #bd2130;
            }}
        """
    
    @property
    def BUTTON_SMALL_CANCEL(self):
        """Get small cancel button style for progress widgets."""
        return f"""
            QPushButton {{
                background-color: {self.COLORS['error']};
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 10px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.COLORS['error_hover']};
            }}
        """
    
    @property
    def BUTTON_SMALL_DISMISS(self):
        """Get small dismiss button style for status widgets."""
        return f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                color: {self.COLORS['text_muted']};
                font-size: 10px;
            }}
            QPushButton:hover {{
                color: {self.COLORS['text']};
            }}
        """
    
    # =============================================================================
    # CONTAINER STYLES
    # =============================================================================
    
    @property
    def GROUP_BOX(self):
        """Get group box style."""
        return f"""
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {self.COLORS['border']};
                border-radius: 5px;
                margin-top: 15px;
                padding-top: 10px;
                background-color: {self.COLORS['background']};
                color: {self.COLORS['text']};
                font-size: 12px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {self.COLORS['text']};
                background-color: {self.COLORS['background']};
            }}
        """
    
    @property
    def PANEL_STYLE(self):
        """Get panel style for main panels."""
        return f"""
            QWidget {{
                background-color: {self.COLORS['background']};
                color: {self.COLORS['text']};
            }}
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {self.COLORS['border']};
                border-radius: 5px;
                margin-top: 15px;
                padding-top: 10px;
                background-color: {self.COLORS['background']};
                color: {self.COLORS['text']};
                font-size: 12px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {self.COLORS['text']};
                background-color: {self.COLORS['background']};
            }}
        """
    
    # =============================================================================
    # TEXT INPUT STYLES
    # =============================================================================
    
    @property
    def TEXT_EDIT(self):
        """Get text edit style."""
        return f"""
            QTextEdit {{
                border: 1px solid {self.COLORS['border']};
                border-radius: 4px;
                padding: 8px;
                background-color: {self.COLORS['surface']};
                color: {self.COLORS['text']};
                selection-background-color: {self.COLORS['selection']};
                selection-color: {self.COLORS['selection_text']};
                min-height: 100px;
            }}
            QTextEdit:focus {{
                border-color: {self.COLORS['primary']};
            }}
        """
    
    @property
    def CONSOLE_STYLE(self):
        """Get console text edit style."""
        return f"""
            QTextEdit {{
                background-color: {self.COLORS['console_bg']};
                color: {self.COLORS['console_text']};
                border: 1px solid {self.COLORS['console_border']};
                border-radius: 4px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 10px;
                padding: 8px;
            }}
        """
    
    # =============================================================================
    # LIST AND TABLE STYLES
    # =============================================================================
    
    @property
    def LIST_WIDGET(self):
        """Get list widget style."""
        return f"""
            QListWidget {{
                border: 1px solid {self.COLORS['border']};
                border-radius: 4px;
                background-color: {self.COLORS['surface']};
                color: {self.COLORS['text']};
                alternate-background-color: {self.COLORS['background_alt']};
            }}
            QListWidget::item {{
                padding: 5px;
                border-bottom: 1px solid {self.COLORS['border']};
                color: {self.COLORS['text']};
            }}
            QListWidget::item:selected {{
                background-color: {self.COLORS['selection']};
                color: {self.COLORS['selection_text']};
            }}
            QListWidget::item:hover {{
                background-color: {self.COLORS['background_alt']};
            }}
        """
    
    # =============================================================================
    # PROGRESS AND STATUS STYLES
    # =============================================================================
    
    @property
    def STATUS_BAR(self):
        """Get status bar style."""
        return f"""
            QStatusBar {{
                background-color: {self.COLORS['background_alt']};
                border-top: 1px solid {self.COLORS['border']};
                color: {self.COLORS['text']};
                min-height: 12px;
            }}
        """
    
    @property
    def PROGRESS_BAR(self):
        """Get progress bar style."""
        return f"""
            QProgressBar {{
                border: 2px solid {self.COLORS['border']};
                border-radius: 8px;
                text-align: center;
                background-color: {self.COLORS['background_alt']};
                color: {self.COLORS['text']};
                font-weight: bold;
                min-height: 15px;
                max-height: 20px;
            }}
            QProgressBar::chunk {{
                background-color: {self.COLORS['primary']};
                border-radius: 6px;
            }}
        """
    
    def get_status_label_style(self, status_type: str = "info") -> str:
        """Get status label style by type."""
        colors = self.STATUS_COLORS.get(status_type, self.STATUS_COLORS['info'])
        return f"""
            QLabel {{
                font-weight: bold;
                padding: 8px;
                min-height: 12px;
                background-color: {colors['background']};
                color: {colors['text']};
                border: 1px solid {colors['border']};
                border-radius: 3px;
                font-size: 12px;
            }}
        """
    
    def get_progress_widget_style(self) -> str:
        """Get progress widget container style."""
        return f"""
            QWidget {{
                background-color: {self.COLORS['surface']};
                border: 1px solid {self.COLORS['border']};
                border-radius: 4px;
                padding: 8px;
                margin: 2px;
            }}
        """
    
    def get_busy_widget_style(self) -> str:
        """Get busy widget container style."""
        warning_bg = self.COLORS['warning'] if self.is_dark_mode else '#fff3cd'
        warning_border = self.COLORS['warning_hover'] if self.is_dark_mode else '#ffeaa7'
        
        return f"""
            QWidget {{
                background-color: {warning_bg};
                border: 1px solid {warning_border};
                border-radius: 4px;
                padding: 8px;
                margin: 2px;
            }}
        """
    
    def get_status_message_widget_style(self, level: str) -> str:
        """Get status message widget style by level."""
        colors = self.STATUS_COLORS.get(level, self.STATUS_COLORS['info'])
        return f"""
            QWidget {{
                background-color: {colors['background']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
                padding: 8px;
                margin: 2px;
            }}
            QLabel {{
                color: {colors['text']};
                background-color: transparent;
            }}
        """
    
    # =============================================================================
    # LABEL STYLES
    # =============================================================================
    
    @property
    def HEADER_LABEL(self):
        """Get header label style."""
        return f"""
            QLabel {{
                font-weight: bold;
                font-size: 14px;
                color: {self.COLORS['text']};
                padding: 5px;
                background-color: {self.COLORS['background_alt']};
                border-bottom: 1px solid {self.COLORS['border']};
            }}
        """
    
    @property
    def SECTION_TITLE_LABEL(self):
        """Get section title label style."""
        return f"""
            QLabel {{
                color: {self.COLORS['text']};
                font-weight: bold;
                font-size: 11px;
                margin-top: 5px;
                background-color: transparent;
            }}
        """
    
    @property
    def INFO_LABEL(self):
        """Get info label style."""
        return f"""
            QLabel {{
                font-weight: bold;
                padding: 8px;
                min-height: 15px;
                background-color: {self.COLORS['background_alt']};
                border: 1px solid {self.COLORS['border']};
                border-radius: 3px;
                color: {self.COLORS['text']};
                font-size: 12px;
            }}
        """
    
    @property
    def MESSAGE_LABEL(self):
        """Get message label style for progress widgets."""
        return f"""
            QLabel {{
                color: {self.COLORS['text_muted']};
                background-color: transparent;
                font-size: 9px;
            }}
        """
    
    # =============================================================================
    # UTILITY METHODS
    # =============================================================================
    
    def get_button_style(self, button_type: str = 'primary') -> str:
        """
        Get button style by type.
        
        Args:
            button_type: Type of button ('primary', 'secondary', 'success', 'warning', 'error')
            
        Returns:
            CSS style string
        """
        styles = {
            'primary': self.BUTTON_PRIMARY,
            'secondary': self.BUTTON_SECONDARY,
            'success': self.BUTTON_SUCCESS,
            'warning': self.BUTTON_WARNING,
            'error': self.BUTTON_ERROR
        }
        return styles.get(button_type, self.BUTTON_PRIMARY)
        
    def apply_drop_zone_style(self, widget, active: bool = False):
        """
        Apply drop zone styling to a widget.
        
        Args:
            widget: Widget to style
            active: Whether to apply active (drag over) styling
        """
        if active:
            widget.setStyleSheet(self.DROP_ZONE_ACTIVE)
        else:
            widget.setStyleSheet(self.DROP_ZONE_NORMAL)
            
    # =============================================================================
    # MAIN WINDOW AND LAYOUT STYLES
    # =============================================================================
    
    def get_main_window_style(self) -> str:
        """
        Get the main window stylesheet.
        
        Returns:
            CSS style string for the main window
        """
        return f"""
            QMainWindow {{
                background-color: {self.COLORS['background']};
                color: {self.COLORS['text']};
            }}
            QWidget {{
                background-color: {self.COLORS['background']};
                color: {self.COLORS['text']};
            }}
            QLabel {{
                color: {self.COLORS['text']};
                background-color: transparent;
            }}
            QFrame {{
                background-color: {self.COLORS['background']};
                color: {self.COLORS['text']};
            }}
            QSplitter::handle {{
                background-color: {self.COLORS['border']};
            }}
            QSplitter::handle:horizontal {{
                width: 2px;
            }}
            QSplitter::handle:vertical {{
                height: 2px;
            }}
        """
    
    def get_scroll_area_style(self) -> str:
        """Get scroll area style."""
        return f"""
            QScrollArea {{
                border: 1px solid {self.COLORS['border']};
                border-radius: 4px;
                background-color: {self.COLORS['surface']};
            }}
            QScrollBar:vertical {{
                background-color: {self.COLORS['background_alt']};
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {self.COLORS['border_light']};
                border-radius: 6px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {self.COLORS['text_muted']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
            }}
        """


# Global styles instance
_styles_instance = None

def get_app_styles() -> AppStyles:
    """
    Get the global AppStyles instance.
    
    Returns:
        AppStyles instance
    """
    global _styles_instance
    if _styles_instance is None:
        _styles_instance = AppStyles()
    return _styles_instance

def refresh_app_styles():
    """Refresh the global styles instance (useful when theme changes)."""
    global _styles_instance
    _styles_instance = None