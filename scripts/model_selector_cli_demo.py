import os
import yaml
from model_selector import ModelSelector

HOME_CONFIG_PATH = os.path.expanduser("~/.pdf_cleanup_agent/config.yml")
PROJECT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.yml")

def save_user_selection(backend, model=None):
    config = {"backend": backend}
    if model:
        config["ollama_model"] = model
    # Save to home config
    os.makedirs(os.path.dirname(HOME_CONFIG_PATH), exist_ok=True)
    with open(HOME_CONFIG_PATH, "w") as f:
        yaml.safe_dump(config, f)
    # Save to project config
    with open(PROJECT_CONFIG_PATH, "w") as f:
        yaml.safe_dump(config, f)

def load_user_selection():
    # Prefer home config, fall back to project config
    if os.path.exists(HOME_CONFIG_PATH):
        with open(HOME_CONFIG_PATH, "r") as f:
            return yaml.safe_load(f)
    elif os.path.exists(PROJECT_CONFIG_PATH):
        with open(PROJECT_CONFIG_PATH, "r") as f:
            return yaml.safe_load(f)
    else:
        return None


def main():
    selector = ModelSelector()
    print("=== Smart Model Selector Demo ===\n")

    # Load previous selection
    last_selection = load_user_selection()
    if last_selection:
        print(f"Last selection: {last_selection}")
        use_last = input("Use last selection? (y/n): ").strip().lower()
        if use_last == 'y':
            print(f"Using previous selection: {last_selection}")
            return

    # Ollama status
    print(f"Ollama installed: {selector.ollama_installed}")
    if not selector.ollama_installed:
        print("Ollama is not installed.")
        print(selector.get_ollama_install_instructions())
    else:
        print("Testing Ollama connection...")
        connected = selector.test_ollama_connection()
        print(f"Ollama connected: {connected}")
        if connected:
            models = selector.list_ollama_models()
            print("\nInstalled Ollama models:")
            if models:
                for m in models:
                    print(f"  {m['name']} (ID: {m['id']}, Size: {m['size']}, Modified: {m['modified']})")
            else:
                print("  No models found.")

    # Hardware info
    print("\nHardware Info:")
    for k, v in selector.hardware_info.items():
        print(f"  {k}: {v}")

    # Model recommendation
    print(f"\nRecommended model: {selector.model_recommendation}")

    # Gemini stub
    print(f"Gemini available: {selector.gemini_available}")

    # Backend selection
    print("\nSelect backend:")
    options = []
    ollama_models = []
    if selector.ollama_installed and selector.ollama_connected:
        ollama_models = selector.list_ollama_models()
        for m in ollama_models:
            options.append(f"Ollama: {m['name']}")
    if selector.gemini_available:
        options.append('Gemini (stub)')
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    if not options:
        print("No available backends detected.")
        return
    choice = input(f"Enter choice (1-{len(options)}): ").strip()
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(options):
            print(f"You selected: {options[idx]}")
            # Save selection to config.yml
            if options[idx].startswith("Ollama: "):
                model_name = options[idx].split(": ", 1)[1]
                save_user_selection("ollama", model_name)
            else:
                save_user_selection("gemini")
        else:
            print("Invalid selection.")
    except ValueError:
        print("Invalid input.")

if __name__ == "__main__":
    main() 