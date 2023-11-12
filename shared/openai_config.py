from shared.settings import settings
from openai import OpenAI

def get_openai_client():
    return OpenAI(api_key=settings.OPENAI_API_KEY)
