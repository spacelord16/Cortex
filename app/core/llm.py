from langchain_openai import ChatOpenAI
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_community.chat_models import ChatOllama
from app.core.config import get_settings
import os
from dotenv import load_dotenv

load_dotenv()  # ensures GOOGLE_API_KEY etc. are in os.environ for SDKs that read it directly

settings = get_settings()

# --- Singleton LLM cache ---
# Re-instantiating the LLM client on every node call adds overhead.
# We create it once per server process and reuse it everywhere.
_llm_instance = None

def get_llm():
    """
    Factory function to return the configured LLM instance.
    Supports: gemini, huggingface, ollama, openai (default / Groq-compatible)
    Uses a module-level singleton so the client is created only once per process.
    """
    global _llm_instance
    if _llm_instance is not None:
        return _llm_instance

    provider = settings.LLM_PROVIDER

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        _llm_instance = ChatGoogleGenerativeAI(
            model=settings.LLM_MODEL or "gemini-2.0-flash",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0,
            convert_system_message_to_human=True,
        )

    elif provider == "huggingface":
        llm = HuggingFaceEndpoint(
            repo_id=settings.LLM_MODEL,
            task="text-generation",
            max_new_tokens=512,
            do_sample=True,
            repetition_penalty=1.03,
            huggingfacehub_api_token=settings.HUGGINGFACEHUB_API_TOKEN
        )
        _llm_instance = ChatHuggingFace(llm=llm)

    elif provider == "ollama":
        _llm_instance = ChatOllama(
            base_url=settings.LLM_BASE_URL or "http://localhost:11434",
            model=settings.LLM_MODEL
        )

    else:  # Default: OpenAI-compatible (Groq, LlamaAPI, etc.)
        _llm_instance = ChatOpenAI(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
            model=settings.LLM_MODEL,
            temperature=0
        )

    return _llm_instance

