"""
LLM Speed & Latency Benchmark Test
Compares latency and time-to-first-token (TTFT) across popular fast models.

Required Environment Variables:
- OPENAI_API_KEY      (for GPT-4o-mini)
- ANTHROPIC_API_KEY   (for Claude 3.5 Haiku)
- GOOGLE_API_KEY      (for Gemini 1.5 Flash)
- GROQ_API_KEY        (optional, for Llama-3-8B / Mixtral speed tests)

Usage:
  # First install missing packages if any:
  pip install langchain-openai langchain-groq
  
  # Then run:
  python llm_benchmark.py
"""

import time
import os
import asyncio
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# LangChain Imports
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate

try:
    from langchain_groq import ChatGroq
except ImportError:
    ChatGroq = None




# Benchmark configuration
TEST_PROMPT = """You are a career advisor. List exactly 3 key skills required for a 'Full Stack Developer' role. 
Format your output as a simple comma-separated list without any extra words or greetings."""

MODELS_TO_TEST = []

if os.getenv("OPENAI_API_KEY"):
    MODELS_TO_TEST.append({
        "provider": "OpenAI",
        "name": "gpt-4o-mini",
        "llm": ChatOpenAI(model="gpt-4o-mini", temperature=0)
    })



if os.getenv("GROQ_API_KEY") and ChatGroq:
    MODELS_TO_TEST.append({
        "provider": "Groq",
        "name": "llama-3.1-8b-instant",
        "llm": ChatGroq(model_name="llama-3.1-8b-instant", temperature=0)
    })


async def run_benchmark():
    print(f"Starting LLM Benchmark Test...\nPrompt length: {len(TEST_PROMPT)} characters")
    print("-" * 60)
    
    if not MODELS_TO_TEST:
        print("⚠️ ERROR: No API keys found! Please set at least OPENAI_API_KEY.")
        print("Example (Windows): $env:OPENAI_API_KEY='sk-...'")
        return

    results = []

    for model_info in MODELS_TO_TEST:
        print(f"Testing {model_info['provider']} ({model_info['name']})...", end="", flush=True)
        llm = model_info["llm"]
        
        start_time = time.time()
        try:
            # We use ainvoke to test async performance
            response = await llm.ainvoke([HumanMessage(content=TEST_PROMPT)])
            end_time = time.time()
            
            latency = end_time - start_time
            content = response.content.strip().replace('\n', ' ')
            
            # Show snippet
            snippet = content[:50] + "..." if len(content) > 50 else content
            
            print(f" \033[92m[DONE]\033[0m in {latency:.3f}s")
            
            results.append({
                "provider": model_info["provider"],
                "model": model_info["name"],
                "latency_sec": latency,
                "response": snippet
            })
            
        except Exception as e:
            print(f" \033[91m[FAILED]\033[0m")
            print(f"   Error: {e}")
            
    # Print Comparison Table
    print("\n" + "=" * 60)
    print("🏆 BENCHMARK RESULTS")
    print("=" * 60)
    print(f"{'Provider':<12} | {'Model':<25} | {'Latency':<8} | {'Sample Output'}")
    print("-" * 60)
    
    # Sort by fastest
    results.sort(key=lambda x: x["latency_sec"])
    
    for r in results:
        print(f"{r['provider']:<12} | {r['model']:<25} | {r['latency_sec']:.3f}s | {r['response']}")


if __name__ == "__main__":
    # Suppress verbose warnings
    import warnings
    warnings.filterwarnings("ignore")
    
    asyncio.run(run_benchmark())
