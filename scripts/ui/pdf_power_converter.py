import sys
import os
import subprocess
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox, QTextEdit, QDialog, QFileDialog, QComboBox, QListWidget, QListWidgetItem, QGroupBox
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtCore import QTimer, QProcess, QUrl
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


class PDFDropListWidget(QListWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setAcceptDrops(True)
        self.setDragDropMode(QListWidget.NoDragDrop)
        self.refresh_pdf_list()

    def refresh_pdf_list(self):
        self.clear()
        pdf_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/pdf'))
        if not os.path.exists(pdf_dir):
            os.makedirs(pdf_dir, exist_ok=True)
        for fname in os.listdir(pdf_dir):
            if fname.lower().endswith('.pdf'):
                self.addItem(QListWidgetItem(fname))

    def dragEnterEvent(self, event):
        if event is not None:
            mime = event.mimeData()
            if mime and mime.hasUrls():
                for url in mime.urls():
                    if url.toLocalFile().lower().endswith('.pdf'):
                        event.acceptProposedAction()
                        return
            event.ignore()

    def dropEvent(self, event):
        if event is not None:
            mime = event.mimeData()
            if mime and mime.hasUrls():
                for url in mime.urls():
                    file_path = url.toLocalFile()
                    if file_path.lower().endswith('.pdf'):
                        self.main_window.handle_pdf_drop(file_path)


def main():
    app = QApplication(sys.argv)
    main_window = QWidget()
    main_window.setWindowTitle('PDF Power Converter')
    icon_path = os.path.join(os.path.dirname(__file__), 'icons', 'app_icon.png')
    if os.path.exists(icon_path):
        main_window.setWindowIcon(QIcon(icon_path))

    # Main layout: horizontal split
    main_layout = QHBoxLayout()
    main_window.setLayout(main_layout)

    # Left panel: PDF list, drag-and-drop, open folder, logs
    left_panel = QWidget()
    left_layout = QVBoxLayout()
    left_panel.setLayout(left_layout)
    pdf_list = PDFDropListWidget(main_window=main_window, parent=main_window)
    left_layout.addWidget(QLabel('PDFs'))
    left_layout.addWidget(pdf_list)
    open_folder_btn = QPushButton('Open Output Folder')
    left_layout.addWidget(open_folder_btn)
    log_label = QLabel('Console Logs:')
    left_layout.addWidget(log_label)
    log_text = QTextEdit()
    log_text.setReadOnly(True)
    left_layout.addWidget(log_text)
    left_layout.setStretchFactor(log_text, 2)
    main_layout.addWidget(left_panel, 1)

    # Right panel: existing controls
    right_panel = QWidget()
    right_layout = QVBoxLayout()
    right_panel.setLayout(right_layout)
    main_layout.addWidget(right_panel, 2)

    # Move all existing controls to right_layout instead of window.layout()
    label = QLabel('Test llm status')
    right_layout.addWidget(label)
    btn = QPushButton('Run hello_world.py')
    right_layout.addWidget(btn)
    btn_stream = QPushButton('Run Stream')
    right_layout.addWidget(btn_stream)
    btn_bob = QPushButton('Run bob')
    right_layout.addWidget(btn_bob)
    model_select_btn = QPushButton('Model Selection')
    right_layout.addWidget(model_select_btn)
    label = QLabel('Run operations on your files')
    edit_prompt_btn = QPushButton('Edit LLM Prompt')
    right_layout.addWidget(edit_prompt_btn)
    run_agent_btn = QPushButton('Process all PDFs')
    right_layout.addWidget(run_agent_btn)
    stop_agent_btn = QPushButton('Stop agent_stream.py')
    stop_agent_btn.setEnabled(False)
    right_layout.addWidget(stop_agent_btn)
    reprocess_btn = QPushButton('Re-process Markdown with LLM')
    right_layout.addWidget(reprocess_btn)
    trim_btn = QPushButton('Trim Artefacts (Post-process)')
    right_layout.addWidget(trim_btn)
    preview_btn = QPushButton('Open Text Preview')
    right_layout.addWidget(preview_btn)
    # Model status label
    status_label = QLabel('')
    right_layout.addWidget(status_label)
    right_layout.addStretch(1)

    agent_process = QProcess(main_window)

    def run_click_stream():
        venv_python = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../venv/bin/python'))
        if not os.path.exists(venv_python):
            venv_python = sys.executable
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../scripts/tests/example_stream.py'))
        agent_process.start(venv_python, [script_path])
        if agent_process.waitForStarted(3000):
            add_logs('example_stream.py started!')
        else:
            add_logs('Failed to start example_stream.py')
    btn_stream.clicked.connect(run_click_stream)


    def read_agent_output():
        output = agent_process.readAllStandardOutput().data().decode()
        if output:
            add_logs(output)
        error = agent_process.readAllStandardError().data().decode()
        if error:
            add_logs(f"[stderr] {error}")

    def run_agent_stream():
        add_logs("starting run_agent_stream()")
        venv_python = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../venv/bin/python'))
        if not os.path.exists(venv_python):
            venv_python = sys.executable
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../scripts/agent_stream.py'))
        agent_process.start(venv_python, [script_path])
        if agent_process.waitForStarted(3000):
            add_logs('agent_stream.py started!')
            stop_agent_btn.setEnabled(True)
            run_agent_btn.setEnabled(False)
        else:
            add_logs("Failed to start agent_stream.py")

    def stop_agent_stream():
        if agent_process.state() != QProcess.ProcessState.NotRunning:
            agent_process.terminate()
            if not agent_process.waitForFinished(3000):
                agent_process.kill()
            QMessageBox.information(main_window, 'Agent', 'agent_stream.py stopped!')
            stop_agent_btn.setEnabled(False)
            run_agent_btn.setEnabled(True)
        else:
            QMessageBox.information(main_window, 'Agent', 'agent_stream.py is not running.')

    run_agent_btn.clicked.connect(run_agent_stream)
    stop_agent_btn.clicked.connect(stop_agent_stream)

    def on_agent_finished():
        stop_agent_btn.setEnabled(False)
        run_agent_btn.setEnabled(True)
  #     QMessageBox.information(main_window, 'Agent', 'agent_stream.py finished.')

    agent_process.finished.connect(on_agent_finished)
    agent_process.readyReadStandardOutput.connect(read_agent_output)
    agent_process.readyReadStandardError.connect(read_agent_output)

    def on_click_hello():
        output = run_hello_world()
        # QMessageBox.information(main_window, 'hello_world.py Output', output)
        add_logs(output)
    def on_click_bob():
        output = "Hi Bob"
        # QMessageBox.information(main_window, 'hello_world.py Output', output)
        add_logs(output)

    def new_logs(txt):
        log_text.setPlainText(txt)
    def add_logs(txt):
        log_text.append(txt)

    btn.clicked.connect(on_click_hello)
    btn_bob.clicked.connect(on_click_bob)

    def open_text_preview():
        preview_dialog = QDialog(main_window)
        preview_dialog.setWindowTitle('Markdown Text Preview')
        preview_layout = QVBoxLayout()
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        md_path = os.path.join(os.path.dirname(__file__), '../../data/markdown/masks_of_nyarlathotep.md')
        last_content = {'text': ''}

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
        prompt_dialog = QDialog(main_window)
        prompt_dialog.setWindowTitle('Edit LLM Prompt')
        prompt_layout = QVBoxLayout()
        prompt_edit = QTextEdit()
        prompt_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../prompts/parse_pdf_text'))
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompt_edit.setPlainText(f.read())
        except Exception as e:
            prompt_edit.setPlainText(f'Error loading prompt: {e}')

        # Prompt templates: dynamically load from prompts folder
        prompts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../prompts'))
        template_files = [f for f in os.listdir(prompts_dir) if os.path.isfile(os.path.join(prompts_dir, f)) and not f.startswith('.')]
        templates = {}
        for fname in template_files:
            fpath = os.path.join(prompts_dir, fname)
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    templates[fname] = f.read()
            except Exception as e:
                templates[fname] = f'[Error loading {fname}: {e}]'
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
        md_path, _ = QFileDialog.getOpenFileName(main_window, 'Select Markdown File', os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/markdown')), 'Markdown Files (*.md)')
        if not md_path:
            return
        # Run the reprocess script with QProcess
        reprocess_script = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../scripts/reprocess_markdown_with_llm.py'))
        venv_python = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../venv/bin/python'))
        if not os.path.exists(venv_python):
            venv_python = sys.executable
        process = QProcess(main_window)
        process.start(venv_python, [reprocess_script, md_path])
        if process.waitForStarted(3000):
            process.waitForFinished(-1)
            if process.exitCode() == 0:
                QMessageBox.information(main_window, 'Re-process', 'Markdown re-processed with LLM!')
            else:
                QMessageBox.critical(main_window, 'Re-process', 'Failed to re-process markdown.')
        else:
            QMessageBox.critical(main_window, 'Re-process', 'Failed to start re-processing script.')

    reprocess_btn.clicked.connect(reprocess_markdown)

    def trim_artefacts():
        # Let user select a markdown file
        md_path, _ = QFileDialog.getOpenFileName(main_window, 'Select Markdown File', os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/markdown')), 'Markdown Files (*.md)')
        if not md_path:
            return
        # Output path: <original_name>_trimmed.md
        base, ext = os.path.splitext(md_path)
        out_path = base + '_trimmed.md'
        postprocess_script = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../scripts/post_processing.py'))
        venv_python = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../venv/bin/python'))
        if not os.path.exists(venv_python):
            venv_python = sys.executable
        process = QProcess(main_window)
        process.start(venv_python, [postprocess_script, md_path, out_path])
        if process.waitForStarted(3000):
            process.waitForFinished(-1)
            if process.exitCode() == 0:
                QMessageBox.information(main_window, 'Trim Artefacts', f'Trimmed artefacts and saved to {out_path}')
            else:
                QMessageBox.critical(main_window, 'Trim Artefacts', 'Failed to trim artefacts.')
        else:
            QMessageBox.critical(main_window, 'Trim Artefacts', 'Failed to start post-processing script.')

    trim_btn.clicked.connect(trim_artefacts)

    def open_model_selection():
        selector = ModelSelector()
        selector.test_ollama_connection()
        dialog = QDialog(main_window)
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
    status_label.setText(f'Model: {model_name} (Checking...)')

    def handle_pdf_drop(pdf_path):
        # Copy PDF to data/pdf
        add_logs(f'running handle_pdf_drop')
        pdf_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/pdf'))
        os.makedirs(pdf_dir, exist_ok=True)
        dest_path = os.path.join(pdf_dir, os.path.basename(pdf_path))
        try:
            shutil.copy2(pdf_path, dest_path)
            add_logs(f'Copied PDF: {os.path.basename(pdf_path)}')
        except Exception as e:
            QMessageBox.critical(main_window, 'PDF Pipeline', f'Failed to copy PDF: {e}')
            log_text.append(f'Failed to copy PDF: {e}')
            return
        pdf_list.refresh_pdf_list()
        # Run the pipeline for the copied PDF
        pipeline_script = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../scripts/pdf_process_pipeline.py'))
        venv_python = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../venv/bin/python'))
        if not os.path.exists(venv_python):
            venv_python = sys.executable
        process = QProcess(main_window)
        process.start(venv_python, [pipeline_script, dest_path])
        if process.waitForStarted(3000):
            process.waitForFinished(-1)
            if process.exitCode() == 0:
                QMessageBox.information(main_window, 'PDF Pipeline', f'Pipeline completed for {os.path.basename(dest_path)}')
                log_text.append(f'Pipeline completed for {os.path.basename(dest_path)}')
            else:
                QMessageBox.critical(main_window, 'PDF Pipeline', f'Pipeline failed for {os.path.basename(dest_path)}')
                log_text.append(f'Pipeline failed for {os.path.basename(dest_path)}')
        else:
            QMessageBox.critical(main_window, 'PDF Pipeline', 'Failed to start pipeline script.')
            log_text.append('Failed to start pipeline script.')

    main_window.handle_pdf_drop = handle_pdf_drop

    # Open output folder button logic
    def open_output_folder():
        # Open both markdown and json output folders
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data'))
        # On macOS, open both folders in Finder; on Windows, open in Explorer; on Linux, open in default file manager
        for subfolder in ['markdown', 'json']:
          # folder = os.path.join(base_dir, subfolder)
            folder = subfolder
            if os.path.exists(folder):
                QDesktopServices.openUrl(QUrl.fromLocalFile(folder))
            else:
                log_text.append(f'Output folder not found: {folder}')
    open_folder_btn.clicked.connect(open_output_folder)

    def preprocess_all_pdfs():
        add_logs('Starting preprocessing of all PDFs...')
        pdf_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/pdf'))
        venv_python = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../venv/bin/python'))
        if not os.path.exists(venv_python):
            venv_python = sys.executable
        pipeline_script = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../scripts/pdf_process_pipeline.py'))
        pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]
        if not pdf_files:
            add_logs('No PDFs found in input directory.')
            return
        # Use a list to queue PDFs
        preprocess_all_pdfs.pdf_queue = [os.path.join(pdf_dir, f) for f in pdf_files]
        preprocess_all_pdfs.venv_python = venv_python
        preprocess_all_pdfs.pipeline_script = pipeline_script
        preprocess_all_pdfs.process = QProcess(main_window)
        def process_next_pdf():
            if not preprocess_all_pdfs.pdf_queue:
                add_logs('All PDFs processed.')
                return
            pdf_path = preprocess_all_pdfs.pdf_queue.pop(0)
            fname = os.path.basename(pdf_path)
            add_logs(f'Processing {fname}...')
            p = preprocess_all_pdfs.process
            p.finished.disconnect() if p.receivers(p.finished) else None
            def on_finished(exitCode, exitStatus):
                if exitCode == 0:
                    add_logs(f'✅ Preprocessing complete for {fname}')
                else:
                    add_logs(f'❌ Preprocessing failed for {fname}')
                process_next_pdf()
            p.finished.connect(on_finished)
            p.start(preprocess_all_pdfs.venv_python, [preprocess_all_pdfs.pipeline_script, pdf_path])
        process_next_pdf()

    run_agent_btn.clicked.disconnect()
    run_agent_btn.clicked.connect(preprocess_all_pdfs)

    # --- Model & LLM Controls Group ---
    model_group = QGroupBox('Model & LLM Controls')
    model_layout = QVBoxLayout()
    model_group.setLayout(model_layout)
    model_layout.addWidget(QLabel('Test llm status'))
    model_layout.addWidget(model_select_btn)
    model_layout.addWidget(edit_prompt_btn)
    model_layout.addWidget(status_label)
    right_layout.addWidget(model_group)

    # --- PDF Processing Group ---
    pdf_group = QGroupBox('PDF Processing')
    pdf_layout = QVBoxLayout()
    pdf_group.setLayout(pdf_layout)
    pdf_layout.addWidget(QLabel('Run operations on your files'))
    pdf_layout.addWidget(run_agent_btn)
    pdf_layout.addWidget(reprocess_btn)
    pdf_layout.addWidget(trim_btn)
    pdf_layout.addWidget(preview_btn)
    right_layout.addWidget(pdf_group)

    # --- Miscellaneous/Testing Group ---
    misc_group = QGroupBox('Miscellaneous / Testing')
    misc_layout = QVBoxLayout()
    misc_group.setLayout(misc_layout)
    misc_layout.addWidget(btn)
    misc_layout.addWidget(btn_stream)
    misc_layout.addWidget(btn_bob)
    right_layout.addWidget(misc_group)

    right_layout.addWidget(stop_agent_btn)
    right_layout.addStretch(1)

    main_window.resize(900, 600)
    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main() 