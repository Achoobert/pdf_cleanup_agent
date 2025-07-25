"""
Application Styles

Centralized styling and theming for the application.
"""


class AppStyles:
    """
    Centralized styling definitions for the application.
    
    This class provides consistent styling across all UI components.
    """
    
    # Color palette
    COLORS = {
        'primary': '#0078d4',
        'primary_hover': '#106ebe',
        'secondary': '#6c757d',
        'success': '#28a745',
        'warning': '#ffc107',
        'error': '#dc3545',
        'info': '#17a2b8',
        'light': '#f8f9fa',
        'dark': '#343a40',
        'background': '#ffffff',
        'border': '#dee2e6',
        'text': '#212529',
        'text_muted': '#6c757d'
    }
    
    # Drop zone styles
    DROP_ZONE_NORMAL = """
        QListWidget {
            border: 2px dashed #cccccc;
            border-radius: 5px;
            background-color: #fafafa;
            padding: 10px;
        }
        QListWidget:hover {
            border-color: #999999;
        }
    """
    
    DROP_ZONE_ACTIVE = """
        QListWidget {
            border: 3px solid #0078d4;
            border-radius: 5px;
            background-color: rgba(0, 120, 212, 0.1);
            padding: 10px;
        }
    """
    
    # Button styles
    BUTTON_PRIMARY = f"""
        QPushButton {{
            background-color: {COLORS['primary']};
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {COLORS['primary_hover']};
        }}
        QPushButton:pressed {{
            background-color: #005a9e;
        }}
        QPushButton:disabled {{
            background-color: {COLORS['secondary']};
            color: #ffffff;
        }}
    """
    
    BUTTON_SECONDARY = f"""
        QPushButton {{
            background-color: {COLORS['secondary']};
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
        }}
        QPushButton:hover {{
            background-color: #5a6268;
        }}
        QPushButton:pressed {{
            background-color: #545b62;
        }}
        QPushButton:disabled {{
            background-color: #e9ecef;
            color: {COLORS['text_muted']};
        }}
    """
    
    BUTTON_SUCCESS = f"""
        QPushButton {{
            background-color: {COLORS['success']};
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
        }}
        QPushButton:hover {{
            background-color: #218838;
        }}
        QPushButton:pressed {{
            background-color: #1e7e34;
        }}
    """
    
    BUTTON_WARNING = f"""
        QPushButton {{
            background-color: {COLORS['warning']};
            color: #212529;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
        }}
        QPushButton:hover {{
            background-color: #e0a800;
        }}
        QPushButton:pressed {{
            background-color: #d39e00;
        }}
    """
    
    BUTTON_ERROR = f"""
        QPushButton {{
            background-color: {COLORS['error']};
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
        }}
        QPushButton:hover {{
            background-color: #c82333;
        }}
        QPushButton:pressed {{
            background-color: #bd2130;
        }}
    """
    
    # Group box styles
    GROUP_BOX = f"""
        QGroupBox {{
            font-weight: bold;
            border: 2px solid {COLORS['border']};
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
            color: {COLORS['text']};
        }}
    """
    
    # Text edit styles
    TEXT_EDIT = f"""
        QTextEdit {{
            border: 1px solid {COLORS['border']};
            border-radius: 4px;
            padding: 8px;
            background-color: {COLORS['background']};
            selection-background-color: {COLORS['primary']};
        }}
        QTextEdit:focus {{
            border-color: {COLORS['primary']};
        }}
    """
    
    # List widget styles
    LIST_WIDGET = f"""
        QListWidget {{
            border: 1px solid {COLORS['border']};
            border-radius: 4px;
            background-color: {COLORS['background']};
            alternate-background-color: {COLORS['light']};
        }}
        QListWidget::item {{
            padding: 5px;
            border-bottom: 1px solid {COLORS['border']};
        }}
        QListWidget::item:selected {{
            background-color: {COLORS['primary']};
            color: white;
        }}
        QListWidget::item:hover {{
            background-color: {COLORS['light']};
        }}
    """
    
    # Status bar styles
    STATUS_BAR = f"""
        QStatusBar {{
            background-color: {COLORS['light']};
            border-top: 1px solid {COLORS['border']};
            color: {COLORS['text']};
        }}
    """
    
    # Progress bar styles
    PROGRESS_BAR = f"""
        QProgressBar {{
            border: 1px solid {COLORS['border']};
            border-radius: 4px;
            text-align: center;
            background-color: {COLORS['light']};
        }}
        QProgressBar::chunk {{
            background-color: {COLORS['primary']};
            border-radius: 3px;
        }}
    """
    
    @classmethod
    def get_button_style(cls, button_type: str = 'primary') -> str:
        """
        Get button style by type.
        
        Args:
            button_type: Type of button ('primary', 'secondary', 'success', 'warning', 'error')
            
        Returns:
            CSS style string
        """
        styles = {
            'primary': cls.BUTTON_PRIMARY,
            'secondary': cls.BUTTON_SECONDARY,
            'success': cls.BUTTON_SUCCESS,
            'warning': cls.BUTTON_WARNING,
            'error': cls.BUTTON_ERROR
        }
        return styles.get(button_type, cls.BUTTON_PRIMARY)
        
    @classmethod
    def apply_drop_zone_style(cls, widget, active: bool = False):
        """
        Apply drop zone styling to a widget.
        
        Args:
            widget: Widget to style
            active: Whether to apply active (drag over) styling
        """
        if active:
            widget.setStyleSheet(cls.DROP_ZONE_ACTIVE)
        else:
            widget.setStyleSheet(cls.DROP_ZONE_NORMAL)
            
    @classmethod
    def get_main_window_style(cls) -> str:
        """
        Get the main window stylesheet.
        
        Returns:
            CSS style string for the main window
        """
        return f"""
            QMainWindow {{
                background-color: {cls.COLORS['background']};
                color: {cls.COLORS['text']};
            }}
            QWidget {{
                background-color: {cls.COLORS['background']};
                color: {cls.COLORS['text']};
            }}
        """