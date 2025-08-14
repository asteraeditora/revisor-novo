import os
import time
import logging
import json
import shutil
from typing import List, Dict, Tuple
from docx import Document
from .modular_prompt_system import ModularPromptSystem, PromptModule

class SmartDocumentProcessor:
    """Processador com segmentação inteligente e prompts modulares"""
    
    def __init__(self, api_client, mode: str = "editorial"):
        self.api_client = api_client
        self.mode = mode
        self.prompt_system = ModularPromptSystem()
        self.logger = logging.getLogger(__name__)
        
        # Configurações de segmentação
        self.target_paragraphs_per_block = 12  # ~2-3 páginas
        self.max_paragraphs_per_block = 20
        self.min_paragraphs_per_block = 5
    
    def process_document(self, input_path: str, output_path: str, callback=None):
        """Processa documento com segmentação inteligente"""
        try:
            self.logger.info(f"**INICIANDO PROCESSAMENTO MODULAR**")
            self.logger.info(f"Modo: **{self.mode.upper()}**")
            
            # 1. Copia o arquivo para preservar formatação
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            shutil.copy2(input_path, output_path)
            
            # 2. Abre o documento de saída para edição
            doc = Document(output_path)
            
            # 3. Extrai conteúdo
            all_paragraphs = self._extract_all_content(doc)
            
            self.logger.info(f"Total de parágrafos: **{len(all_paragraphs)}**")
            
            # 4. Cria blocos inteligentes
            blocks = self._create_smart_blocks(all_paragraphs)
            self.logger.info(f"Documento dividido em **{len(blocks)} blocos**")
            
            # 5. Processa cada bloco com módulos apropriados
            all_corrections = []
            modules = self.prompt_system.get_prompt_sequence(self.mode)
            
            for block_idx, block in enumerate(blocks):
                if callback:
                    callback(block_idx + 1, len(blocks), 
                            f"Processando bloco {block_idx + 1}/{len(blocks)}")
                
                # Processa bloco com cada módulo
                block_corrections = self._process_block_modular(
                    block, block_idx, modules
                )
                
                all_corrections.extend(block_corrections)
                
                # Delay entre blocos
                if block_idx < len(blocks) - 1:
                    self.prompt_system.wait_between_calls()
            
            # 6. IMPORTANTE: Aplica correções no documento
            if all_corrections:
                self._apply_corrections(doc, all_corrections)
                
                # 7. Salva o documento com as correções
                doc.save(output_path)
                self.logger.info(f"Documento salvo com correções: {output_path}")
            else:
                self.logger.warning("Nenhuma correção encontrada!")
            
            self.logger.info(f"**PROCESSAMENTO CONCLUÍDO**")
            self.logger.info(f"Total de correções: **{len(all_corrections)}**")
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"Erro no processamento: {str(e)}")
            raise
    
    def _extract_all_content(self, doc: Document) -> List[Dict]:
        """Extrai todo conteúdo do documento"""
        all_content = []
        para_num = 0
        
        # Parágrafos normais
        for i, para in enumerate(doc.paragraphs):
            if para.text.strip():
                para_num += 1
                all_content.append({
                    'index': para_num,
                    'doc_index': i,
                    'text': para.text,
                    'paragraph_obj': para,
                    'type': 'paragraph',
                    'context': self._analyze_paragraph_context(para, i, doc.paragraphs)
                })
        
        # TODO: Adicionar extração de tabelas
        
        return all_content
    
    def _analyze_paragraph_context(self, para, index: int, all_paragraphs) -> Dict:
        """Analisa contexto do parágrafo para segmentação inteligente"""
        context = {
            'is_title': False,
            'is_section_end': False,
            'is_list_item': False,
            'is_question': False,
            'is_citation_start': False,
            'next_is_empty': False
        }
        
        text = para.text.strip()
        
        # Detecta títulos
        if len(text) < 100 and not text.endswith('.'):
            context['is_title'] = True
        
        # Detecta fim de seção
        if index < len(all_paragraphs) - 1:
            next_para = all_paragraphs[index + 1]
            if not next_para.text.strip():
                context['next_is_empty'] = True
                context['is_section_end'] = True
        
        # Detecta itens de lista
        if text.startswith(('•', '-', '1.', '2.', 'a)', 'b)')):
            context['is_list_item'] = True
        
        # Detecta questões
        if text.startswith(tuple(f'{i}.' for i in range(1, 100))):
            context['is_question'] = True
        
        # Detecta início de citação
        if any(marker in text.lower() for marker in ['leia o texto:', 'observe:', 'veja:']):
            context['is_citation_start'] = True
        
        return context
    
    def _create_smart_blocks(self, paragraphs: List[Dict]) -> List[List[Dict]]:
        """Cria blocos usando segmentação inteligente"""
        blocks = []
        current_block = []
        
        for i, para in enumerate(paragraphs):
            current_block.append(para)
            
            # Verifica se deve cortar aqui
            should_cut = self._should_cut_block(current_block, para, i, paragraphs)
            
            if should_cut:
                blocks.append(current_block)
                current_block = []
        
        # Adiciona último bloco se houver
        if current_block:
            blocks.append(current_block)
        
        return blocks
    
    def _should_cut_block(self, current_block: List[Dict], para: Dict, 
                         index: int, all_paragraphs: List[Dict]) -> bool:
        """Decide se deve cortar o bloco neste ponto"""
        
        # Tamanho mínimo não atingido
        if len(current_block) < self.min_paragraphs_per_block:
            return False
        
        # Tamanho máximo atingido - força corte
        if len(current_block) >= self.max_paragraphs_per_block:
            return True
        
        # Tamanho ideal atingido - procura melhor ponto
        if len(current_block) >= self.target_paragraphs_per_block:
            context = para['context']
            
            # Pontos ideais para corte
            if context['is_section_end']:
                return True
            
            if context['is_title'] and index > 0:
                # Corta ANTES do título (volta um)
                current_block.pop()  # Remove o título do bloco atual
                return True
            
            # Se próximo é questão, corta aqui
            if index < len(all_paragraphs) - 1:
                next_para = all_paragraphs[index + 1]
                if next_para['context']['is_question']:
                    return True
        
        return False
    
    def _process_block_modular(self, block: List[Dict], block_idx: int, 
                              modules: List[PromptModule]) -> List[Dict]:
        """Processa bloco usando módulos sequenciais"""
        
        self.logger.info(f"\n**BLOCO {block_idx + 1}**")
        self.logger.info(f"Parágrafos: {block[0]['index']} a {block[-1]['index']}")
        self.logger.info(f"Módulos a aplicar: {len(modules)}")
        
        # Prepara texto do bloco
        block_text = self._prepare_block_text(block)
        
        # Acumula correções de todos os módulos
        all_corrections = []
        
        # Aplica cada módulo separadamente
        for module_idx, module in enumerate(modules):
            if module.name in ["formato", "protecoes"]:
                continue  # Estes são sempre incluídos
            
            self.logger.info(f"  Aplicando módulo: **{module.name}**")
            
            # Constrói prompt com este módulo específico
            base_modules = [
                self.prompt_system.modules["formato"],
                self.prompt_system.modules["protecoes"],
                module
            ]
            
            prompt = self.prompt_system.build_prompt(base_modules, block_text)
            
            # Chama API
            try:
                corrections = self._call_api_for_corrections(prompt, block_idx)
                
                if corrections:
                    self.logger.info(f"    → {len(corrections)} correções encontradas")
                    
                    # Adiciona informação do módulo
                    for corr in corrections:
                        corr['module'] = module.name
                        corr['block_index'] = block_idx
                    
                    all_corrections.extend(corrections)
                
            except Exception as e:
                self.logger.error(f"Erro no módulo {module.name}: {str(e)}")
            
            # Delay entre módulos
            if module_idx < len(modules) - 1:
                time.sleep(0.3)  # 300ms entre módulos
        
        return all_corrections
    
    def _prepare_block_text(self, block: List[Dict]) -> str:
        """Prepara texto do bloco para análise"""
        lines = []
        
        for para in block:
            lines.append(f"[PARÁGRAFO {para['index']}]")
            
            # Adiciona contexto relevante
            if para['context']['is_title']:
                lines.append("[TIPO: TÍTULO]")
            elif para['context']['is_list_item']:
                lines.append("[TIPO: ITEM DE LISTA]")
            elif para['context']['is_question']:
                lines.append("[TIPO: QUESTÃO]")
            
            lines.append(para['text'])
            lines.append("")
        
        return "\n".join(lines)
    
    def _call_api_for_corrections(self, prompt: str, block_idx: int) -> List[Dict]:
        """Chama API e processa resposta"""
        # Aqui você chamaria sua API real
        # Por enquanto, simulação:
        
        # self.api_client.get_corrections(prompt)
        
        # Retorno simulado
        return []
    
    def _apply_corrections(self, doc: Document, corrections: List[Dict]):
        """Aplica todas as correções no documento"""
        self.logger.info(f"Aplicando {len(corrections)} correções no documento...")
        
        # Agrupa correções por parágrafo para eficiência
        corrections_by_para = {}
        for corr in corrections:
            para_num = corr.get('paragraph', 0)
            if para_num not in corrections_by_para:
                corrections_by_para[para_num] = []
            corrections_by_para[para_num].append(corr)
        
        # Mapeia número do parágrafo para objeto parágrafo
        para_map = {}
        para_counter = 0
        
        # Mapeia parágrafos normais
        for i, para in enumerate(doc.paragraphs):
            if para.text.strip():
                para_counter += 1
                para_map[para_counter] = para
        
        # TODO: Adicionar mapeamento de tabelas se necessário
        
        # Aplica correções em cada parágrafo
        applied_count = 0
        for para_num, para_corrections in sorted(corrections_by_para.items()):
            if para_num in para_map:
                paragraph = para_map[para_num]
                original_text = paragraph.text
                current_text = original_text
                
                # Ordena correções pela posição no texto (se disponível)
                # para aplicar da direita para esquerda e não bagunçar índices
                sorted_corrections = sorted(para_corrections, 
                                          key=lambda x: len(original_text) - len(x.get('error', '')), 
                                          reverse=True)
                
                # Aplica cada correção
                for corr in sorted_corrections:
                    error = corr.get('error', '')
                    correction = corr.get('correction', '')
                    
                    if error and correction and error in current_text:
                        # Aplica a correção
                        current_text = current_text.replace(error, correction, 1)
                        applied_count += 1
                        
                        self.logger.debug(f"Aplicada correção no parágrafo {para_num}: '{error}' → '{correction}'")
                
                # Atualiza o texto do parágrafo se houve mudanças
                if current_text != original_text:
                    paragraph.text = current_text
            else:
                self.logger.warning(f"Parágrafo {para_num} não encontrado no documento")
        
        self.logger.info(f"Aplicadas {applied_count} de {len(corrections)} correções")