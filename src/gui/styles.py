DARK_THEME = {
    "window": {
        "background": "#1e1e1e",
        "font": "Segoe UI",
        "font_size": 10
    },
    "primary": {
        "background": "#2d2d30",
        "foreground": "#cccccc",
        "border": "#3e3e42",
        "hover": "#3e3e42",
        "pressed": "#007acc"
    },
    "secondary": {
        "background": "#252526",
        "foreground": "#969696",
        "border": "#3e3e42"
    },
    "accent": {
        "primary": "#007acc",
        "success": "#4caf50",
        "warning": "#ff9800",
        "error": "#f44336",
        "info": "#2196f3"
    },
    "text": {
        "primary": "#ffffff",
        "secondary": "#cccccc",
        "disabled": "#5a5a5a"
    }
}

def get_stylesheet():
    """Retorna stylesheet completo para a aplicação"""
    return f"""
    QMainWindow {{
        background-color: {DARK_THEME["window"]["background"]};
        font-family: {DARK_THEME["window"]["font"]};
        font-size: {DARK_THEME["window"]["font_size"]}pt;
    }}
    
    QWidget {{
        background-color: {DARK_THEME["window"]["background"]};
        color: {DARK_THEME["text"]["secondary"]};
    }}
    
    QPushButton {{
        background-color: {DARK_THEME["primary"]["background"]};
        color: {DARK_THEME["text"]["primary"]};
        border: 1px solid {DARK_THEME["primary"]["border"]};
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: 500;
        min-height: 32px;
    }}
    
    QPushButton:hover {{
        background-color: {DARK_THEME["primary"]["hover"]};
        border-color: {DARK_THEME["accent"]["primary"]};
    }}
    
    QPushButton:pressed {{
        background-color: {DARK_THEME["accent"]["primary"]};
    }}
    
    QPushButton:disabled {{
        background-color: {DARK_THEME["secondary"]["background"]};
        color: {DARK_THEME["text"]["disabled"]};
        border-color: {DARK_THEME["secondary"]["border"]};
    }}
    
    QPushButton#primaryButton {{
        background-color: {DARK_THEME["accent"]["primary"]};
        border: none;
        color: white;
        font-weight: 600;
    }}
    
    QPushButton#primaryButton:hover {{
        background-color: #0098ff;
    }}
    
    QPushButton#primaryButton:disabled {{
        background-color: #004d7a;
    }}
    
    QLineEdit, QTextEdit {{
        background-color: {DARK_THEME["secondary"]["background"]};
        color: {DARK_THEME["text"]["primary"]};
        border: 1px solid {DARK_THEME["primary"]["border"]};
        border-radius: 4px;
        padding: 6px;
    }}
    
    QLineEdit:focus, QTextEdit:focus {{
        border-color: {DARK_THEME["accent"]["primary"]};
        outline: none;
    }}
    
    QProgressBar {{
        background-color: {DARK_THEME["secondary"]["background"]};
        border: 1px solid {DARK_THEME["primary"]["border"]};
        border-radius: 4px;
        text-align: center;
        color: {DARK_THEME["text"]["primary"]};
    }}
    
    QProgressBar::chunk {{
        background-color: {DARK_THEME["accent"]["primary"]};
        border-radius: 3px;
    }}
    
    QLabel {{
        color: {DARK_THEME["text"]["secondary"]};
        background-color: transparent;
    }}
    
    QLabel#titleLabel {{
        color: {DARK_THEME["text"]["primary"]};
        font-size: 16pt;
        font-weight: 600;
    }}
    
    QLabel#subtitleLabel {{
        color: {DARK_THEME["text"]["secondary"]};
        font-size: 10pt;
    }}
    
    QGroupBox {{
        color: {DARK_THEME["text"]["primary"]};
        border: 1px solid {DARK_THEME["primary"]["border"]};
        border-radius: 4px;
        margin-top: 12px;
        padding-top: 12px;
        font-weight: 600;
    }}
    
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px 0 5px;
        background-color: {DARK_THEME["window"]["background"]};
    }}
    
    QListWidget {{
        background-color: {DARK_THEME["secondary"]["background"]};
        color: {DARK_THEME["text"]["primary"]};
        border: 1px solid {DARK_THEME["primary"]["border"]};
        border-radius: 4px;
        padding: 4px;
    }}
    
    QListWidget::item {{
        padding: 4px;
        border-radius: 2px;
    }}
    
    QListWidget::item:selected {{
        background-color: {DARK_THEME["accent"]["primary"]};
        color: white;
    }}
    
    QMessageBox {{
        background-color: {DARK_THEME["window"]["background"]};
        color: {DARK_THEME["text"]["primary"]};
    }}
    """