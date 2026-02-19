from langchain_openai import ChatOpenAI
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_community.chat_models import ChatOllama
from app.core.config import get_settings

settings = get_settings()

def get_llm():
    """
    Factory function to return the configured LLM instance.
    """
    provider = settings.LLM_PROVIDER
    
    if provider == "huggingface":
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
        
    else: # Default to OpenAI / Compatible (Groq, LlamaAPI)
        return ChatOpenAI(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
            model=settings.LLM_MODEL,
            temperature=0
        )
