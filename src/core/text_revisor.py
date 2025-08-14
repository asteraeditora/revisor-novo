import re
from typing import List, Tuple

class TextRevisor:
    """Classe para lógica de revisão de texto"""
    
    @staticmethod
    def prepare_text_for_revision(text: str) -> Tuple[str, dict]:
        """Prepara texto para revisão, preservando elementos especiais"""
        preserved_elements = {}
        counter = 0
        
        # Preserva URLs
        url_pattern = r'(https?://[^\s]+)'
        for match in re.finditer(url_pattern, text):
            placeholder = f"__URL_{counter}__"
            preserved_elements[placeholder] = match.group(0)
            text = text.replace(match.group(0), placeholder)
            counter += 1
        
        # Preserva marcações especiais
        markup_pattern = r'(\[[^\]]+\])'
        for match in re.finditer(markup_pattern, text):
            placeholder = f"__MARKUP_{counter}__"
            preserved_elements[placeholder] = match.group(0)
            text = text.replace(match.group(0), placeholder)
            counter += 1
        
        # Preserva e-mails
        email_pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        for match in re.finditer(email_pattern, text):
            placeholder = f"__EMAIL_{counter}__"
            preserved_elements[placeholder] = match.group(0)
            text = text.replace(match.group(0), placeholder)
            counter += 1
        
        return text, preserved_elements
    
    @staticmethod
    def restore_preserved_elements(text: str, preserved_elements: dict) -> str:
        """Restaura elementos preservados após revisão"""
        for placeholder, original in preserved_elements.items():
            text = text.replace(placeholder, original)
        return text
    
    @staticmethod
    def validate_revision(original: str, revised: str) -> bool:
        """Valida se a revisão manteve a estrutura essencial"""
        # Verifica se manteve marcações especiais
        original_markups = re.findall(r'\[[^\]]+\]', original)
        revised_markups = re.findall(r'\[[^\]]+\]', revised)
        
        if set(original_markups) != set(revised_markups):
            return False
        
        # Verifica se manteve URLs
        original_urls = re.findall(r'https?://[^\s]+', original)
        revised_urls = re.findall(r'https?://[^\s]+', revised)
        
        if set(original_urls) != set(revised_urls):
            return False
        
        # Verifica se não houve mudança drástica no tamanho
        len_ratio = len(revised) / len(original) if len(original) > 0 else 1
        if len_ratio < 0.7 or len_ratio > 1.3:  # Tolerância de 30%
            return False
        
        return True
    
    @staticmethod
    def handle_multiple_choice_questions(text: str) -> Tuple[str, List[str]]:
        """Identifica e separa questões de múltipla escolha"""
        # Padrões comuns de questões
        patterns = [
            r'^[a-eA-E]\)',  # a) b) c) etc.
            r'^[a-eA-E]\.',  # a. b. c. etc.
            r'^\([a-eA-E]\)',  # (a) (b) (c) etc.
            r'^[1-5]\)',  # 1) 2) 3) etc.
            r'^[1-5]\.',  # 1. 2. 3. etc.
        ]
        
        lines = text.split('\n')
        question_lines = []
        options = []
        
        in_options = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Verifica se é uma opção
            is_option = False
            for pattern in patterns:
                if re.match(pattern, line):
                    is_option = True
                    in_options = True
                    break
            
            if is_option:
                options.append(line)
            else:
                if in_options:
                    # Terminou as opções
                    in_options = False
                question_lines.append(line)
        
        question_text = '\n'.join(question_lines)
        
        return question_text, options