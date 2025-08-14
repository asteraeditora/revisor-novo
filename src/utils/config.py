import json
import os

class Config:
    def __init__(self):
        # Pega o diretório raiz do projeto (2 níveis acima de utils/)
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.config_path = os.path.join(base_dir, "config.json")
        self.load_config()
    
    def load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = self.get_default_config()
            self.save_config(config)
        
        self.API_KEY = config.get("api_key", "")
        self.MODEL = config.get("model", "gpt-4.1")  # SEMPRE gpt-4.1
        self.MAX_TOKENS_PER_CHUNK = config.get("max_tokens_per_chunk", 50000)  # Maior para gpt-4.1
        self.MAX_RETRIES = config.get("max_retries", 3)
        self.OUTPUT_PATHS = config.get("output_paths", {
            "revised": "output/revised",
            "comparisons": "output/comparisons",
            "logs": "output/logs"
        })
    
    def get_default_config(self):
        return {
            "api_key": "",
            "model": "gpt-4.1",  # SEMPRE gpt-4.1
            "max_tokens_per_chunk": 10000,  # Aproveita janela maior do gpt-4.1
            "max_retries": 3,
            "output_paths": {
                "revised": "output/revised",
                "comparisons": "output/comparisons",
                "logs": "output/logs"
            }
        }
    
    def save_config(self, config):
        # Cria diretório se não existir
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
    
    def update_api_key(self, api_key):
        config = self.get_current_config()
        config["api_key"] = api_key
        self.save_config(config)
        self.API_KEY = api_key
    
    def get_current_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return self.get_default_config()