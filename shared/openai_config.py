import os
import dotenv
from openai import OpenAI

dotenv.load_dotenv()

def get_openai_client():
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key is None:
        raise ValueError('The OPENAI_API_KEY environment variable is not set.')
    return OpenAI(api_key=api_key)