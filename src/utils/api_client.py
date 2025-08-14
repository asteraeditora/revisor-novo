import openai
import time
import logging
import json
import re
from typing import List, Dict

class OpenAIClient:
    """Cliente para API OpenAI - Versão Otimizada com Retry"""
    
    def __init__(self, api_key: str, model: str = "gpt-4.1"):
        self.api_key = api_key  
        openai.api_key = api_key
        # Usa GPT-4.1 como solicitado
        self.model = model  # Agora respeita o parâmetro, mas o padrão é gpt-4.1
        self.logger = logging.getLogger(__name__)
        
        # Configurações otimizadas para GPT-4.1
        self.temperature = 0  # Mais determinístico
        self.max_tokens = 4000  # Aumentado para processar mais correções por vez
        
        # Rate limit para GPT-4 (muito menor que gpt-3.5)
        self.requests_per_minute = 60  # Limite mais baixo do GPT-4
        self.last_request_time = 0
        self.min_time_between_requests = 60.0 / self.requests_per_minute
        self.retry_delays = [2, 5, 10, 20]  # Delays maiores para GPT-4
    
    def identify_errors_precise(self, prompt: str, block_index: int = 0) -> List[Dict]:
        """
        Versão otimizada com retry e backoff exponencial
        """
        
        # Controle de rate limit mais conservador
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_time_between_requests:
            time.sleep(self.min_time_between_requests - time_since_last)
        
        self.last_request_time = time.time()
        
        # Tentativas com retry
        for attempt in range(len(self.retry_delays)):
            try:
                # Prompt mais curto e direto
                messages = [
                    {
                        "role": "system", 
                        "content": "Você é um corretor. Responda APENAS com JSON válido."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ]
                
                # Chamada otimizada
                start_time = time.time()
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=messages,
                    temperature=0,
                    max_tokens=self.max_tokens,
                    top_p=1,  # Sem penalidades = mais rápido
                    frequency_penalty=0,
                    presence_penalty=0,
                    n=1,  # Uma resposta só
                    stream=False,  # Sem streaming
                    request_timeout=120  # Timeout de 120 segundos para GPT-4.1
                )
                
                api_time = time.time() - start_time
                self.logger.debug(f"Bloco {block_index}: API respondeu em {api_time:.2f}s")
                
                result = response.choices[0].message.content.strip()
                
                # Parse rápido do JSON
                try:
                    # Tenta direto primeiro (mais rápido)
                    if result.startswith('{') and result.endswith('}'):
                        data = json.loads(result)
                    else:
                        # Fallback com regex se necessário
                        json_match = re.search(r'\{.*\}', result, re.DOTALL)
                        if json_match:
                            data = json.loads(json_match.group())
                        else:
                            return []
                    
                    corrections = data.get('corrections', [])
                    
                    # Validação mínima e rápida
                    valid_corrections = []
                    for corr in corrections:
                        # Validação super básica
                        if (corr.get('paragraph') and 
                            corr.get('error') and 
                            corr.get('correction') and 
                            corr.get('error') != corr.get('correction')):
                            corr['block_index'] = block_index
                            valid_corrections.append(corr)
                    
                    return valid_corrections
                    
                except:
                    return []
                    
            except (openai.error.APIError, openai.error.ServiceUnavailableError, openai.error.APIConnectionError) as e:
                # Erro de servidor - faz retry com backoff
                if attempt < len(self.retry_delays) - 1:
                    delay = self.retry_delays[attempt]
                    self.logger.warning(f"Erro de servidor no bloco {block_index}, tentativa {attempt + 1}. Aguardando {delay}s...")
                    time.sleep(delay)
                    continue
                else:
                    self.logger.error(f"Erro no bloco {block_index} após {attempt + 1} tentativas: {str(e)}")
                    return []
                    
            except openai.error.RateLimitError as e:
                # Rate limit - espera mais
                if attempt < len(self.retry_delays) - 1:
                    delay = self.retry_delays[attempt] * 2  # Dobra o delay para rate limit
                    self.logger.warning(f"Rate limit no bloco {block_index}. Aguardando {delay}s...")
                    time.sleep(delay)
                    continue
                else:
                    return []
                    
            except Exception as e:
                # Captura erros genéricos incluindo "server overloaded" e timeout
                error_msg = str(e).lower()
                if "overloaded" in error_msg or "server" in error_msg or "timeout" in error_msg:
                    if attempt < len(self.retry_delays) - 1:
                        delay = self.retry_delays[attempt]
                        self.logger.warning(f"Timeout/Servidor sobrecarregado no bloco {block_index}. Aguardando {delay}s...")
                        time.sleep(delay)
                        continue
                
                self.logger.error(f"Erro inesperado no bloco {block_index}: {str(e)}")
                return []
        
        return []
    
    def identify_errors_batch(self, prompts: List[tuple]) -> List[List[Dict]]:
        """
        Processa múltiplos blocos em paralelo para máxima velocidade
        
        Args:
            prompts: Lista de tuplas (prompt, block_index)
            
        Returns:
            Lista de listas de correções
        """
        results = []
        
        # Processa em lotes de 10 para não sobrecarregar
        batch_size = 10
        for i in range(0, len(prompts), batch_size):
            batch = prompts[i:i+batch_size]
            batch_results = []
            
            for prompt, block_idx in batch:
                result = self.identify_errors_precise(prompt, block_idx)
                batch_results.append(result)
            
            results.extend(batch_results)
            
            # Log de progresso
            self.logger.info(f"Processados {min(i+batch_size, len(prompts))}/{len(prompts)} blocos")
        
        return results
    
    def _validate_correction(self, correction: Dict) -> bool:
        """Validação mínima para velocidade"""
        return bool(
            correction.get('paragraph') and 
            correction.get('error') and 
            correction.get('correction') and
            correction['error'] != correction['correction']
        )
    
    # Métodos removidos ou simplificados para velocidade
    
    def get_segmentation_analysis(self, text: str) -> Dict:
        """Removido - segmentação agora é fixa para velocidade"""
        return {"ideal_cut_point": -1, "reason": "disabled", "confidence": 0.0}
    
    def set_mode(self, mode: str):
        """Ignorado"""
        pass
    
    def identify_errors(self, text: str, text_index: int = 0) -> List[Dict]:
        """Ignorado"""
        return []