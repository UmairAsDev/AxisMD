import os
import yaml
from dotenv import load_dotenv
from pyprojroot import here

load_dotenv()

class LoadToolsConfig:
    def __init__(self) -> None:
        """Load configuration from YAML and environment variables."""

        config_path = here("config/config.yaml")
        with open(config_path, "r") as cfg:
            app_config = yaml.load(cfg, Loader=yaml.FullLoader)
            
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key is not None:
            os.environ["OPENAI_API_KEY"] = openai_api_key
        
        self.db_url = "postgres://neondb_owner:npg_ce1TbYCx4DwR@ep-late-haze-ad9zbod6-pooler.c-2.us-east-1.aws.neon.tech/AxisMD"
        
        self.host = os.environ["HOST"]
        self.port = int(os.environ["PORT"])
        self.db_username = app_config["database"]["user"]
        self.db_password = app_config["database"]["password"]
        self.db_name = app_config["database"]["dbname"]
        self.audio_file = app_config["audio"]["dir"]
        self.voice_model = app_config["voice_llm"]["model"]
        self.provider = app_config["voice_llm"]["provider"]
        self.openai_api_key = os.environ["OPENAI_API_KEY"]
        self.temperature = app_config["voice_llm"]["temperature"]
        self.max_token = app_config["voice_llm"]["max_tokens"]
        self.top_p = app_config["llm"]["top_p"]
        self.frequency_penalty = app_config["llm"]["frequency_penalty"]
        self.presence_penalty = app_config["llm"]["presence_penalty"]
        self.noise_reduction = app_config["voice_llm"]["noise_reduction"]
        self.silence_duration = app_config["voice_llm"]["silence_duration"]
        self.threshold = app_config["voice_llm"]["threshold"]
        self.voice_llm_mini = app_config["voice_llm_mini"]["model"]
        
TOOLS_CFG = LoadToolsConfig()
        