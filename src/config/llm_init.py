from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_xai import ChatXAI

from langchain.chat_models import init_chat_model

load_dotenv()
init_chat_model()
model = ChatAnthropic(
    model_name="claude-sonnet-4-20250514",
    timeout=120,
)
# ChatXAI(model="grok-3-mini", timeout=120)
# .with_fallbacks([ChatXAI(model="grok-3-mini", timeout=60)])


__all__ = [
    "model",
]
