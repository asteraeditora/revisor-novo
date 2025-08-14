from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QProgressBar, QFrame, QTextEdit)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QPainter, QBrush, QPen, QColor

class FileDropArea(QFrame):
    """Área para arrastar e soltar arquivos"""
    
    fileDropped = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                border: 2px dashed #007acc;
                border-radius: 8px;
                background-color: #252526;
                min-height: 150px;
            }
            QFrame:hover {
                background-color: #2d2d30;
                border-color: #0098ff;
            }
        """)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Ícone
        self.icon_label = QLabel("📄")
        self.icon_label.setStyleSheet("font-size: 48px; background: transparent;")
        self.icon_label.setAlignment(Qt.AlignCenter)
        
        # Texto
        self.text_label = QLabel("Arraste um arquivo .docx aqui\nou clique para selecionar")
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setStyleSheet("background: transparent;")
        
        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_label)
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
            self.setStyleSheet("""
                QFrame {
                    border: 2px solid #0098ff;
                    border-radius: 8px;
                    background-color: #2d2d30;
                }
            """)
        else:
            event.ignore()
    
    def dragLeaveEvent(self, event):
        self.setStyleSheet("""
            QFrame {
                border: 2px dashed #007acc;
                border-radius: 8px;
                background-color: #252526;
            }
        """)
    
    def dropEvent(self, event):
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        if files and files[0].endswith('.docx'):
            self.fileDropped.emit(files[0])
        self.dragLeaveEvent(event)
    
    def set_file(self, filename: str):
        """Atualiza visualização quando arquivo é selecionado"""
        self.icon_label.setText("✅")
        self.text_label.setText(f"Arquivo selecionado:\n{filename}")
        self.setStyleSheet("""
            QFrame {
                border: 2px solid #4caf50;
                border-radius: 8px;
                background-color: #252526;
            }
        """)
    
    def clear_file(self):
        """Limpa seleção de arquivo"""
        self.icon_label.setText("📄")
        self.text_label.setText("Arraste um arquivo .docx aqui\nou clique para selecionar")
        self.setStyleSheet("""
            QFrame {
                border: 2px dashed #007acc;
                border-radius: 8px;
                background-color: #252526;
            }
        """)

class AnimatedProgressBar(QProgressBar):
    """Barra de progresso animada"""
    
    def __init__(self):
        super().__init__()
        self.setTextVisible(True)
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._animate)
        self._animation_step = 0
        self._base_style = """
            QProgressBar {
                background-color: #252526;
                border: 1px solid #3e3e42;
                border-radius: 4px;
                text-align: center;
                color: #ffffff;
            }
            QProgressBar::chunk {
                background-color: #007acc;
                border-radius: 3px;
            }
        """
        self.setStyleSheet(self._base_style)
    
    def start_animation(self):
        """Inicia animação de progresso indeterminado"""
        self.animation_timer.start(100)
    
    def stop_animation(self):
        """Para animação"""
        self.animation_timer.stop()
        self.setStyleSheet(self._base_style)
    
    def _animate(self):
        """Anima a barra de progresso"""
        if self.value() == 0:
            # Modo indeterminado - animação simples de pulso
            self._animation_step = (self._animation_step + 5) % 100
            
            # Alterna entre cores para criar efeito de pulso
            if self._animation_step < 50:
                color = "#007acc"
            else:
                color = "#0098ff"
            
            style = f"""
            QProgressBar {{
                background-color: #252526;
                border: 1px solid #3e3e42;
                border-radius: 4px;
                text-align: center;
                color: #ffffff;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 3px;
            }}
            """
            self.setStyleSheet(style)

class StatusWidget(QWidget):
    """Widget para mostrar status da operação"""
    
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
        # Ícone de status
        self.status_icon = QLabel()
        self.status_icon.setFixedSize(20, 20)
        
        # Texto de status
        self.status_text = QLabel("Pronto")
        
        # Tempo decorrido
        self.time_label = QLabel()
        
        layout.addWidget(self.status_icon)
        layout.addWidget(self.status_text)
        layout.addStretch()
        layout.addWidget(self.time_label)
        
        self.set_ready()
    
    def set_ready(self):
        """Define status como pronto"""
        self.status_icon.setText("✅")
        self.status_text.setText("Pronto")
        self.time_label.clear()
    
    def set_processing(self, text: str = "Processando..."):
        """Define status como processando"""
        self.status_icon.setText("⏳")
        self.status_text.setText(text)
    
    def set_success(self, text: str = "Concluído"):
        """Define status como sucesso"""
        self.status_icon.setText("✅")
        self.status_text.setText(text)
    
    def set_error(self, text: str = "Erro"):
        """Define status como erro"""
        self.status_icon.setText("❌")
        self.status_text.setText(text)
    
    def set_time(self, seconds: int):
        """Atualiza tempo decorrido"""
        minutes = seconds // 60
        secs = seconds % 60
        self.time_label.setText(f"Tempo: {minutes:02d}:{secs:02d}")

class APIKeyDialog(QWidget):
    """Diálogo para inserir chave da API"""
    
    keySubmitted = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configurar API Key")
        self.setFixedSize(400, 200)
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #cccccc;
            }
            QTextEdit {
                background-color: #252526;
                color: #ffffff;
                border: 1px solid #3e3e42;
                border-radius: 4px;
                padding: 6px;
            }
            QPushButton {
                background-color: #2d2d30;
                color: #ffffff;
                border: 1px solid #3e3e42;
                border-radius: 4px;
                padding: 8px 16px;
                min-height: 32px;
            }
            QPushButton:hover {
                background-color: #3e3e42;
                border-color: #007acc;
            }
            QPushButton#primaryButton {
                background-color: #007acc;
                border: none;
            }
            QPushButton#primaryButton:hover {
                background-color: #0098ff;
            }
        """)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Título
        title = QLabel("Configure sua chave da API OpenAI")
        title.setStyleSheet("font-size: 14pt; font-weight: bold; color: #ffffff;")
        layout.addWidget(title)
        
        # Descrição
        desc = QLabel("Insira sua chave da API para começar a usar o revisor:")
        layout.addWidget(desc)
        
        # Campo de entrada
        self.key_input = QTextEdit()
        self.key_input.setPlaceholderText("sk-...")
        self.key_input.setMaximumHeight(60)
        layout.addWidget(self.key_input)
        
        # Botões
        btn_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("Salvar")
        self.save_btn.clicked.connect(self._on_save)
        self.save_btn.setObjectName("primaryButton")
        
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.clicked.connect(self.close)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)
        
        layout.addLayout(btn_layout)
    
    def _on_save(self):
        key = self.key_input.toPlainText().strip()
        if key:
            self.keySubmitted.emit(key)
            self.close()