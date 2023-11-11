from shared.settings import Settings
from openai import OpenAI

def get_openai_client():
    settings = Settings()
    return OpenAI(api_key=settings.OPENAI_API_KEY)
