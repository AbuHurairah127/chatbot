import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is not set in .env")

client = Groq(api_key=GROQ_API_KEY)
DEFAULT_MODEL = "openai/gpt-oss-20b"


def generate_reply(prompt: str) -> str:
    """Send the user prompt to Groq and return the assistant reply."""
    completion = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful AI assistant. Reply clearly and concisely.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=1024,
    )
    return completion.choices[0].message.content or ""
