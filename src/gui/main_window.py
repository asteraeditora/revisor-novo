import os
import logging
from datetime import datetime
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QPushButton, QLabel, QFileDialog, QMessageBox,
                            QGroupBox, QListWidget, QListWidgetItem, QSplitter,
                            )
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon

from .widgets import FileDropArea, AnimatedProgressBar, StatusWidget, APIKeyDialog
from ..core.smart_document_processor import SmartDocumentProcessor
from ..utils.api_client import OpenAIClient
from .styles import get_stylesheet


from ..core.document_comparer import DocumentComparer
from ..utils.config import Config

class ProcessingThread(QThread):
    """Thread para processamento em background"""
    
    progress = pyqtSignal(int, int, str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, processor, input_path, output_path):
        super().__init__()
        self.processor = processor
        self.input_path = input_path
        self.output_path = output_path
    
    def run(self):
        try:
            def callback(current, total, status):
                self.progress.emit(current, total, status)
            
            result = self.processor.process_document(
                self.input_path, 
                self.output_path,
                callback
            )
            
            self.finished.emit(result)
            
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    """Janela principal da aplicação"""
    
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.processor = None
        self.current_file = None
        self.processing_thread = None
        self.elapsed_timer = QTimer()
        self.elapsed_seconds = 0
        
        self._init_ui()
        self._check_api_key()
        
    def _init_ui(self):
        """Inicializa interface"""
        self.setWindowTitle("Revisor de Documentos Word")
        self.setMinimumSize(1000, 700)
        
        # Aplica tema
        self.setStyleSheet(get_stylesheet())
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Cabeçalho
        header_layout = QHBoxLayout()
        
        title = QLabel("Revisor de Documentos Word")
        title.setObjectName("titleLabel")
        
        subtitle = QLabel("Correção gramatical inteligente com preservação de formatação")
        subtitle.setObjectName("subtitleLabel")
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        header_layout.addStretch()
        
        # Botão de configurações
        config_btn = QPushButton("⚙️ Configurações")
        config_btn.clicked.connect(self._show_config)
        header_layout.addWidget(config_btn)
        
        main_layout.addLayout(header_layout)
        
        # Área principal com splitter
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Painel esquerdo - Upload e controles
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        
        # Área de upload
        upload_group = QGroupBox("Documento")
        upload_layout = QVBoxLayout()
        
        self.drop_area = FileDropArea()
        self.drop_area.fileDropped.connect(self._load_file)
        upload_layout.addWidget(self.drop_area)
        
        # Botões de arquivo
        file_btn_layout = QHBoxLayout()
        
        select_btn = QPushButton("Selecionar Arquivo")
        select_btn.clicked.connect(self._select_file)
        
        clear_btn = QPushButton("Limpar")
        clear_btn.clicked.connect(self._clear_file)
        
        file_btn_layout.addWidget(select_btn)
        file_btn_layout.addWidget(clear_btn)
        upload_layout.addLayout(file_btn_layout)
        
        upload_group.setLayout(upload_layout)
        left_layout.addWidget(upload_group)
        
        # Controles de processamento
        process_group = QGroupBox("Processamento")
        process_layout = QVBoxLayout()
        
        # Barra de progresso
        self.progress_bar = AnimatedProgressBar()
        process_layout.addWidget(self.progress_bar)
        
        # Status
        self.status_widget = StatusWidget()
        process_layout.addWidget(self.status_widget)
        
        # Botão processar
        self.process_btn = QPushButton("▶️ Iniciar Revisão")
        self.process_btn.setObjectName("primaryButton")
        self.process_btn.clicked.connect(self._start_processing)
        self.process_btn.setEnabled(False)
        process_layout.addWidget(self.process_btn)
        
        process_group.setLayout(process_layout)
        left_layout.addWidget(process_group)
        
        left_layout.addStretch()

        
        
        # Painel direito - Histórico
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)
        
        history_group = QGroupBox("Histórico de Revisões")
        history_layout = QVBoxLayout()
        
        self.history_list = QListWidget()
        self.history_list.itemDoubleClicked.connect(self._open_result)
        history_layout.addWidget(self.history_list)
        
        # Botões do histórico
        history_btn_layout = QHBoxLayout()
        
        open_btn = QPushButton("Abrir")
        open_btn.clicked.connect(self._open_selected)
        
        compare_btn = QPushButton("Ver Comparação")
        compare_btn.clicked.connect(self._open_comparison)
        
        history_btn_layout.addWidget(open_btn)
        history_btn_layout.addWidget(compare_btn)
        history_btn_layout.addStretch()
        
        history_layout.addLayout(history_btn_layout)
        
        history_group.setLayout(history_layout)
        right_layout.addWidget(history_group)
        
        # Adiciona painéis ao splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([600, 400])
        
        # Timer para tempo decorrido
        self.elapsed_timer.timeout.connect(self._update_elapsed_time)
        
        # Carrega histórico
        self._load_history()
    
    def _check_api_key(self):
        """Verifica se a API key está configurada"""
        if not self.config.API_KEY:
            self._show_api_key_dialog()
        else:
            self._init_processor()
    
    def _init_processor(self):
        """Inicializa processador com API key"""
        if self.config.API_KEY:
            # Cria cliente API primeiro
            api_client = OpenAIClient(self.config.API_KEY, self.config.MODEL)
            # Cria processador smart com modo padrão
            self.processor = SmartDocumentProcessor(api_client, mode="editorial")
    
    def _show_api_key_dialog(self):
        """Mostra diálogo para configurar API key"""
        dialog = APIKeyDialog()
        dialog.keySubmitted.connect(self._save_api_key)
        dialog.show()
    
    def _save_api_key(self, key: str):
        """Salva API key"""
        self.config.update_api_key(key)
        self._init_processor()
        QMessageBox.information(self, "Sucesso", "API Key configurada com sucesso!")
    
    def _show_config(self):
        """Mostra configurações"""
        self._show_api_key_dialog()
    
    def _select_file(self):
        """Seleciona arquivo via diálogo"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar Documento Word",
            "",
            "Documentos Word (*.docx)"
        )
        
        if file_path:
            self._load_file(file_path)
    
    def _load_file(self, file_path: str):
        """Carrega arquivo selecionado"""
        if not file_path.endswith('.docx'):
            QMessageBox.warning(
                self,
                "Arquivo Inválido",
                "Por favor, selecione um arquivo .docx"
            )
            return
        
        self.current_file = file_path
        filename = os.path.basename(file_path)
        self.drop_area.set_file(filename)
        self.process_btn.setEnabled(True)
        self.status_widget.set_ready()
    
    def _clear_file(self):
        """Limpa arquivo selecionado"""
        self.current_file = None
        self.drop_area.clear_file()
        self.process_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_widget.set_ready()
    
    def _start_processing(self):
        """Inicia processamento do documento"""
        if not self.current_file:
            return
        
        if not self.processor:
            QMessageBox.warning(
                self,
                "API Key Necessária",
                "Por favor, configure sua API Key primeiro."
            )
            self._show_api_key_dialog()
            return
        
        # Prepara caminhos de saída
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.splitext(os.path.basename(self.current_file))[0]
        
        output_name = f"{base_name}_revisado_{timestamp}.docx"
        output_path = os.path.join(self.config.OUTPUT_PATHS["revised"], output_name)
        
        # Garante que diretório existe
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Desabilita controles
        self.process_btn.setEnabled(False)
        self.drop_area.setEnabled(False)
        
        # Inicia animações
        self.progress_bar.setValue(0)
        self.progress_bar.start_animation()
        self.status_widget.set_processing("Iniciando revisão...")
        
        # Inicia timer
        self.elapsed_seconds = 0
        self.elapsed_timer.start(1000)
        
        # Cria e inicia thread
        self.processing_thread = ProcessingThread(
            self.processor,
            self.current_file,
            output_path
        )
        
        self.processing_thread.progress.connect(self._update_progress)
        self.processing_thread.finished.connect(self._processing_finished)
        self.processing_thread.error.connect(self._processing_error)
        
        self.processing_thread.start()
    
    def _update_progress(self, current: int, total: int, status: str):
        """Atualiza progresso"""
        if total > 0:
            percent = int((current / total) * 100)
            self.progress_bar.setValue(percent)
            self.progress_bar.stop_animation()
        
        self.status_widget.set_processing(f"{status} ({current}/{total})")
    
    def _update_elapsed_time(self):
        """Atualiza tempo decorrido"""
        self.elapsed_seconds += 1
        self.status_widget.set_time(self.elapsed_seconds)
    
    def _processing_finished(self, output_path: str):
        """Processamento concluído com sucesso"""
        self.elapsed_timer.stop()
        self.progress_bar.setValue(100)
        self.progress_bar.stop_animation()
        self.status_widget.set_success("Revisão concluída!")
        
        # Reabilita controles
        self.process_btn.setEnabled(True)
        self.drop_area.setEnabled(True)
        
        # Gera comparação
        self._generate_comparison(self.current_file, output_path)
        
        # Atualiza histórico
        self._add_to_history(self.current_file, output_path)
        
        # Pergunta se quer abrir
        reply = QMessageBox.question(
            self,
            "Revisão Concluída",
            "Documento revisado com sucesso!\nDeseja abrir o resultado?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            os.startfile(output_path)
    
    def _processing_error(self, error_msg: str):
        """Erro durante processamento"""
        self.elapsed_timer.stop()
        self.progress_bar.stop_animation()
        self.status_widget.set_error("Erro no processamento")
        
        # Reabilita controles
        self.process_btn.setEnabled(True)
        self.drop_area.setEnabled(True)
        
        # Log do erro
        logging.error(f"Erro no processamento: {error_msg}")
        
        # Mostra erro
        QMessageBox.critical(
            self,
            "Erro",
            f"Ocorreu um erro durante o processamento:\n\n{error_msg}"
        )
    
    def _generate_comparison(self, original_path: str, revised_path: str):
        """Gera documento de comparação"""
        try:
            comparer = DocumentComparer()
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = os.path.splitext(os.path.basename(original_path))[0]
            
            comparison_name = f"{base_name}_comparacao_{timestamp}.docx"
            comparison_path = os.path.join(
                self.config.OUTPUT_PATHS["comparisons"], 
                comparison_name
            )
            
            comparer.compare_documents(original_path, revised_path, comparison_path)
            
        except Exception as e:
            logging.error(f"Erro ao gerar comparação: {str(e)}")
    
    def _add_to_history(self, original_path: str, revised_path: str):
        """Adiciona item ao histórico"""
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
        filename = os.path.basename(original_path)
        
        item = QListWidgetItem(f"{filename} - {timestamp}")
        item.setData(Qt.UserRole, {
            'original': original_path,
            'revised': revised_path,
            'timestamp': timestamp
        })
        
        self.history_list.insertItem(0, item)
        
        # Salva histórico
        self._save_history()
    
    def _load_history(self):
        """Carrega histórico de revisões"""
        # Por enquanto, apenas lista arquivos na pasta de saída
        revised_dir = self.config.OUTPUT_PATHS["revised"]
        
        if os.path.exists(revised_dir):
            for file in sorted(os.listdir(revised_dir), reverse=True)[:20]:
                if file.endswith('.docx'):
                    item = QListWidgetItem(file)
                    item.setData(Qt.UserRole, {
                        'revised': os.path.join(revised_dir, file)
                    })
                    self.history_list.addItem(item)
    
    def _save_history(self):
        """Salva histórico (implementar persistência futura)"""
        pass
    
    def _open_selected(self):
        """Abre documento selecionado no histórico"""
        current = self.history_list.currentItem()
        if current:
            data = current.data(Qt.UserRole)
            if 'revised' in data:
                os.startfile(data['revised'])
    
    def _open_result(self, item):
        """Abre resultado com duplo clique"""
        data = item.data(Qt.UserRole)
        if 'revised' in data:
            os.startfile(data['revised'])
    
    def _open_comparison(self):
        """Abre documento de comparação"""
        current = self.history_list.currentItem()
        if current:
            data = current.data(Qt.UserRole)
            if 'revised' in data:
                # Tenta encontrar arquivo de comparação correspondente
                revised_name = os.path.basename(data['revised'])
                base_name = revised_name.replace('_revisado_', '_comparacao_')
                
                comparison_path = os.path.join(
                    self.config.OUTPUT_PATHS["comparisons"],
                    base_name
                )
                
                if os.path.exists(comparison_path):
                    os.startfile(comparison_path)
                else:
                    QMessageBox.information(
                        self,
                        "Comparação não encontrada",
                        "Arquivo de comparação não foi encontrado."
                    )