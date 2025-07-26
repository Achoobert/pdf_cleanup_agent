"""
Process Handler

Manages QProcess instances for running external scripts and commands.
"""

from PyQt5.QtCore import QProcess, pyqtSignal, QTimer
from typing import Dict, Optional, List, NamedTuple
from dataclasses import dataclass
from enum import Enum
import sys
import os
import uuid

from .base_handler import BaseHandler


class ProcessState(Enum):
    """Process execution states."""
    QUEUED = "queued"
    RUNNING = "running"
    FINISHED = "finished"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ProcessInfo:
    """Information about a process."""
    process_id: str
    command: str
    args: List[str]
    working_dir: Optional[str]
    state: ProcessState
    exit_code: Optional[int] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None


class QueuedProcess(NamedTuple):
    """Represents a queued process."""
    process_id: str
    command: str
    args: List[str]
    working_dir: Optional[str]


class ProcessManager(BaseHandler):
    """
    Manages multiple QProcess instances for running external scripts.
    
    This class provides a centralized way to manage process execution,
    including queuing, cancellation, and output streaming with sequential
    processing support.
    """
    
    # Signals for process events
    process_started = pyqtSignal(str)  # process_id
    process_finished = pyqtSignal(str, int)  # process_id, exit_code
    process_output = pyqtSignal(str, str)  # process_id, output
    process_error = pyqtSignal(str, str)  # process_id, error
    process_queued = pyqtSignal(str)  # process_id
    process_cancelled = pyqtSignal(str)  # process_id
    queue_empty = pyqtSignal()  # All processes completed
    
    # Enhanced progress signals
    process_progress_updated = pyqtSignal(str, int, str)  # process_id, percentage, message
    queue_status_changed = pyqtSignal(int, int)  # queue_length, active_count
    
    def __init__(self, parent=None, max_concurrent_processes: int = 1, auto_process_queue: bool = True):
        super().__init__(parent)
        self.active_processes: Dict[str, QProcess] = {}
        self.process_queue: List[QueuedProcess] = []
        self.process_info: Dict[str, ProcessInfo] = {}
        self.max_concurrent_processes = max_concurrent_processes
        self.auto_process_queue = auto_process_queue
        
        # Timer for checking queue
        self.queue_timer = QTimer()
        self.queue_timer.timeout.connect(self._process_queue)
        self.queue_timer.setSingleShot(True)
        
    def _setup(self):
        """Setup the process manager."""
        # Start queue processing timer
        self.queue_timer.start(100)
        
    def queue_process(self, command: str, args: List[str] = None, 
                     working_dir: str = None, process_id: str = None) -> str:
        """
        Queue a process for execution.
        
        Args:
            command: Command to execute
            args: Command arguments
            working_dir: Working directory for the process
            process_id: Optional process identifier (auto-generated if None)
            
        Returns:
            Process ID for tracking
        """
        if process_id is None:
            process_id = str(uuid.uuid4())[:8]
            
        if args is None:
            args = []
            
        # Create process info
        process_info = ProcessInfo(
            process_id=process_id,
            command=command,
            args=args,
            working_dir=working_dir,
            state=ProcessState.QUEUED
        )
        self.process_info[process_id] = process_info
        
        # Add to queue
        queued_process = QueuedProcess(process_id, command, args, working_dir)
        self.process_queue.append(queued_process)
        
        self.process_queued.emit(process_id)
        self._emit_status(f"Process {process_id} queued")
        
        # Emit queue status update
        self.queue_status_changed.emit(len(self.process_queue), len(self.active_processes))
        
        # Start processing queue if auto processing is enabled
        if self.auto_process_queue and not self.queue_timer.isActive():
            self.queue_timer.start(100)
        
        return process_id
        
    def start_process(self, process_id: str, command: str, args: List[str] = None, 
                     working_dir: str = None) -> bool:
        """
        Start a new process immediately (bypassing queue).
        
        Args:
            process_id: Unique identifier for the process
            command: Command to execute
            args: Command arguments
            working_dir: Working directory for the process
            
        Returns:
            True if process started successfully, False otherwise
        """
        if process_id in self.active_processes:
            self._handle_error("process_error", f"Process {process_id} already running")
            return False
            
        if len(self.active_processes) >= self.max_concurrent_processes:
            self._handle_error("process_error", f"Maximum concurrent processes ({self.max_concurrent_processes}) reached")
            return False
            
        if args is None:
            args = []
            
        try:
            process = QProcess(self)
            
            # Setup process connections
            process.readyReadStandardOutput.connect(
                lambda: self._handle_stdout(process_id)
            )
            process.readyReadStandardError.connect(
                lambda: self._handle_stderr(process_id)
            )
            process.finished.connect(
                lambda exit_code, exit_status: self._handle_finished(process_id, exit_code)
            )
            
            # Set working directory if specified
            if working_dir:
                process.setWorkingDirectory(working_dir)
                
            # Store process reference
            self.active_processes[process_id] = process
            
            # Update process info
            if process_id not in self.process_info:
                self.process_info[process_id] = ProcessInfo(
                    process_id=process_id,
                    command=command,
                    args=args,
                    working_dir=working_dir,
                    state=ProcessState.RUNNING
                )
            else:
                self.process_info[process_id].state = ProcessState.RUNNING
                
            self.process_info[process_id].start_time = self._get_current_time()
            
            # Start the process
            if args:
                process.start(command, args)
            else:
                process.start(command)
                
            if process.waitForStarted(3000):
                self.process_started.emit(process_id)
                self._emit_status(f"Process {process_id} started")
                
                # Emit queue status update
                self.queue_status_changed.emit(len(self.process_queue), len(self.active_processes))
                return True
            else:
                self._cleanup_process(process_id)
                self._handle_error("process_error", f"Failed to start process {process_id}")
                return False
                
        except Exception as e:
            self._cleanup_process(process_id)
            self._handle_error("process_error", f"Error starting process {process_id}: {e}")
            return False
            
    def cancel_process(self, process_id: str) -> bool:
        """
        Cancel a process (remove from queue or stop if running).
        
        Args:
            process_id: Process identifier
            
        Returns:
            True if process was cancelled, False otherwise
        """
        # Check if process is in queue
        for i, queued_process in enumerate(self.process_queue):
            if queued_process.process_id == process_id:
                self.process_queue.pop(i)
                if process_id in self.process_info:
                    self.process_info[process_id].state = ProcessState.CANCELLED
                self.process_cancelled.emit(process_id)
                self._emit_status(f"Process {process_id} cancelled (removed from queue)")
                return True
                
        # Check if process is running
        if process_id in self.active_processes:
            return self.stop_process(process_id, force=False)
            
        return False
        
    def stop_process(self, process_id: str, force: bool = False) -> bool:
        """
        Stop a running process.
        
        Args:
            process_id: Process identifier
            force: If True, kill the process immediately
            
        Returns:
            True if process was stopped, False otherwise
        """
        if process_id not in self.active_processes:
            return False
            
        try:
            process = self.active_processes[process_id]
            
            # Update process info
            if process_id in self.process_info:
                self.process_info[process_id].state = ProcessState.CANCELLED
                self.process_info[process_id].end_time = self._get_current_time()
            
            if force:
                process.kill()
            else:
                process.terminate()
                if not process.waitForFinished(3000):
                    process.kill()
                    
            self.process_cancelled.emit(process_id)
            self._emit_status(f"Process {process_id} stopped")
            return True
            
        except Exception as e:
            self._handle_error("process_error", f"Error stopping process {process_id}: {e}")
            return False
            
    def stop_all_processes(self):
        """Stop all running processes and clear queue."""
        # Clear queue
        cancelled_queue = [p.process_id for p in self.process_queue]
        self.process_queue.clear()
        
        for process_id in cancelled_queue:
            if process_id in self.process_info:
                self.process_info[process_id].state = ProcessState.CANCELLED
            self.process_cancelled.emit(process_id)
        
        # Stop running processes
        process_ids = list(self.active_processes.keys())
        for process_id in process_ids:
            self.stop_process(process_id, force=True)
            
    def _process_queue(self):
        """Process the next item in the queue if possible."""
        if not self.process_queue:
            if not self.active_processes:
                self.queue_empty.emit()
            return
            
        if len(self.active_processes) >= self.max_concurrent_processes:
            return
            
        # Get next process from queue
        queued_process = self.process_queue.pop(0)
        
        # Start the process
        success = self.start_process(
            queued_process.process_id,
            queued_process.command,
            queued_process.args,
            queued_process.working_dir
        )
        
        if not success and queued_process.process_id in self.process_info:
            self.process_info[queued_process.process_id].state = ProcessState.FAILED
            
        # Continue processing queue if auto processing is enabled
        if self.auto_process_queue and self.process_queue:
            self.queue_timer.start(100)
            
    def get_process_info(self, process_id: str) -> Optional[ProcessInfo]:
        """Get information about a process."""
        return self.process_info.get(process_id)
        
    def get_all_process_info(self) -> Dict[str, ProcessInfo]:
        """Get information about all processes."""
        return self.process_info.copy()
        
    def get_queue_length(self) -> int:
        """Get the number of processes in the queue."""
        return len(self.process_queue)
        
    def get_active_process_count(self) -> int:
        """Get the number of currently running processes."""
        return len(self.active_processes)
        
    def is_process_running(self, process_id: str) -> bool:
        """Check if a process is currently running."""
        if process_id not in self.active_processes:
            return False
        return self.active_processes[process_id].state() != QProcess.NotRunning
        
    def clear_completed_processes(self):
        """Clear information about completed processes."""
        completed_ids = [
            pid for pid, info in self.process_info.items()
            if info.state in [ProcessState.FINISHED, ProcessState.FAILED, ProcessState.CANCELLED]
            and pid not in self.active_processes
        ]
        
        for process_id in completed_ids:
            del self.process_info[process_id]
            
    def get_python_executable(self) -> str:
        """Get the appropriate Python executable path."""
        venv_python = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', '..', '..', 'venv', 'bin', 'python'
        ))
        
        if os.path.exists(venv_python):
            return venv_python
        return sys.executable
        
    def _get_current_time(self) -> float:
        """Get current timestamp."""
        import time
        return time.time()
        
    def _handle_stdout(self, process_id: str):
        """Handle standard output from a process."""
        if process_id in self.active_processes:
            process = self.active_processes[process_id]
            output = process.readAllStandardOutput().data().decode(errors='replace')
            if output:
                # Split output into lines for better handling
                lines = output.rstrip().split('\n')
                for line in lines:
                    if line.strip():
                        self.process_output.emit(process_id, line.strip())
                        
                        # Try to extract progress information
                        progress_percentage = self._extract_progress_from_output(line.strip())
                        if progress_percentage >= 0:
                            self.process_progress_updated.emit(process_id, progress_percentage, line.strip())
                
    def _handle_stderr(self, process_id: str):
        """Handle standard error from a process."""
        if process_id in self.active_processes:
            process = self.active_processes[process_id]
            error = process.readAllStandardError().data().decode(errors='replace')
            if error:
                # Split error into lines for better handling
                lines = error.rstrip().split('\n')
                for line in lines:
                    if line.strip():
                        self.process_error.emit(process_id, line.strip())
                
    def _handle_finished(self, process_id: str, exit_code: int):
        """Handle process completion."""
        # Update process info
        if process_id in self.process_info:
            self.process_info[process_id].exit_code = exit_code
            self.process_info[process_id].end_time = self._get_current_time()
            
            if exit_code == 0:
                self.process_info[process_id].state = ProcessState.FINISHED
            else:
                self.process_info[process_id].state = ProcessState.FAILED
        
        self.process_finished.emit(process_id, exit_code)
        self._cleanup_process(process_id)
        
        if exit_code == 0:
            self._emit_status(f"Process {process_id} completed successfully")
        else:
            self._emit_status(f"Process {process_id} failed with exit code {exit_code}")
            
        # Emit queue status update
        self.queue_status_changed.emit(len(self.process_queue), len(self.active_processes))
        
        # Continue processing queue if auto processing is enabled
        if self.auto_process_queue and self.process_queue:
            self.queue_timer.start(100)
            
    def _cleanup_process(self, process_id: str):
        """Clean up process resources."""
        if process_id in self.active_processes:
            process = self.active_processes[process_id]
            try:
                # Disconnect signals to prevent issues during cleanup
                process.readyReadStandardOutput.disconnect()
                process.readyReadStandardError.disconnect()
                process.finished.disconnect()
            except:
                pass  # Signals may already be disconnected
                
            process.deleteLater()
            del self.active_processes[process_id]
            
    def cleanup(self):
        """Cleanup all processes when shutting down."""
        self.queue_timer.stop()
        self.stop_all_processes()
        
        # Wait for processes to finish (create a copy of the list to avoid iteration issues)
        active_processes = list(self.active_processes.values())
        for process in active_processes:
            if process.state() != QProcess.NotRunning:
                process.waitForFinished(1000)
                
        super().cleanup()
    
    def _extract_progress_from_output(self, output: str) -> int:
        """
        Extract progress percentage from process output.
        
        Args:
            output: Process output string
            
        Returns:
            Progress percentage (0-100) or -1 if no progress found
        """
        import re
        
        # Common progress patterns
        patterns = [
            r'(\d+)%',  # "50%"
            r'(\d+)/(\d+)',  # "5/10"
            r'Progress:\s*(\d+)',  # "Progress: 75"
            r'Step\s*(\d+)\s*of\s*(\d+)',  # "Step 3 of 5"
            r'Processing\s*(\d+)\s*of\s*(\d+)',  # "Processing 3 of 5"
            r'\[(\d+)/(\d+)\]',  # "[3/5]"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                if len(match.groups()) == 1:
                    # Direct percentage
                    return min(100, max(0, int(match.group(1))))
                elif len(match.groups()) == 2:
                    # Fraction format
                    try:
                        current = int(match.group(1))
                        total = int(match.group(2))
                        if total > 0:
                            return min(100, max(0, int((current / total) * 100)))
                    except ValueError:
                        continue
        
        return -1  # No progress found