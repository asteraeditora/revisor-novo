import sys
import os
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# Adiciona diretório pai ao path para permitir imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.gui.main_window import MainWindow
from src.utils.config import Config

def setup_logging():
    """Configura sistema de logging"""
    config = Config()
    log_dir = config.OUTPUT_PATHS.get("logs", "output/logs")
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, "word_revisor.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def main():
    """Função principal"""
    # Configura DPI awareness para Windows
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Configura logging
    setup_logging()
    
    # Cria aplicação
    app = QApplication(sys.argv)
    app.setApplicationName("Word Revisor")
    app.setOrganizationName("WordRevisor")
    
    # Cria e mostra janela principal
    window = MainWindow()
    window.show()
    
    # Executa aplicação
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()