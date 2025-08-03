from openai import OpenAI
from .config import API_KEY


client = OpenAI(api_key=API_KEY)