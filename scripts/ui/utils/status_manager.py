"""
Status Manager

Centralized status and progress management system for the PDF Cleanup Agent.
"""

from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from typing import Dict, Optional, List, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import uuid


class StatusLevel(Enum):
    """Status message severity levels."""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    DEBUG = "debug"


class ProgressType(Enum):
    """Types of progress indicators."""
    DETERMINATE = "determinate"  # Known progress (0-100%)
    INDETERMINATE = "indeterminate"  # Unknown progress (busy indicator)
    PULSE = "pulse"  # Pulsing indicator


@dataclass
class StatusMessage:
    """Represents a status message."""
    id: str
    message: str
    level: StatusLevel
    timestamp: datetime
    source: Optional[str] = None
    details: Optional[str] = None
    persistent: bool = False
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())[:8]


@dataclass
class ProgressInfo:
    """Represents progress information."""
    id: str
    title: str
    progress_type: ProgressType
    current: int = 0
    maximum: int = 100
    message: str = ""
    is_active: bool = True
    start_time: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())[:8]
        if not self.start_time:
            self.start_time = datetime.now()
    
    @property
    def percentage(self) -> float:
        """Get progress as percentage."""
        if self.maximum == 0:
            return 0.0
        return min(100.0, (self.current / self.maximum) * 100.0)
    
    @property
    def is_complete(self) -> bool:
        """Check if progress is complete."""
        return self.current >= self.maximum and self.progress_type == ProgressType.DETERMINATE


@dataclass
class BusyIndicator:
    """Represents a busy indicator for long-running operations."""
    id: str
    operation: str
    message: str = ""
    is_active: bool = True
    start_time: Optional[datetime] = None
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())[:8]
        if not self.start_time:
            self.start_time = datetime.now()


class StatusManager(QObject):
    """
    Centralized status and progress management system.
    
    This class manages status messages, progress indicators, and busy states
    across the entire application, providing a unified interface for UI updates.
    """
    
    # Signals for status updates
    status_message_added = pyqtSignal(StatusMessage)
    status_message_updated = pyqtSignal(StatusMessage)
    status_message_removed = pyqtSignal(str)  # message_id
    status_cleared = pyqtSignal()
    
    # Signals for progress updates
    progress_started = pyqtSignal(ProgressInfo)
    progress_updated = pyqtSignal(ProgressInfo)
    progress_finished = pyqtSignal(str)  # progress_id
    progress_cancelled = pyqtSignal(str)  # progress_id
    
    # Signals for busy indicators
    busy_started = pyqtSignal(BusyIndicator)
    busy_updated = pyqtSignal(BusyIndicator)
    busy_finished = pyqtSignal(str)  # busy_id
    
    # General UI state signals
    ui_state_changed = pyqtSignal(dict)  # state_dict
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Status message storage
        self.status_messages: Dict[str, StatusMessage] = {}
        self.status_history: List[StatusMessage] = []
        self.max_history_size = 1000
        
        # Progress tracking
        self.active_progress: Dict[str, ProgressInfo] = {}
        self.progress_history: List[ProgressInfo] = []
        
        # Busy indicators
        self.busy_indicators: Dict[str, BusyIndicator] = {}
        
        # Auto-cleanup timer for non-persistent messages
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self._cleanup_old_messages)
        self.cleanup_timer.start(30000)  # Clean up every 30 seconds
        
        # Message display timer for temporary messages
        self.message_timers: Dict[str, QTimer] = {}
        
    def add_status_message(self, message: str, level: StatusLevel = StatusLevel.INFO,
                          source: Optional[str] = None, details: Optional[str] = None,
                          persistent: bool = False, auto_remove_ms: Optional[int] = None) -> str:
        """
        Add a status message.
        
        Args:
            message: Status message text
            level: Message severity level
            source: Source component/module name
            details: Additional details about the status
            persistent: Whether message should persist until manually removed
            auto_remove_ms: Auto-remove after specified milliseconds
            
        Returns:
            Message ID for tracking
        """
        status_msg = StatusMessage(
            id="",  # Will be auto-generated
            message=message,
            level=level,
            timestamp=datetime.now(),
            source=source,
            details=details,
            persistent=persistent
        )
        
        self.status_messages[status_msg.id] = status_msg
        self.status_history.append(status_msg)
        
        # Trim history if needed
        if len(self.status_history) > self.max_history_size:
            self.status_history = self.status_history[-self.max_history_size:]
        
        self.status_message_added.emit(status_msg)
        
        # Set up auto-removal timer if specified
        if auto_remove_ms and not persistent:
            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(lambda: self.remove_status_message(status_msg.id))
            timer.start(auto_remove_ms)
            self.message_timers[status_msg.id] = timer
        
        return status_msg.id
    
    def update_status_message(self, message_id: str, message: Optional[str] = None,
                             level: Optional[StatusLevel] = None, details: Optional[str] = None) -> bool:
        """
        Update an existing status message.
        
        Args:
            message_id: ID of message to update
            message: New message text (optional)
            level: New severity level (optional)
            details: New details (optional)
            
        Returns:
            True if message was updated, False if not found
        """
        if message_id not in self.status_messages:
            return False
        
        status_msg = self.status_messages[message_id]
        
        if message is not None:
            status_msg.message = message
        if level is not None:
            status_msg.level = level
        if details is not None:
            status_msg.details = details
        
        status_msg.timestamp = datetime.now()
        
        self.status_message_updated.emit(status_msg)
        return True
    
    def remove_status_message(self, message_id: str) -> bool:
        """
        Remove a status message.
        
        Args:
            message_id: ID of message to remove
            
        Returns:
            True if message was removed, False if not found
        """
        if message_id not in self.status_messages:
            return False
        
        del self.status_messages[message_id]
        
        # Clean up timer if exists
        if message_id in self.message_timers:
            self.message_timers[message_id].stop()
            del self.message_timers[message_id]
        
        self.status_message_removed.emit(message_id)
        return True
    
    def clear_status_messages(self, level: Optional[StatusLevel] = None):
        """
        Clear status messages.
        
        Args:
            level: If specified, only clear messages of this level
        """
        if level is None:
            # Clear all non-persistent messages
            to_remove = [
                msg_id for msg_id, msg in self.status_messages.items()
                if not msg.persistent
            ]
        else:
            # Clear messages of specific level
            to_remove = [
                msg_id for msg_id, msg in self.status_messages.items()
                if msg.level == level and not msg.persistent
            ]
        
        for msg_id in to_remove:
            self.remove_status_message(msg_id)
        
        if not level:
            self.status_cleared.emit()
    
    def start_progress(self, title: str, progress_type: ProgressType = ProgressType.DETERMINATE,
                      maximum: int = 100, message: str = "", progress_id: Optional[str] = None) -> str:
        """
        Start a progress indicator.
        
        Args:
            title: Progress title/description
            progress_type: Type of progress indicator
            maximum: Maximum progress value (for determinate progress)
            message: Initial progress message
            progress_id: Optional custom progress ID
            
        Returns:
            Progress ID for tracking
        """
        if progress_id is None:
            progress_id = str(uuid.uuid4())[:8]
        
        progress_info = ProgressInfo(
            id=progress_id,
            title=title,
            progress_type=progress_type,
            current=0,
            maximum=maximum,
            message=message,
            is_active=True,
            start_time=datetime.now()
        )
        
        self.active_progress[progress_id] = progress_info
        self.progress_started.emit(progress_info)
        
        return progress_id
    
    def update_progress(self, progress_id: str, current: Optional[int] = None,
                       maximum: Optional[int] = None, message: Optional[str] = None) -> bool:
        """
        Update progress information.
        
        Args:
            progress_id: ID of progress to update
            current: New current progress value
            maximum: New maximum progress value
            message: New progress message
            
        Returns:
            True if progress was updated, False if not found
        """
        if progress_id not in self.active_progress:
            return False
        
        progress_info = self.active_progress[progress_id]
        
        if current is not None:
            progress_info.current = current
        if maximum is not None:
            progress_info.maximum = maximum
        if message is not None:
            progress_info.message = message
        
        # Estimate completion time for determinate progress
        if progress_info.progress_type == ProgressType.DETERMINATE and progress_info.current > 0:
            elapsed = datetime.now() - progress_info.start_time
            if progress_info.current < progress_info.maximum:
                remaining_ratio = (progress_info.maximum - progress_info.current) / progress_info.current
                estimated_remaining = elapsed * remaining_ratio
                progress_info.estimated_completion = datetime.now() + estimated_remaining
        
        self.progress_updated.emit(progress_info)
        
        # Auto-finish if complete
        if progress_info.is_complete:
            self.finish_progress(progress_id)
        
        return True
    
    def finish_progress(self, progress_id: str, message: Optional[str] = None) -> bool:
        """
        Finish a progress indicator.
        
        Args:
            progress_id: ID of progress to finish
            message: Optional completion message
            
        Returns:
            True if progress was finished, False if not found
        """
        if progress_id not in self.active_progress:
            return False
        
        progress_info = self.active_progress[progress_id]
        progress_info.is_active = False
        progress_info.current = progress_info.maximum
        
        if message:
            progress_info.message = message
        
        # Move to history
        self.progress_history.append(progress_info)
        del self.active_progress[progress_id]
        
        self.progress_finished.emit(progress_id)
        return True
    
    def cancel_progress(self, progress_id: str) -> bool:
        """
        Cancel a progress indicator.
        
        Args:
            progress_id: ID of progress to cancel
            
        Returns:
            True if progress was cancelled, False if not found
        """
        if progress_id not in self.active_progress:
            return False
        
        progress_info = self.active_progress[progress_id]
        progress_info.is_active = False
        
        # Move to history
        self.progress_history.append(progress_info)
        del self.active_progress[progress_id]
        
        self.progress_cancelled.emit(progress_id)
        return True
    
    def start_busy_indicator(self, operation: str, message: str = "", busy_id: Optional[str] = None) -> str:
        """
        Start a busy indicator for long-running operations.
        
        Args:
            operation: Operation description
            message: Optional status message
            busy_id: Optional custom busy ID
            
        Returns:
            Busy indicator ID for tracking
        """
        if busy_id is None:
            busy_id = str(uuid.uuid4())[:8]
        
        busy_indicator = BusyIndicator(
            id=busy_id,
            operation=operation,
            message=message,
            is_active=True,
            start_time=datetime.now()
        )
        
        self.busy_indicators[busy_id] = busy_indicator
        self.busy_started.emit(busy_indicator)
        
        return busy_id
    
    def update_busy_indicator(self, busy_id: str, message: Optional[str] = None) -> bool:
        """
        Update a busy indicator.
        
        Args:
            busy_id: ID of busy indicator to update
            message: New status message
            
        Returns:
            True if indicator was updated, False if not found
        """
        if busy_id not in self.busy_indicators:
            return False
        
        if message is not None:
            self.busy_indicators[busy_id].message = message
        
        self.busy_updated.emit(self.busy_indicators[busy_id])
        return True
    
    def finish_busy_indicator(self, busy_id: str) -> bool:
        """
        Finish a busy indicator.
        
        Args:
            busy_id: ID of busy indicator to finish
            
        Returns:
            True if indicator was finished, False if not found
        """
        if busy_id not in self.busy_indicators:
            return False
        
        self.busy_indicators[busy_id].is_active = False
        del self.busy_indicators[busy_id]
        
        self.busy_finished.emit(busy_id)
        return True
    
    def get_status_messages(self, level: Optional[StatusLevel] = None) -> List[StatusMessage]:
        """
        Get current status messages.
        
        Args:
            level: If specified, only return messages of this level
            
        Returns:
            List of status messages
        """
        if level is None:
            return list(self.status_messages.values())
        else:
            return [msg for msg in self.status_messages.values() if msg.level == level]
    
    def get_active_progress(self) -> List[ProgressInfo]:
        """Get all active progress indicators."""
        return list(self.active_progress.values())
    
    def get_busy_indicators(self) -> List[BusyIndicator]:
        """Get all active busy indicators."""
        return list(self.busy_indicators.values())
    
    def is_busy(self) -> bool:
        """Check if any operations are currently busy."""
        return len(self.busy_indicators) > 0 or len(self.active_progress) > 0
    
    def get_ui_state(self) -> dict:
        """
        Get current UI state information.
        
        Returns:
            Dictionary containing current UI state
        """
        return {
            'is_busy': self.is_busy(),
            'active_progress_count': len(self.active_progress),
            'busy_indicator_count': len(self.busy_indicators),
            'status_message_count': len(self.status_messages),
            'has_errors': any(msg.level == StatusLevel.ERROR for msg in self.status_messages.values()),
            'has_warnings': any(msg.level == StatusLevel.WARNING for msg in self.status_messages.values())
        }
    
    def _cleanup_old_messages(self):
        """Clean up old non-persistent status messages."""
        cutoff_time = datetime.now()
        cutoff_time = cutoff_time.replace(minute=cutoff_time.minute - 5)  # 5 minutes ago
        
        to_remove = [
            msg_id for msg_id, msg in self.status_messages.items()
            if not msg.persistent and msg.timestamp < cutoff_time
        ]
        
        for msg_id in to_remove:
            self.remove_status_message(msg_id)
    
    def cleanup(self):
        """Cleanup status manager resources."""
        self.cleanup_timer.stop()
        
        # Stop all message timers
        for timer in self.message_timers.values():
            timer.stop()
        self.message_timers.clear()
        
        # Clear all data
        self.status_messages.clear()
        self.active_progress.clear()
        self.busy_indicators.clear()