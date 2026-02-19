# Cortex (formerly Me-Server)

**Cortex** is an Agentic Personal Operating System designed to proactively manage your digital life. Built with **FastAPI**, **LangGraph**, and **Next.js**, it features a multi-agent architecture capable of intelligent routing, system monitoring, and future RAG/Calendar integrations.

## 🚀 Quick Start

1. **Install Dependencies**:
   - Backend: `uv sync` (or `pip install -r requirements.txt`)
   - Frontend: `cd frontend && npm install`

2. **Configure Environment**:
   - Copy `.env.example` to `.env`.
   - Set your LLM keys (OpenAI, Hugging Face, or Groq).

3. **Launch Cortex**:
   ```bash
   chmod +x start_cortex.sh
   ./start_cortex.sh
   ```
   - **Backend**: `http://localhost:8000`
   - **Frontend**: `http://localhost:3000`

## 🧠 Architecture

- **Supervisor Agent**: Routes requests using JSON-based reasoning (Model Agnostic).
- **System Worker**: Monitor CPU, RAM, Battery using local tools (Manual ReAct Loop).
- **Journal Worker**: (Coming Soon) RAG-based introspection.
- **Calendar Worker**: (Coming Soon) Schedule management.

## 🛠 Tech Stack

- **Backend**: Python, FastAPI, LangGraph, LangChain.
- **Frontend**: TypeScript, Next.js, Tailwind CSS, shadcn/ui.
- **LLM**: Agnostic (Tested with Llama-3-70B via Hugging Face & OpenAI).

## License
MIT
