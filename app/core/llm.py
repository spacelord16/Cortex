from langchain_openai import ChatOpenAI
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_community.chat_models import ChatOllama
from app.core.config import get_settings
import os
from dotenv import load_dotenv

load_dotenv()  # ensures GOOGLE_API_KEY etc. are in os.environ for SDKs that read it directly

settings = get_settings()

def get_llm():
    """
    Factory function to return the configured LLM instance.
    Supports: gemini, huggingface, ollama, openai (default / Groq-compatible)
    """
    provider = settings.LLM_PROVIDER

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=settings.LLM_MODEL or "gemini-2.0-flash",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0,
            convert_system_message_to_human=True,
        )

    elif provider == "huggingface":
        # Use HuggingFace Endpoint (Serverless)
        llm = HuggingFaceEndpoint(
            repo_id=settings.LLM_MODEL,
            task="text-generation",
            max_new_tokens=512,
            do_sample=True,
            repetition_penalty=1.03,
            huggingfacehub_api_token=settings.HUGGINGFACEHUB_API_TOKEN
        )
        return ChatHuggingFace(llm=llm)

    elif provider == "ollama":
        return ChatOllama(
            base_url=settings.LLM_BASE_URL or "http://localhost:11434",
            model=settings.LLM_MODEL
        )

    else:  # Default: OpenAI-compatible (Groq, LlamaAPI, etc.)
        return ChatOpenAI(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
            model=settings.LLM_MODEL,
            temperature=0
        )
