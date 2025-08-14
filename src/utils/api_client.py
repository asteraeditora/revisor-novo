import openai
import time
import logging
import json
import re
from typing import List, Dict

class OpenAIClient:
    """Cliente para API OpenAI - Versão Modular"""
    
    def __init__(self, api_key: str, model: str = "gpt-4.1"):
        self.api_key = api_key  
        openai.api_key = api_key
        self.model = model
        self.logger = logging.getLogger(__name__)
        
        # Configurações para o modelo
        self.temperature = 0.1
        self.max_tokens = 10000
    
    def identify_errors_precise(self, prompt: str, block_index: int = 0) -> List[Dict]:
        """
        Recebe prompt MODULAR já montado e retorna correções
        
        Args:
            prompt: Prompt completo já montado pelo sistema modular
            block_index: Índice do bloco sendo processado
            
        Returns:
            Lista de correções encontradas
        """
        
        self.logger.debug(f"Processando bloco {block_index} com prompt modular")
        
        for attempt in range(3):
            try:
                # Chama a API com o prompt modular
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system", 
                            "content": "Você é um revisor de textos educacionais. Siga as instruções fornecidas com precisão."
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    top_p=0.1,
                    frequency_penalty=0,
                    presence_penalty=0
                )
                
                result = response.choices[0].message.content.strip()
                
                # Processa resposta
                try:
                    # Tenta extrair JSON da resposta
                    json_match = re.search(r'\{.*\}', result, re.DOTALL)
                    if json_match:
                        data = json.loads(json_match.group())
                    else:
                        data = json.loads(result)
                    
                    corrections = data.get('corrections', [])
                    
                    # Valida e filtra correções
                    validated_corrections = []
                    for corr in corrections:
                        if self._validate_correction(corr):
                            corr['block_index'] = block_index
                            validated_corrections.append(corr)
                    
                    self.logger.info(f"Bloco {block_index}: {len(validated_corrections)} correções válidas")
                    return validated_corrections
                    
                except json.JSONDecodeError as e:
                    self.logger.error(f"Erro ao decodificar JSON: {e}")
                    self.logger.error(f"Resposta: {result[:500]}...")
                    return []
                    
            except openai.error.RateLimitError:
                self.logger.warning(f"Rate limit atingido. Aguardando...")
                time.sleep(5 * (attempt + 1))  # Espera progressiva
                
            except openai.error.APIError as e:
                self.logger.error(f"Erro da API na tentativa {attempt + 1}: {str(e)}")
                if attempt < 2:
                    time.sleep(2 ** attempt)
                    
            except Exception as e:
                self.logger.error(f"Erro inesperado na tentativa {attempt + 1}: {str(e)}")
                if attempt < 2:
                    time.sleep(1)
                else:
                    return []
        
        return []
    
    def _validate_correction(self, correction: Dict) -> bool:
        """
        Valida correção básica
        
        Args:
            correction: Dicionário com a correção
            
        Returns:
            True se a correção é válida
        """
        # Validações básicas
        required_fields = ['paragraph', 'error', 'correction', 'type']
        
        for field in required_fields:
            if field not in correction:
                self.logger.warning(f"Correção sem campo obrigatório '{field}'")
                return False
        
        # Verifica se não está vazio
        if not correction['error'].strip() or not correction['correction'].strip():
            return False
        
        # Verifica se realmente é uma mudança
        if correction['error'] == correction['correction']:
            return False
        
        # Validações específicas que eram feitas nos prompts antigos
        # mas agora são responsabilidade dos módulos
        
        # Se tem confidence, valida
        if 'confidence' in correction:
            if correction['confidence'] < 0.7:  # Threshold de confiança
                self.logger.info(f"Correção rejeitada por baixa confiança: {correction['confidence']}")
                return False
        
        return True
    
    def get_segmentation_analysis(self, text: str) -> Dict:
        """
        Analisa onde segmentar o texto
        
        Args:
            text: Texto para analisar
            
        Returns:
            Dicionário com ponto de corte ideal
        """
        prompt = """**ANÁLISE DE SEGMENTAÇÃO**
        
Analise o texto e indique o melhor ponto para dividir este bloco.
Procure quebras naturais entre tópicos ou seções.

Retorne APENAS um JSON:
{
    "ideal_cut_point": número_do_parágrafo,
    "reason": "motivo",
    "confidence": 0.0-1.0
}"""
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Você é um especialista em segmentação de texto."},
                    {"role": "user", "content": prompt + "\n\n" + text}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            result = response.choices[0].message.content.strip()
            return json.loads(result)
            
        except Exception as e:
            self.logger.error(f"Erro na análise de segmentação: {str(e)}")
            return {"ideal_cut_point": -1, "reason": "erro", "confidence": 0.0}
    
    # Métodos auxiliares para compatibilidade
    
    def set_mode(self, mode: str):
        """Mantido para compatibilidade, mas não usado no sistema modular"""
        self.logger.info(f"set_mode chamado com '{mode}' - ignorado no sistema modular")
    
    def identify_errors(self, text: str, text_index: int = 0) -> List[Dict]:
        """Mantido para compatibilidade"""
        self.logger.warning("identify_errors chamado - use identify_errors_precise com prompt modular")
        return []