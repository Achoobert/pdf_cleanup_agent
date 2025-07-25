"""
Process Handler

Manages QProcess instances for running external scripts and commands.
"""

from PyQt5.QtCore import QProcess, pyqtSignal
from typing import Dict, Optional
import sys
import os

from .base_handler import BaseHandler


class ProcessManager(BaseHandler):
    """
    Manages multiple QProcess instances for running external scripts.
    
    This class provides a centralized way to manage process execution,
    including queuing, cancellation, and output streaming.
    """
    
    # Signals for process events
    process_started = pyqtSignal(str)  # process_id
    process_finished = pyqtSignal(str, int)  # process_id, exit_code
    process_output = pyqtSignal(str, str)  # process_id, output
    process_error = pyqtSignal(str, str)  # process_id, error
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_processes: Dict[str, QProcess] = {}
        self.process_queue: list = []
        
    def _setup(self):
        """Setup the process manager."""
        # No specific setup required for process manager
        pass
        
    def start_process(self, process_id: str, command: str, args: list = None, 
                     working_dir: str = None) -> bool:
        """
        Start a new process.
        
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
            
            # Start the process
            if args:
                process.start(command, args)
            else:
                process.start(command)
                
            if process.waitForStarted(3000):
                self.process_started.emit(process_id)
                self._emit_status(f"Process {process_id} started")
                return True
            else:
                self._cleanup_process(process_id)
                self._handle_error("process_error", f"Failed to start process {process_id}")
                return False
                
        except Exception as e:
            self._cleanup_process(process_id)
            self._handle_error("process_error", f"Error starting process {process_id}: {e}")
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
            
            if force:
                process.kill()
            else:
                process.terminate()
                if not process.waitForFinished(3000):
                    process.kill()
                    
            self._emit_status(f"Process {process_id} stopped")
            return True
            
        except Exception as e:
            self._handle_error("process_error", f"Error stopping process {process_id}: {e}")
            return False
            
    def stop_all_processes(self):
        """Stop all running processes."""
        process_ids = list(self.active_processes.keys())
        for process_id in process_ids:
            self.stop_process(process_id, force=True)
            
    def is_process_running(self, process_id: str) -> bool:
        """Check if a process is currently running."""
        if process_id not in self.active_processes:
            return False
        return self.active_processes[process_id].state() != QProcess.NotRunning
        
    def get_python_executable(self) -> str:
        """Get the appropriate Python executable path."""
        venv_python = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', '..', '..', 'venv', 'bin', 'python'
        ))
        
        if os.path.exists(venv_python):
            return venv_python
        return sys.executable
        
    def _handle_stdout(self, process_id: str):
        """Handle standard output from a process."""
        if process_id in self.active_processes:
            process = self.active_processes[process_id]
            output = process.readAllStandardOutput().data().decode(errors='replace')
            if output:
                self.process_output.emit(process_id, output.rstrip())
                
    def _handle_stderr(self, process_id: str):
        """Handle standard error from a process."""
        if process_id in self.active_processes:
            process = self.active_processes[process_id]
            error = process.readAllStandardError().data().decode(errors='replace')
            if error:
                self.process_error.emit(process_id, error.rstrip())
                
    def _handle_finished(self, process_id: str, exit_code: int):
        """Handle process completion."""
        self.process_finished.emit(process_id, exit_code)
        self._cleanup_process(process_id)
        
        if exit_code == 0:
            self._emit_status(f"Process {process_id} completed successfully")
        else:
            self._emit_status(f"Process {process_id} failed with exit code {exit_code}")
            
    def _cleanup_process(self, process_id: str):
        """Clean up process resources."""
        if process_id in self.active_processes:
            process = self.active_processes[process_id]
            process.deleteLater()
            del self.active_processes[process_id]
            
    def cleanup(self):
        """Cleanup all processes when shutting down."""
        self.stop_all_processes()
        super().cleanup()