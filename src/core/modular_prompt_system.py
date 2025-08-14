import time
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class PromptModule:
    """Módulo individual de prompt"""
    name: str
    content: str
    priority: int = 0

class ModularPromptSystem:
    """Sistema modular de prompts otimizado para velocidade"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.delay_between_calls = 50  # 50ms apenas - muito mais rápido
        
        # Registra todos os módulos de prompt
        self.modules = {
            # **MÓDULOS BASE**
            "formato": self._get_format_module(),
            "protecoes": self._get_protections_module(),
            
            # **MÓDULOS DE CORREÇÃO**
            "erros_graves": self._get_serious_errors_module(),
            "erros_gramaticais": self._get_grammar_errors_module(),
            "pontuacao": self._get_punctuation_module(),
            
            # **MÓDULOS DE QUALIDADE**
            "repeticoes": self._get_repetitions_module(),
            "redundancias": self._get_redundancy_module(),
            "fluidez": self._get_fluency_module(),
            
            # **MÓDULOS DIDÁTICOS**
            "maneirismos_ia": self._get_ai_mannerisms_module(),
            "linguagem_didatica": self._get_didactic_language_module(),
            "tratamento_uniforme": self._get_uniform_treatment_module(),
            "numeros_uniformes_padrao_internacional": self._get_uniform_treatment_module(),
            
            # **MÓDULO DE SEGMENTAÇÃO**
            "segmentacao": self._get_segmentation_module(),
            
            # **MÓDULO ESPECIAL PARA QUESTÕES**
            "questoes_com_gabarito": self._get_questions_with_answer_key_module()
        }
    
    # **MÓDULOS BASE**
    
    def _get_format_module(self) -> PromptModule:
        """Módulo de formato de resposta"""
        return PromptModule(
            name="formato",
            content="""**FORMATO DE RESPOSTA**
Retorne APENAS um JSON válido:
{
  "corrections": [
    {
      "paragraph": 1,
      "error": "texto com erro",
      "correction": "texto corrigido",
      "type": "tipo do erro"
    }
  ]
}

Se não houver correções: {"corrections": []                }"""
        )
    
    def _get_questions_with_answer_key_module(self) -> PromptModule:
        """Módulo especial para questões com gabarito"""
        return PromptModule(
            name="questoes_com_gabarito",
            content="""**REVISÃO ESPECIAL DE QUESTÕES COM GABARITO**

INSTRUÇÕES CRÍTICAS:

1. **IDENTIFICAÇÃO AUTOMÁTICA**:
   - Linhas marcadas com [ALTERNATIVA_CORRETA] = alternativa correta segundo o gabarito
   - Linhas marcadas com [ALTERNATIVA_INCORRETA] = alternativas incorretas
   - O sistema já identificou qual é qual baseado no gabarito

2. **PARA [ALTERNATIVA_INCORRETA]**:
   - Corrija APENAS erros gramaticais, ortográficos e de pontuação
   - NUNCA corrija conteúdo factual (está errado de propósito!)
   - NUNCA altere informações técnicas, datas, nomes ou conceitos
   - Exemplo: "São Paulo é a capital do Brazil" → "São Paulo é a capital do Brasil"
   - NÃO mude para "Brasília é a capital do Brasil" (isso é correção factual!)

3. **PARA [ALTERNATIVA_CORRETA]**:
   - Corrija TODOS os erros: gramática, ortografia, pontuação E factualidade
   - Garanta que a informação está 100% correta
   - Exemplo: "Brazília é a capital do Brazil" → "Brasília é a capital do Brasil"

4. **IMPORTANTE**:
   - Se não houver marcação [ALTERNATIVA_CORRETA/INCORRETA], trate como texto normal
   - O gabarito em si (ex: "Gabarito: C") só precisa correção gramatical""",
            priority=11
        )
    
    def _get_protections_module(self) -> PromptModule:
        """Módulo de conteúdo protegido"""
        return PromptModule(
            name="protecoes",
            content="""**CONTEÚDO PROTEGIDO - NUNCA ALTERE**

REGRA ABSOLUTA: Os seguintes conteúdos NUNCA devem ser modificados:

1. **ALTERNATIVAS DE QUESTÕES**
   - QUALQUER linha que comece com: a), b), c), d), e)
   - QUALQUER linha que comece com: (a), (b), (c), (d), (e)
   - QUALQUER linha que comece com: a., b., c., d., e.
   - QUALQUER linha que comece com: A), B), C), D), E)
   - Mesmo que contenham erros propositais ou factuais

2. **CITAÇÕES E REFERÊNCIAS**
   - Qualquer texto entre aspas com atribuição de autoria
   - Textos com fonte indicada (Fonte:, Referência:, Extraído de:, Adaptado de:)
   - Textos seguidos de referência bibliográfica ou URL
   - Textos da Wikipedia ou qualquer outra fonte online
   - Qualquer parágrafo que termine com indicação de fonte
   - Textos indentados ou em itálico que sejam citações
   - Blocos de texto seguidos por autor, data ou fonte

3. **POEMAS E TEXTOS LITERÁRIOS**
   - Versos de poemas (linhas curtas sem pontuação final)
   - Textos com estrutura poética ou literária
   - Letras de músicas
   - Trechos de obras literárias

4. **OUTROS PROTEGIDOS**
   - Códigos BNCC (EF01LP01, EM13LGG101, etc)
   - URLs e links completos
   - Referências bibliográficas completas
   - Gabaritos de questões
   - Exemplos de erros (quando indicado)
   - Fórmulas matemáticas e químicas

IMPORTANTE: Na dúvida, NÃO ALTERE. É melhor preservar um texto com erro do que alterar uma citação original."""
        )
    
    # **MÓDULOS DE CORREÇÃO BÁSICA**
    
    def _get_serious_errors_module(self) -> PromptModule:
        """Módulo para erros graves apenas"""
        return PromptModule(
            name="erros_graves",
            content="""**CORRIJA APENAS ERROS GRAVÍSSIMOS**
1. Erros de digitação óbvios (computadr → computador)
2. Ortografia grotescamente errada (ezemplo → exemplo)
3. Concordância completamente errada (os menino → os meninos)
4. Acentuação faltando em palavras básicas (voce → você)
5. Pontuação duplicada (.., ,, → . ,)
6. Falta de espaço óbvia (amesa → a mesa)

**NA DÚVIDA, NÃO CORRIJA!**""",
            priority=1
        )
    
    def _get_grammar_errors_module(self) -> PromptModule:
        """Módulo para todos os erros gramaticais"""
        return PromptModule(
            name="erros_gramaticais",
            content="""**CORRIJA TODOS OS ERROS GRAMATICAIS**
1. Ortografia incorreta
2. Concordância verbal e nominal
3. Regência verbal e nominal
4. Acentuação incorreta ou faltando
5. Crase incorreta ou faltando
6. Uso incorreto de pronomes
7. Conjugação verbal errada""",
            priority=2
        )
    
    def _get_punctuation_module(self) -> PromptModule:
        """Módulo específico para pontuação"""
        return PromptModule(
            name="pontuacao",
            content="""**CORRIJA PONTUAÇÃO**
1. Falta de ponto final em parágrafos
2. Vírgulas obrigatórias faltando
3. Pontuação antes de conjunções
4. Dois-pontos e ponto-e-vírgula incorretos
5. Aspas e parênteses desbalanceados
6. Espaços incorretos com pontuação""",
            priority=3
        )
    
    # **MÓDULOS DE QUALIDADE**
    
    def _get_repetitions_module(self) -> PromptModule:
        """Módulo para repetições"""
        return PromptModule(
            name="repeticoes",
            content="""**REMOVA REPETIÇÕES DESNECESSÁRIAS**
1. Palavra repetida em sequência (o o → o)
2. Mesma palavra 3+ vezes em 2 linhas
3. Início de frases consecutivas iguais
4. Repetição de conectivos próximos""",
            priority=4
        )
    
    def _get_redundancy_module(self) -> PromptModule:
        """Módulo para redundâncias"""
        return PromptModule(
            name="redundancias",
            content="""**ELIMINE REDUNDÂNCIAS**
1. Subir para cima → subir
2. Entrar para dentro → entrar
3. Sair para fora → sair
4. Elo de ligação → elo
5. Planos para o futuro → planos""",
            priority=5
        )
    
    def _get_fluency_module(self) -> PromptModule:
        """Módulo para fluidez"""
        return PromptModule(
            name="fluidez",
            content="""**MELHORE A FLUIDEZ (MÍNIMO NECESSÁRIO)**
1. Adicione conectivos essenciais faltando
2. Complete frases truncadas
3. Resolva ambiguidades graves
4. Corrija ordem de palavras confusa""",
            priority=6
        )
    
    # **MÓDULOS DIDÁTICOS**
    
    def _get_ai_mannerisms_module(self) -> PromptModule:
        """Módulo para maneirismos de IA"""
        return PromptModule(
            name="maneirismos_ia",
            content="""**REMOVA MANEIRISMOS DE IA**
1. Metáforas desnecessárias (é como um quebra-cabeça)
2. Analogias forçadas (são como temperos)
3. Juízo de valor (fascinante, incrível, o mais legal)
4. Perguntas retóricas (Sabe quando...? Já pensou...?)
5. Saudações diretas (Olá, estudantes!)
6. Verbos informais (vamos mergulhar, vamos explorar)
7. Adjetivação excessiva (super interessante, muito mais divertido)""",
            priority=7
        )
    
    def _get_didactic_language_module(self) -> PromptModule:
        """Módulo para linguagem didática"""
        return PromptModule(
            name="linguagem_didatica",
            content="""**ADEQUE PARA LINGUAGEM DIDÁTICA**
1. Substitua informalidades (tipo → como, né → não é)
2. Remova diminutivos desnecessários (tudinho → tudo)
3. Elimine gírias e expressões coloquiais
4. Mantenha vocabulário apropriado para idade
5. Use termos técnicos com explicação quando necessário""",
            priority=8
        )
    
    def _get_uniform_treatment_module(self) -> PromptModule:
        """Módulo para tratamento uniforme"""
        return PromptModule(
            name="tratamento_uniforme",
            content="""**PADRONIZE O TRATAMENTO**
1. Use sempre SINGULAR (você, não vocês)
2. Evite "a gente" → use "nós" ou reformule
3. Mantenha impessoalidade quando apropriado
4. Evite se dirigir diretamente ao leitor em excesso""",
            priority=9
        )
    
    def _get_uniform_treatment_module(self) -> PromptModule:
        """Módulo para tratamento uniforme de números e unidades."""
        return PromptModule(
            name="numeros_uniformes_padrao_internacional",
            content="""**REGRAS DE FORMATAÇÃO NUMÉRICA (PADRÃO INTERNACIONAL)**

1.  **SEPARADOR DE MILHARES**:
    * Todos os números com quatro ou mais dígitos devem ter seus grupos de três dígitos separados por um **espaço fino não separável (Unicode `U+202F`)**.
    * É estritamente **proibido** o uso de pontos (`.`) ou vírgulas (`,`) como separadores de milhares.
    * **Exemplos de aplicação**:
        * `1000` deve ser formatado como `1 000`
        * `12345` deve ser formatado como `12 345`
        * `1500000` deve ser formatado como `1 500 000`

2.  **NÚMERO E UNIDADE**:
    * Sempre utilize um **espaço não separável (Unicode `U+00A0`)** entre um número e sua respectiva unidade de medida (ex: cm, kg, km/h, R$).
    * Esta regra garante que o número e sua unidade nunca sejam separados por uma quebra de linha.
    * **Exemplos de aplicação**:
        * `10cm` ou `10 cm` (com espaço comum) deve ser formatado como `10 cm` (com `U+00A0`).
        * `R$50` deve ser formatado como `R$ 50` (com `U+00A0`).
        * `78km` deve ser formatado como `78 km` (com `U+00A0`).

3.  **INTEGRIDADE NUMÉRICA**:
    * Um número completo, incluindo seus separadores de milhares e sua unidade (se aplicável), deve ser tratado como um bloco único e indivisível, **sempre permanecendo na mesma linha**. As regras acima garantem essa condição.""",
        priority=10
    )
    
    # **MÓDULO DE SEGMENTAÇÃO**
    
    def _get_segmentation_module(self) -> PromptModule:
        """Módulo para análise de segmentação"""
        return PromptModule(
            name="segmentacao",
            content="""**ANÁLISE DE SEGMENTAÇÃO DE BLOCO**
Analise o texto e indique onde seria ideal cortar este bloco:

1. **Procure por quebras naturais**:
   - Fim de seção ou tópico
   - Mudança de assunto
   - Transição entre conceitos
   - Após conclusão de ideia

2. **Evite cortar**:
   - No meio de parágrafos
   - Durante explicações
   - Entre pergunta e resposta
   - No meio de listas

3. **Tamanho ideal**: 2-3 páginas (aproximadamente 10-15 parágrafos)

Retorne:
{
  "ideal_cut_point": número_do_parágrafo,
  "reason": "motivo da escolha",
  "confidence": 0.0-1.0
}"""
        )
    
    def get_prompt_sequence(self, mode: str) -> List[PromptModule]:
        """Retorna sequência de prompts baseada no modo"""
        
        sequences = {
            # Modo ULTRA RÁPIDO - apenas o essencial
            "fast": [
                self.modules["formato"],
                self.modules["protecoes"],
                self.modules["erros_gramaticais"],
                self.modules["pontuacao"]
            ],
            
            "conservador": [
                self.modules["formato"],
                self.modules["protecoes"],
                self.modules["erros_graves"]
            ],
            
            "balanceado": [
                self.modules["formato"],
                self.modules["protecoes"],
                self.modules["erros_graves"],
                self.modules["erros_gramaticais"],
                self.modules["pontuacao"]
            ],
            
            "editorial": [
                self.modules["formato"],
                self.modules["protecoes"],
                self.modules["erros_gramaticais"],
                self.modules["pontuacao"],
                self.modules["repeticoes"],
                self.modules["redundancias"],
                self.modules["fluidez"],
                self.modules["maneirismos_ia"],
                self.modules["linguagem_didatica"],
                self.modules["tratamento_uniforme"],
                self.modules["segmentacao"],
                self.modules["questoes_com_gabarito"],
                self.modules["numeros_uniformes_padrao_internacional"]
            ]
        }
        
        return sequences.get(mode, sequences["fast"])
    
    def build_prompt(self, modules: List[PromptModule], text: str) -> str:
        """Constrói prompt completo com módulos selecionados"""
        prompt_parts = [
            "Você é um revisor de textos educacionais.",
            ""
        ]
        
        # Adiciona módulos em ordem de prioridade
        sorted_modules = sorted(modules, key=lambda m: m.priority)
        for module in sorted_modules:
            prompt_parts.append(module.content)
            prompt_parts.append("")
        
        prompt_parts.append("**TEXTO PARA REVISAR:**")
        prompt_parts.append(text)
        
        return "\n".join(prompt_parts)
    
    def wait_between_calls(self):
        """Aguarda entre chamadas para evitar throttling"""
        time.sleep(self.delay_between_calls / 1000.0)  # Converte ms para segundos