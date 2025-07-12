import sys
import os
import subprocess
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPushButton, QMessageBox, QTextEdit, QDialog, QFileDialog, QComboBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer, QProcess
import yaml
import requests
import shutil

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from model_selector import ModelSelector


def run_hello_world():
    try:
        hello_world_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../hello_world.py'))
        result = subprocess.run([sys.executable, hello_world_path], capture_output=True, text=True, timeout=300)
        output = result.stdout.strip() or result.stderr.strip() or 'No output.'
    except Exception as e:
        output = f'Error: {e}'
    return output


class PDFDropWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAcceptDrops(True)
        self.setLayout(QVBoxLayout())

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith('.pdf'):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.lower().endswith('.pdf'):
                self.parent().handle_pdf_drop(file_path)


def main():
    app = QApplication(sys.argv)
    window = PDFDropWidget()
    window.setWindowTitle('PDF Power Converter')
    icon_path = os.path.join(os.path.dirname(__file__), 'icons', 'app_icon.png')
    if os.path.exists(icon_path):
        window.setWindowIcon(QIcon(icon_path))
    label = QLabel('Hello, World!')
    window.layout().addWidget(label)
    btn = QPushButton('Run hello_world.py')
    window.layout().addWidget(btn)
    output_text = QTextEdit()
    output_text.setReadOnly(True)
    window.layout().addWidget(output_text)

    # Add button for opening text preview
    preview_btn = QPushButton('Open Text Preview')
    window.layout().addWidget(preview_btn)

    # Add button for running agent_stream.py
    run_agent_btn = QPushButton('Run agent_stream.py')
    window.layout().addWidget(run_agent_btn)
    stop_agent_btn = QPushButton('Stop agent_stream.py')
    stop_agent_btn.setEnabled(False)
    window.layout().addWidget(stop_agent_btn)

    # Add button for editing the LLM prompt
    edit_prompt_btn = QPushButton('Edit LLM Prompt')
    window.layout().addWidget(edit_prompt_btn)

    # Add button for re-processing markdown with LLM
    reprocess_btn = QPushButton('Re-process Markdown with LLM')
    window.layout().addWidget(reprocess_btn)

    # Add button for post-processing to trim artefacts
    trim_btn = QPushButton('Trim Artefacts (Post-process)')
    window.layout().addWidget(trim_btn)

    # Add button for model selection
    model_select_btn = QPushButton('Model Selection')
    window.layout().addWidget(model_select_btn)

    agent_process = QProcess(window)

    def run_agent_stream():
        # Use venv python if available
        venv_python = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../venv/bin/python'))
        if not os.path.exists(venv_python):
            venv_python = sys.executable
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../scripts/agent_stream.py'))
        agent_process.start(venv_python, [script_path])
        if agent_process.waitForStarted(3000):
            QMessageBox.information(window, 'Agent', 'agent_stream.py started!')
            stop_agent_btn.setEnabled(True)
            run_agent_btn.setEnabled(False)
        else:
            QMessageBox.warning(window, 'Agent', 'Failed to start agent_stream.py')

    def stop_agent_stream():
        if agent_process.state() != QProcess.NotRunning:
            agent_process.terminate()
            if not agent_process.waitForFinished(3000):
                agent_process.kill()
            QMessageBox.information(window, 'Agent', 'agent_stream.py stopped!')
            stop_agent_btn.setEnabled(False)
            run_agent_btn.setEnabled(True)
        else:
            QMessageBox.information(window, 'Agent', 'agent_stream.py is not running.')

    run_agent_btn.clicked.connect(run_agent_stream)
    stop_agent_btn.clicked.connect(stop_agent_stream)

    def on_agent_finished():
        stop_agent_btn.setEnabled(False)
        run_agent_btn.setEnabled(True)
        QMessageBox.information(window, 'Agent', 'agent_stream.py finished.')

    agent_process.finished.connect(on_agent_finished)

    def on_click():
        output = run_hello_world()
        QMessageBox.information(window, 'hello_world.py Output', output)
        output_text.setPlainText(output)

    btn.clicked.connect(on_click)

    def open_text_preview():
        preview_dialog = QDialog(window)
        preview_dialog.setWindowTitle('Markdown Text Preview')
        preview_layout = QVBoxLayout()
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        md_path = os.path.join(os.path.dirname(__file__), '../../data/markdown/masks_of_nyarlathotep.md')
        last_content = {'text': None}

        def load_file():
            try:
                with open(md_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if content != last_content['text']:
                    text_edit.setPlainText(content)
                    last_content['text'] = content
            except Exception as e:
                text_edit.setPlainText(f'Error loading file: {e}')

        # Initial load
        load_file()

        # Set up timer for polling
        timer = QTimer(preview_dialog)
        timer.timeout.connect(load_file)
        timer.start(1000)  # Poll every 1 second

        preview_layout.addWidget(text_edit)
        preview_dialog.setLayout(preview_layout)
        preview_dialog.resize(600, 400)
        preview_dialog.exec_()
        timer.stop()

    preview_btn.clicked.connect(open_text_preview)

    def edit_llm_prompt():
        prompt_dialog = QDialog(window)
        prompt_dialog.setWindowTitle('Edit LLM Prompt')
        prompt_layout = QVBoxLayout()
        prompt_edit = QTextEdit()
        prompt_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../prompts/parse_pdf_text'))
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompt_edit.setPlainText(f.read())
        except Exception as e:
            prompt_edit.setPlainText(f'Error loading prompt: {e}')

        # Prompt templates
        templates = {
            'Clean RPG text': (
                'Act as a text normalization expert. Clean and repair the following PDF-extracted text by performing the following operations...'
            ),
            'Summarize': (
                'Summarize the following text in 3-5 bullet points, focusing on the main plot points and important NPCs.'
            ),
            'Extract NPCs': (
                'Extract a list of all named NPCs from the following text. For each, provide a brief description and any notable traits.'
            ),
        }
        template_combo = QComboBox()
        template_combo.addItem('Select a template...')
        for k in templates:
            template_combo.addItem(k)
        prompt_layout.addWidget(template_combo)
        prompt_layout.addWidget(prompt_edit)
        save_btn = QPushButton('Save')
        prompt_layout.addWidget(save_btn)
        prompt_dialog.setLayout(prompt_layout)
        prompt_dialog.resize(700, 500)

        def on_template_selected(idx):
            if idx <= 0:
                return
            template_name = template_combo.currentText()
            template_text = templates[template_name]
            if prompt_edit.toPlainText().strip() and prompt_edit.toPlainText() != template_text:
                reply = QMessageBox.question(prompt_dialog, 'Overwrite Prompt?', 'Replace current prompt with selected template?', QMessageBox.Yes | QMessageBox.No)
                if reply != QMessageBox.Yes:
                    return
            prompt_edit.setPlainText(template_text)

        template_combo.currentIndexChanged.connect(on_template_selected)

        def save_prompt():
            try:
                with open(prompt_path, 'w', encoding='utf-8') as f:
                    f.write(prompt_edit.toPlainText())
                QMessageBox.information(prompt_dialog, 'Success', 'Prompt saved successfully!')
                prompt_dialog.accept()
            except Exception as e:
                QMessageBox.critical(prompt_dialog, 'Error', f'Failed to save prompt: {e}')

        save_btn.clicked.connect(save_prompt)
        prompt_dialog.exec_()

    edit_prompt_btn.clicked.connect(edit_llm_prompt)

    def reprocess_markdown():
        # Let user select a markdown file
        md_path, _ = QFileDialog.getOpenFileName(window, 'Select Markdown File', os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/markdown')), 'Markdown Files (*.md)')
        if not md_path:
            return
        # Run the reprocess script with QProcess
        reprocess_script = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../scripts/reprocess_markdown_with_llm.py'))
        venv_python = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../venv/bin/python'))
        if not os.path.exists(venv_python):
            venv_python = sys.executable
        process = QProcess(window)
        process.start(venv_python, [reprocess_script, md_path])
        if process.waitForStarted(3000):
            process.waitForFinished(-1)
            if process.exitCode() == 0:
                QMessageBox.information(window, 'Re-process', 'Markdown re-processed with LLM!')
            else:
                QMessageBox.critical(window, 'Re-process', 'Failed to re-process markdown.')
        else:
            QMessageBox.critical(window, 'Re-process', 'Failed to start re-processing script.')

    reprocess_btn.clicked.connect(reprocess_markdown)

    def trim_artefacts():
        # Let user select a markdown file
        md_path, _ = QFileDialog.getOpenFileName(window, 'Select Markdown File', os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/markdown')), 'Markdown Files (*.md)')
        if not md_path:
            return
        # Output path: <original_name>_trimmed.md
        base, ext = os.path.splitext(md_path)
        out_path = base + '_trimmed.md'
        postprocess_script = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../scripts/post_processing.py'))
        venv_python = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../venv/bin/python'))
        if not os.path.exists(venv_python):
            venv_python = sys.executable
        process = QProcess(window)
        process.start(venv_python, [postprocess_script, md_path, out_path])
        if process.waitForStarted(3000):
            process.waitForFinished(-1)
            if process.exitCode() == 0:
                QMessageBox.information(window, 'Trim Artefacts', f'Trimmed artefacts and saved to {out_path}')
            else:
                QMessageBox.critical(window, 'Trim Artefacts', 'Failed to trim artefacts.')
        else:
            QMessageBox.critical(window, 'Trim Artefacts', 'Failed to start post-processing script.')

    trim_btn.clicked.connect(trim_artefacts)

    def open_model_selection():
        selector = ModelSelector()
        selector.test_ollama_connection()
        dialog = QDialog(window)
        dialog.setWindowTitle('Model Selection')
        dlg_layout = QVBoxLayout()
        # Hardware info
        hw = selector.hardware_info
        dlg_layout.addWidget(QLabel(f"Platform: {hw['platform']} | CPU: {hw['cpu']} | RAM: {hw['ram_gb']} GB"))
        dlg_layout.addWidget(QLabel(f"Recommended model: {selector.model_recommendation}"))
        # Backends
        backends = []
        ollama_models = []
        if selector.ollama_installed and selector.ollama_connected:
            ollama_models = selector.list_ollama_models()
            for m in ollama_models:
                backends.append(f"Ollama: {m['name']}")
        if selector.gemini_available:
            backends.append('Gemini (stub)')
        dlg_layout.addWidget(QLabel('Available Backends:'))
        backend_combo = QComboBox()
        backend_combo.addItems(backends)
        dlg_layout.addWidget(backend_combo)
        # Save button
        save_btn = QPushButton('Save Selection')
        dlg_layout.addWidget(save_btn)
        dialog.setLayout(dlg_layout)
        dialog.resize(400, 300)

        def save_selection():
            idx = backend_combo.currentIndex()
            if idx < 0:
                QMessageBox.warning(dialog, 'Model Selection', 'No backend selected.')
                return
            selected = backend_combo.currentText()
            from scripts.model_selector_cli_demo import save_user_selection
            if selected.startswith('Ollama: '):
                model_name = selected.split(': ', 1)[1]
                save_user_selection('ollama', model_name)
            else:
                save_user_selection('gemini')
            QMessageBox.information(dialog, 'Model Selection', f'Selected: {selected}')
            dialog.accept()
            # Optionally reload status label
            check_model_connection()

        save_btn.clicked.connect(save_selection)
        dialog.exec_()

    model_select_btn.clicked.connect(open_model_selection)

    # Load model and API info from config
    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../pipeline_config.yml')), 'r') as f:
        config = yaml.safe_load(f)
    model_name = config['settings']['model']
    ollama_api = config['settings']['ollama_api']

    # Add model connection status label
    status_label = QLabel(f'Model: {model_name} (Checking...)')
    window.layout().addWidget(status_label)

    def check_model_connection():
        try:
            resp = requests.post(ollama_api, json={
                'model': model_name,
                'prompt': 'ping',
                'stream': False
            }, timeout=5)
            if resp.status_code == 200 and 'response' in resp.json():
                status_label.setText(f'Model: {model_name} (Connected)')
            else:
                status_label.setText(f'Model: {model_name} (Not Connected)')
        except Exception:
            status_label.setText(f'Model: {model_name} (Not Connected)')

    check_model_connection()

    def handle_pdf_drop(pdf_path):
        # Copy PDF to data/pdf
        pdf_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/pdf'))
        os.makedirs(pdf_dir, exist_ok=True)
        dest_path = os.path.join(pdf_dir, os.path.basename(pdf_path))
        try:
            shutil.copy2(pdf_path, dest_path)
        except Exception as e:
            QMessageBox.critical(window, 'PDF Pipeline', f'Failed to copy PDF: {e}')
            return
        # Run the pipeline for the copied PDF
        pipeline_script = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../scripts/pdf_process_pipeline.py'))
        venv_python = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../venv/bin/python'))
        if not os.path.exists(venv_python):
            venv_python = sys.executable
        process = QProcess(window)
        process.start(venv_python, [pipeline_script, dest_path])
        if process.waitForStarted(3000):
            process.waitForFinished(-1)
            if process.exitCode() == 0:
                QMessageBox.information(window, 'PDF Pipeline', f'Pipeline completed for {os.path.basename(dest_path)}')
            else:
                QMessageBox.critical(window, 'PDF Pipeline', f'Pipeline failed for {os.path.basename(dest_path)}')
        else:
            QMessageBox.critical(window, 'PDF Pipeline', 'Failed to start pipeline script.')

    window.handle_pdf_drop = handle_pdf_drop

    window.setLayout(window.layout())
    window.resize(400, 300)
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main() 