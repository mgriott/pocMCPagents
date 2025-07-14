import os
from dotenv import load_dotenv

load_dotenv()  # Carga variables desde .env

llm_config_groq = {
    "config_list": [
        {
            "model": os.getenv("GROQ_LLM_MODEL"),
            "api_key": os.getenv("GROQ_API_KEY"),
            "base_url": os.getenv("GROQ_BASE_URL"),
            "price": [0.002, 0.004]
        }
    ]
}
