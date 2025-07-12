import subprocess
import platform
import shutil
import sys

class ModelSelector:
    def __init__(self):
        self.ollama_installed = self.check_ollama_installed()
        self.ollama_connected = False
        self.hardware_info = self.detect_hardware()
        self.model_recommendation = self.recommend_model()
        self.gemini_available = self.check_gemini_stub()

    def check_ollama_installed(self):
        """Check if Ollama is installed by looking for the executable."""
        return shutil.which('ollama') is not None

    def test_ollama_connection(self):
        """Try running a simple Ollama command to test connectivity."""
        if not self.ollama_installed:
            self.ollama_connected = False
            return False
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=5)
            self.ollama_connected = result.returncode == 0
            return self.ollama_connected
        except Exception:
            self.ollama_connected = False
            return False

    def detect_hardware(self):
        """Detect basic hardware info (CPU, RAM)."""
        info = {
            'platform': platform.system(),
            'cpu': platform.processor(),
            'ram_gb': None,
        }
        try:
            if sys.platform == 'darwin':
                import psutil
                info['ram_gb'] = round(psutil.virtual_memory().total / (1024 ** 3), 1)
            elif sys.platform == 'linux' or sys.platform == 'linux2':
                import psutil
                info['ram_gb'] = round(psutil.virtual_memory().total / (1024 ** 3), 1)
            elif sys.platform == 'win32':
                import psutil
                info['ram_gb'] = round(psutil.virtual_memory().total / (1024 ** 3), 1)
        except ImportError:
            info['ram_gb'] = None
        return info

    def recommend_model(self):
        """Recommend a model based on detected hardware."""
        ram = self.hardware_info.get('ram_gb')
        if ram is None:
            return 'llama2 (default, unknown RAM)'
        if ram < 8:
            return 'phi3 (lightweight, <8GB RAM)'
        elif ram < 16:
            return 'llama2 (standard, 8-16GB RAM)'
        else:
            return 'mixtral (large, >16GB RAM)'

    def check_gemini_stub(self):
        """Stub for Gemini availability (always True for now)."""
        return True

    def list_ollama_models(self):
        """Return a list of installed Ollama models (name, id, size, modified)."""
        if not self.ollama_installed:
            return []
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                return []
            lines = result.stdout.strip().split('\n')
            models = []
            for line in lines[1:]:  # skip header
                parts = [p for p in line.split(' ') if p]
                if len(parts) >= 4:
                    models.append({
                        'name': parts[0],
                        'id': parts[1],
                        'size': parts[2],
                        'modified': ' '.join(parts[3:]),
                    })
            return models
        except Exception:
            return []

    def get_status(self):
        return {
            'ollama_installed': self.ollama_installed,
            'ollama_connected': self.ollama_connected,
            'hardware_info': self.hardware_info,
            'model_recommendation': self.model_recommendation,
            'gemini_available': self.gemini_available,
        }

    def get_ollama_install_instructions(self):
        if self.hardware_info['platform'] == 'Darwin':
            return 'Install Ollama: brew install ollama (see https://ollama.com/download)'
        elif self.hardware_info['platform'] == 'Linux':
            return 'Install Ollama: curl -fsSL https://ollama.com/install.sh | sh'
        elif self.hardware_info['platform'] == 'Windows':
            return 'Install Ollama: Download from https://ollama.com/download'
        else:
            return 'See https://ollama.com/download for instructions.' 