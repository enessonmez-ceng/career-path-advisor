# 📚 LangGraph Framework Dokümantasyonu

Kod yazarken birebir başvurabileceğiniz kapsamlı LangGraph referans dökümanı. Proje geliştirmeye uygun, detaylı açıklamalar ve kopyala-yapıştır hazır kod örnekleri içerir.

---

## 📑 İçindekiler

1. [Proje Yapısı](#1-proje-yapısı)
2. [State Yönetimi](#2-state-yönetimi)
3. [Node (Düğüm) Sistemi](#3-node-düğüm-sistemi)
4. [Chain Sistemi](#4-chain-sistemi)
5. [Edge ve Routing](#5-edge-ve-routing)
6. [Pydantic Modelleri](#6-pydantic-modelleri)
7. [Vector Store & RAG](#7-vector-store--rag)
8. [Tool Entegrasyonu](#8-tool-entegrasyonu)
9. [Test Yazımı](#9-test-yazımı)
10. [Agent Patternleri](#10-agent-patternleri)
11. [Tam Proje Örneği](#11-tam-proje-örneği)
12. [Import Referansı](#12-import-referansı)
13. [Sık Yapılan Hatalar](#13-sık-yapılan-hatalar)

---

## 1. Proje Yapısı

### Önerilen Klasör Yapısı

```
project/
├── main.py                      # Entry point
├── ingestion.py                 # Döküman yükleme & vector store
├── .env                         # API anahtarları
├── .chroma/                     # Vector store (ChromaDB)
└── graph/
    ├── __init__.py
    ├── graph.py                 # Workflow tanımı (ana dosya)
    ├── state.py                 # State TypedDict
    ├── consts.py                # Node isimleri sabitleri
    ├── chains/                  # LLM zincirleri
    │   ├── __init__.py
    │   ├── generation.py
    │   ├── retrieval_grader.py
    │   ├── hallucination_grader.py
    │   ├── answer_grader.py
    │   ├── router.py
    │   └── tests/
    │       └── test_chains.py
    └── nodes/                   # Graf düğümleri
        ├── __init__.py
        ├── retrieve.py
        ├── grade_documents.py
        ├── generate.py
        └── web_search.py
```

### Dosya Rolleri

| Dosya | Rol | İçerik |
|-------|-----|--------|
| `main.py` | Giriş noktası | Graf çalıştırma, sonuç gösterme |
| `graph.py` | Workflow | Node ekleme, edge tanımlama, compile |
| `state.py` | Durum | TypedDict ile state tanımı |
| `consts.py` | Sabitler | Node isimleri string sabitleri |
| `chains/*.py` | LLM Zincirleri | Prompt + LLM + Parser |
| `nodes/*.py` | Düğümler | State'i alan/döndüren fonksiyonlar |

---

## 2. State Yönetimi

### 2.1 Özel State Tanımı (TypedDict)

```python
# graph/state.py
from typing import List, TypedDict

class GraphState(TypedDict):
    """
    Graf durumunu temsil eder.
    Her alan grafın her aşamasında erişilebilir.
    """
    question: str           # Kullanıcı sorusu
    generation: str         # LLM cevabı
    web_search: bool        # Web araması gerekli mi?
    documents: List[str]    # Döküman listesi
```

**Kullanım:**
```python
from graph.state import GraphState

# Node fonksiyonu
def my_node(state: GraphState) -> Dict[str, Any]:
    question = state["question"]
    # ... işlem
    return {"generation": "Cevap"}
```

### 2.2 MessagesState (Hazır State)

```python
from langgraph.graph import MessagesState

# MessagesState zaten şu yapıya sahip:
# messages: Annotated[list[BaseMessage], add_messages]

def agent_node(state: MessagesState):
    return {"messages": [response]}
```

### 2.3 Annotated ile Mesaj Biriktirme

```python
from typing import Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class ChatState(TypedDict):
    # Mesajlar append edilir (üzerine yazılmaz)
    messages: Annotated[list[BaseMessage], add_messages]
    context: str  # Normal alan (üzerine yazılır)
```

---

## 3. Node (Düğüm) Sistemi

### 3.1 Node Anatomisi

Her node:
1. State'i parametre olarak alır
2. State'in bir kısmını veya tamamını döndürür
3. Döndürülen değerler mevcut state'e merge edilir

```python
# graph/nodes/retrieve.py
from typing import Any, Dict
from graph.state import GraphState
from ingestion import retriever

def retrieve(state: GraphState) -> Dict[str, Any]:
    """
    Dökümanları vector store'dan getirir.
    
    Args:
        state: Mevcut graf durumu
        
    Returns:
        Güncellenmiş state alanları
    """
    print("------Retrieve--------")
    question = state["question"]
    documents = retriever.invoke(question)
    
    return {"documents": documents, "question": question}
```

### 3.2 Node Örnekleri

#### Retrieve Node
```python
def retrieve(state: GraphState) -> Dict[str, Any]:
    print("------Retrieve--------")
    question = state["question"]
    documents = retriever.invoke(question)
    return {"documents": documents, "question": question}
```

#### Grade Documents Node
```python
def grade_documents(state: GraphState) -> Dict[str, Any]:
    """İlgisiz dökümanları filtreler, web_search flag'i set eder."""
    print("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
    question = state["question"]
    documents = state["documents"]

    filtered_docs = []
    web_search = False
    
    for d in documents:
        score = retrieval_grader.invoke({
            "question": question, 
            "document": d.page_content
        })
        grade = score.binary_score
        
        if grade.lower() == "yes":
            print("---GRADE: DOCUMENT RELEVANT---")
            filtered_docs.append(d)
        else:
            print("---GRADE: DOCUMENT NOT RELEVANT---")
            web_search = True
            continue
            
    return {
        "documents": filtered_docs, 
        "question": question, 
        "web_search": web_search
    }
```

#### Generate Node
```python
def generate(state: GraphState) -> Dict[str, Any]:
    print("-----GENERATE-----")
    question = state["question"]
    documents = state["documents"]

    generation = generation_chain.invoke({
        "context": documents, 
        "question": question
    })
    
    return {
        "documents": documents,
        "question": question, 
        "generation": generation
    }
```

#### Web Search Node
```python
from langchain_core.documents import Document
from langchain_tavily import TavilySearch

web_search_tool = TavilySearch(max_results=3)

def web_search(state: GraphState) -> Dict[str, Any]:
    print("---WEB SEARCH---")
    question = state["question"]
    documents = state["documents"]

    tavily_results = web_search_tool.invoke({"query": question})["results"]
    joined_tavily_result = "\n".join(
        [tavily_result["content"] for tavily_result in tavily_results]
    )
    web_results = Document(page_content=joined_tavily_result)
    
    if documents is not None:
        documents.append(web_results)
    else:
        documents = [web_results]
        
    return {"documents": documents, "question": question}
```

### 3.3 Node Export (__init__.py)

```python
# graph/nodes/__init__.py
from graph.nodes.generate import generate
from graph.nodes.grades_documents import grade_documents
from graph.nodes.retrieve import retrieve
from graph.nodes.web_search import web_search

__all__ = ["generate", "grade_documents", "retrieve", "web_search"]
```

**Kullanım:**
```python
from graph.nodes import generate, grade_documents, retrieve, web_search
```

---

## 4. Chain Sistemi

### 4.1 Chain Anatomisi

Chain = **Prompt** | **LLM** | **Parser**

```python
chain = prompt | llm | parser
result = chain.invoke({"key": "value"})
```

### 4.2 Temel Generation Chain

```python
# graph/chains/generation.py
from langsmith import Client
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
client = Client()
prompt = client.pull_prompt("rlm/rag-prompt")

generation_chain = prompt | llm | StrOutputParser()
```

**Kullanım:**
```python
result = generation_chain.invoke({
    "context": documents, 
    "question": "What is X?"
})
print(result)  # String cevap
```

### 4.3 Structured Output Chain (Grader)

```python
# graph/chains/retrieval_grader.py
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

class GradeDocuments(BaseModel):
    """Binary score for relevance check."""
    binary_score: str = Field(
        description="Documents are relevant to the question, 'yes' or 'no'"
    )

structured_llm_grader = llm.with_structured_output(GradeDocuments)

system = """You are a grader assessing relevance of a retrieved document to a user question.
If the document contains keyword(s) or semantic meaning related to the question, grade it as relevant.
Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."""

grade_prompt = ChatPromptTemplate.from_messages([
    ("system", system),
    ("human", "Retrieved document: \n\n {document} \n\n User question: {question}"),
])

retrieval_grader = grade_prompt | structured_llm_grader
```

**Kullanım:**
```python
result = retrieval_grader.invoke({
    "document": doc.page_content,
    "question": "What is agent memory?"
})
print(result.binary_score)  # "yes" veya "no"
```

### 4.4 Hallucination Grader

```python
# graph/chains/hallucination_grader.py
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_core.runnables import RunnableSequence
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(temperature=0)

class GradeHallucinations(BaseModel):
    """Binary score for hallucination present in generation answer."""
    binary_score: bool = Field(
        description="Answer is grounded in the facts, 'yes' or 'no'"
    )

structured_llm_grader = llm.with_structured_output(GradeHallucinations)

system = """You are a grader assessing whether an LLM generation is grounded in / supported by a set of retrieved facts.
Give a binary score 'yes' or 'no'. 'Yes' means that the answer is grounded in / supported by the set of facts."""

hallucination_prompt = ChatPromptTemplate.from_messages([
    ("system", system),
    ("human", "Set of facts: \n\n {documents} \n\n LLM generation: {generation}"),
])

hallucination_grader: RunnableSequence = hallucination_prompt | structured_llm_grader
```

**Kullanım:**
```python
result = hallucination_grader.invoke({
    "documents": docs,
    "generation": "Agent memory is..."
})
print(result.binary_score)  # True veya False
```

### 4.5 Answer Grader

```python
# graph/chains/answer_grader.py
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_core.runnables import RunnableSequence
from langchain_openai import ChatOpenAI

class GradeAnswer(BaseModel):
    binary_score: bool = Field(
        description="Answer addresses the question, 'yes' or 'no'"
    )

llm = ChatOpenAI(temperature=0)
structured_llm_grader = llm.with_structured_output(GradeAnswer)

system = """You are a grader assessing whether an answer addresses / resolves a question.
Give a binary score 'yes' or 'no'. Yes' means that the answer resolves the question."""

answer_prompt = ChatPromptTemplate.from_messages([
    ("system", system),
    ("human", "User question: \n\n {question} \n\n LLM generation: {generation}"),
])

answer_grader: RunnableSequence = answer_prompt | structured_llm_grader
```

### 4.6 Question Router

```python
# graph/chains/router.py
from typing import Literal
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI

class RouteQuery(BaseModel):
    """Route a user query to the most relevant datasource."""
    datasource: Literal["vectorstore", "websearch"] = Field(
        ...,
        description="Given a user question choose to route it to web search or a vectorstore.",
    )

llm = ChatOpenAI(temperature=0)
structured_llm_router = llm.with_structured_output(RouteQuery)

system = """You are an expert at routing a user question to a vectorstore or web search.
The vectorstore contains documents related to agents, prompt engineering, and adversarial attacks.
Use the vectorstore for questions on these topics. For all else, use web-search."""

route_prompt = ChatPromptTemplate.from_messages([
    ("system", system),
    ("human", "{question}"),
])

question_router = route_prompt | structured_llm_router
```

**Kullanım:**
```python
result = question_router.invoke({"question": "What is agent memory?"})
print(result.datasource)  # "vectorstore" veya "websearch"
```

---

## 5. Edge ve Routing

### 5.1 Normal Edge

```python
workflow.add_edge("node_a", "node_b")
workflow.add_edge("node_b", END)
```

### 5.2 Koşullu Edge

```python
def decide_to_generate(state: GraphState) -> str:
    """State'e göre sonraki node'u belirle."""
    print("---ASSESS GRADED DOCUMENTS---")
    
    if state["web_search"]:
        print("---DECISION: INCLUDE WEB SEARCH---")
        return WEBSEARCH
    else:
        print("---DECISION: GENERATE---")
        return GENERATE

workflow.add_conditional_edges(
    GRADE_DOCUMENTS,          # Kaynak node
    decide_to_generate,        # Karar fonksiyonu
    {
        WEBSEARCH: WEBSEARCH,  # Olası hedefler
        GENERATE: GENERATE,
    },
)
```

### 5.3 Çoklu Koşullu Edge (Hallucination Check)

```python
def grade_generation_grounded_in_documents_and_question(state: GraphState) -> str:
    """Cevabın kalitesini değerlendir ve sonraki adımı belirle."""
    print("---CHECK HALLUCINATIONS---")
    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]

    # Hallucination kontrolü
    score = hallucination_grader.invoke({
        "documents": documents, 
        "generation": generation
    })

    if hallucination_grade := score.binary_score:
        print("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")
        print("---GRADE GENERATION vs QUESTION---")
        
        # Cevap kalitesi kontrolü
        score = answer_grader.invoke({
            "question": question, 
            "generation": generation
        })
        
        if answer_grade := score.binary_score:
            print("---DECISION: GENERATION ADDRESSES QUESTION---")
            return "useful"
        else:
            print("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
            return "not useful"
    else:
        print("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---")
        return "not supported"

workflow.add_conditional_edges(
    GENERATE,
    grade_generation_grounded_in_documents_and_question,
    {
        "not supported": GENERATE,  # Tekrar dene
        "useful": END,              # Bitir
        "not useful": WEBSEARCH,    # Web araması yap
    },
)
```

### 5.4 Conditional Entry Point (Router)

```python
def route_question(state: GraphState) -> str:
    """Soruyu uygun kaynağa yönlendir."""
    print("---ROUTE QUESTION---")
    question = state["question"]
    source: RouteQuery = question_router.invoke({"question": question})
    
    if source.datasource == WEBSEARCH:
        print("---ROUTE QUESTION TO WEB SEARCH---")
        return WEBSEARCH
    elif source.datasource == "vectorstore":
        print("---ROUTE QUESTION TO RAG---")
        return RETRIEVE

workflow.set_conditional_entry_point(
    route_question,
    {
        WEBSEARCH: WEBSEARCH,
        RETRIEVE: RETRIEVE,
    },
)
```

---

## 6. Pydantic Modelleri

### 6.1 Temel Model

```python
from pydantic import BaseModel, Field

class GradeDocuments(BaseModel):
    """Docstring tool description olarak kullanılır."""
    
    binary_score: str = Field(
        description="'yes' veya 'no'"
    )
```

### 6.2 Bool vs Str Karşılaştırması

```python
# String döndür (grader'larda önerilen)
class GradeDocuments(BaseModel):
    binary_score: str = Field(description="'yes' or 'no'")

# Kullanım
if result.binary_score.lower() == "yes":
    ...

# Boolean döndür (direkt kontrol)
class GradeHallucinations(BaseModel):
    binary_score: bool = Field(description="True if grounded")

# Kullanım
if result.binary_score:
    ...
```

### 6.3 Literal Tip ile Kısıtlama

```python
from typing import Literal

class RouteQuery(BaseModel):
    datasource: Literal["vectorstore", "websearch"] = Field(
        ...,  # Zorunlu alan
        description="Route to web search or vectorstore"
    )
```

### 6.4 İç İçe Modeller

```python
class Reflection(BaseModel):
    missing: str = Field(description="Eksik bilgi")
    superfluous: str = Field(description="Gereksiz bilgi")

class AnswerQuestion(BaseModel):
    answer: str = Field(description="Cevap")
    reflection: Reflection = Field(description="Özeleştiri")
    search_queries: List[str] = Field(description="Arama sorguları")

class ReviseAnswer(AnswerQuestion):
    """Kalıtım ile genişletme."""
    references: List[str] = Field(description="Kaynaklar")
```

---

## 7. Vector Store & RAG

### 7.1 Document Ingestion

```python
# ingestion.py
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import OpenAIEmbeddings

load_dotenv()

# 1. URL'lerden döküman yükle
urls = [
    "https://lilianweng.github.io/posts/2023-06-23-agent/",
    "https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/",
]

docs = [WebBaseLoader(url).load() for url in urls]
docs_list = [item for sublist in docs for item in sublist]

# 2. Dökümanları parçala
text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=250, 
    chunk_overlap=0
)
doc_splits = text_splitter.split_documents(docs_list)

# 3. Vector store oluştur (ilk seferde)
# vectorstore = Chroma.from_documents(
#     documents=doc_splits,
#     collection_name="rag-chroma",
#     embedding=OpenAIEmbeddings(),
#     persist_directory="./.chroma",
# )

# 4. Mevcut vector store'dan retriever oluştur
retriever = Chroma(
    collection_name="rag-chroma",
    persist_directory="./.chroma",
    embedding_function=OpenAIEmbeddings(),
).as_retriever()
```

### 7.2 Retriever Kullanımı

```python
from ingestion import retriever

# Sorguya göre döküman getir
docs = retriever.invoke("What is agent memory?")

for doc in docs:
    print(doc.page_content)  # Döküman içeriği
    print(doc.metadata)      # Metadata
```

---

## 8. Tool Entegrasyonu

### 8.1 Tool Tanımlama

```python
from langchain_core.tools import tool

@tool
def multiply(a: float, b: float) -> float:
    """İki sayıyı çarpar."""
    return a * b
```

### 8.2 Tavily Search

```python
from langchain_tavily import TavilySearch

web_search_tool = TavilySearch(max_results=3)

results = web_search_tool.invoke({"query": "What is LangGraph?"})
for result in results["results"]:
    print(result["content"])
```

### 8.3 LLM'e Tool Bağlama

```python
from langchain_openai import ChatOpenAI

tools = [TavilySearch(max_results=1), multiply]
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Tools'u LLM'e bağla
llm_with_tools = llm.bind_tools(tools)

# Belirli tool'u zorla
llm_forced = llm.bind_tools(
    tools=[MySchema], 
    tool_choice="MySchema"
)
```

### 8.4 ToolNode

```python
from langgraph.prebuilt import ToolNode

tool_node = ToolNode(tools)
workflow.add_node("execute_tools", tool_node)
```

---

## 9. Test Yazımı

### 9.1 Test Dosyası Yapısı

```python
# graph/chains/tests/test_chains.py
from dotenv import load_dotenv
from pprint import pprint
load_dotenv()

from graph.chains.retrieval_grader import GradeDocuments, retrieval_grader
from graph.chains.generation import generation_chain
from graph.chains.hallucination_grader import hallucination_grader, GradeHallucinations
from graph.chains.router import question_router, RouteQuery
from ingestion import retriever
```

### 9.2 Retrieval Grader Testleri

```python
def test_retrieval_grader_answer_yes() -> None:
    """İlgili döküman 'yes' döndürmeli."""
    question = "agent memory"
    docs = retriever.invoke(question)
    doc_txt = docs[1].page_content

    res: GradeDocuments = retrieval_grader.invoke({
        "question": question, 
        "document": doc_txt
    })
    
    assert res.binary_score == "yes"


def test_retrieval_grader_answer_no() -> None:
    """İlgisiz döküman 'no' döndürmeli."""
    question = "agent memory"
    docs = retriever.invoke(question)
    doc_txt = docs[1].page_content

    res: GradeDocuments = retrieval_grader.invoke({
        "question": "how to make pizza", 
        "document": doc_txt
    })
    
    assert res.binary_score == "no"
```

### 9.3 Hallucination Grader Testleri

```python
def test_hallucination_grader_answer_yes() -> None:
    """Gerçeklere dayalı cevap True döndürmeli."""
    question = "agent memory"
    docs = retriever.invoke(question)
    generation = generation_chain.invoke({
        "context": docs, 
        "question": question
    })
    
    res: GradeHallucinations = hallucination_grader.invoke({
        "documents": docs, 
        "generation": generation
    })
    
    assert res.binary_score


def test_hallucination_grader_answer_no() -> None:
    """Uydurma cevap False döndürmeli."""
    question = "agent memory"
    docs = retriever.invoke(question)

    res: GradeHallucinations = hallucination_grader.invoke({
        "documents": docs,
        "generation": "In order to make pizza we need to start with the dough",
    })
    
    assert not res.binary_score
```

### 9.4 Router Testleri

```python
def test_router_to_vectorstore() -> None:
    """Bilinen konu vectorstore'a yönlenmeli."""
    question = "agent memory"
    res: RouteQuery = question_router.invoke({"question": question})
    assert res.datasource == "vectorstore"


def test_router_to_websearch() -> None:
    """Bilinmeyen konu websearch'e yönlenmeli."""
    question = "how to make pizza"
    res: RouteQuery = question_router.invoke({"question": question})
    assert res.datasource == "websearch"
```

### 9.5 Test Çalıştırma

```bash
# Tüm testler
poetry run python -m pytest graph/chains/tests/test_chains.py -v

# Tek test
poetry run python -m pytest graph/chains/tests/test_chains.py::test_router_to_vectorstore -v

# Verbose output
poetry run python -m pytest -v -s
```

---

## 10. Agent Patternleri

### Pattern 1: ReAct (Reasoning + Acting)

```
Akış: Agent → Tool → Agent → Tool → ... → END
```

```python
from langgraph.graph import MessagesState, StateGraph, END
from langgraph.prebuilt import ToolNode

def should_continue(state: MessagesState) -> str:
    if not state["messages"][-1].tool_calls:
        return END
    return "tools"

workflow = StateGraph(MessagesState)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", ToolNode(tools))
workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue, {END: END, "tools": "tools"})
workflow.add_edge("tools", "agent")
```

---

### Pattern 2: Reflection

```
Akış: Generate → Reflect → Generate → ... (N iterasyon)
```

```python
def should_continue(state):
    if len(state["messages"]) > 6:
        return END
    return "reflect"

workflow.add_conditional_edges("generate", should_continue)
workflow.add_edge("reflect", "generate")
```

---

### Pattern 3: Reflexion (Araştırmalı)

```
Akış: Draft → Execute Tools → Revise → Execute Tools → ...
```

```python
MAX_ITERATIONS = 2

def event_loop(state) -> Literal["execute_tools", END]:
    tool_visits = sum(isinstance(m, ToolMessage) for m in state["messages"])
    if tool_visits > MAX_ITERATIONS:
        return END
    return "execute_tools"

workflow.add_edge(START, "draft")
workflow.add_edge("draft", "execute_tools")
workflow.add_edge("execute_tools", "revise")
workflow.add_conditional_edges("revise", event_loop)
```

---

### Pattern 4: Self-Corrective RAG (Tam Örnek)

```
Akış: Route → Retrieve → Grade → [WebSearch] → Generate → Check → END
```

```python
from langgraph.graph import END, StateGraph
from graph.consts import RETRIEVE, GRADE_DOCUMENTS, GENERATE, WEBSEARCH
from graph.nodes import generate, grade_documents, retrieve, web_search
from graph.state import GraphState
from graph.chains.answer_grader import answer_grader
from graph.chains.hallucination_grader import hallucination_grader
from graph.chains.router import question_router, RouteQuery

# Karar fonksiyonları
def decide_to_generate(state):
    if state["web_search"]:
        return WEBSEARCH
    return GENERATE

def grade_generation_grounded_in_documents_and_question(state):
    score = hallucination_grader.invoke({
        "documents": state["documents"], 
        "generation": state["generation"]
    })
    if score.binary_score:
        score = answer_grader.invoke({
            "question": state["question"], 
            "generation": state["generation"]
        })
        if score.binary_score:
            return "useful"
        return "not useful"
    return "not supported"

def route_question(state):
    source = question_router.invoke({"question": state["question"]})
    if source.datasource == "websearch":
        return WEBSEARCH
    return RETRIEVE

# Workflow oluştur
workflow = StateGraph(GraphState)

# Node'ları ekle
workflow.add_node(RETRIEVE, retrieve)
workflow.add_node(GRADE_DOCUMENTS, grade_documents)
workflow.add_node(GENERATE, generate)
workflow.add_node(WEBSEARCH, web_search)

# Conditional entry point
workflow.set_conditional_entry_point(route_question, {
    WEBSEARCH: WEBSEARCH,
    RETRIEVE: RETRIEVE,
})

# Edge'leri ekle
workflow.add_edge(RETRIEVE, GRADE_DOCUMENTS)
workflow.add_conditional_edges(GRADE_DOCUMENTS, decide_to_generate, {
    WEBSEARCH: WEBSEARCH,
    GENERATE: GENERATE,
})
workflow.add_conditional_edges(GENERATE, grade_generation_grounded_in_documents_and_question, {
    "not supported": GENERATE,
    "useful": END,
    "not useful": WEBSEARCH,
})
workflow.add_edge(WEBSEARCH, GENERATE)

# Compile
app = workflow.compile()
```

---

## 11. Tam Proje Örneği

### main.py

```python
from dotenv import load_dotenv
load_dotenv()

from graph.graph import app

if __name__ == "__main__":
    print("Hello Advanced RAG")
    result = app.invoke(input={"question": "what is agent memory?"})
    
    print("\n" + "="*50)
    print("📝 FINAL ANSWER:")
    print("="*50)
    print(result["generation"])
```

### Çalıştırma

```bash
# Program çalıştır
poetry run python main.py

# Testleri çalıştır
poetry run python -m pytest graph/chains/tests/test_chains.py -v

# Graf görselleştir
# graph.py çalışınca graph.png oluşur
```

---

## 12. Import Referansı

```python
# ======== LANGGRAPH ========
from langgraph.graph import StateGraph, END, START
from langgraph.graph import MessagesState
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

# ======== LANGCHAIN CORE ========
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import tool, StructuredTool
from langchain_core.documents import Document
from langchain_core.runnables import RunnableSequence

# ======== LANGCHAIN OPENAI ========
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# ======== LANGCHAIN COMMUNITY ========
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_tavily import TavilySearch

# ======== LANGSMITH ========
from langsmith import Client

# ======== PYDANTIC ========
from pydantic import BaseModel, Field

# ======== TYPING ========
from typing import TypedDict, Annotated, List, Dict, Any, Literal

# ======== ENVIRONMENT ========
from dotenv import load_dotenv
load_dotenv()
```

---

## 13. Sık Yapılan Hatalar

### ❌ State Key Hatası
```python
# Yanlış
question = state["messages"]  # KeyError

# Doğru - State tanımına bak
question = state["question"]
```

### ❌ Pydantic Field Tipi Eksik
```python
# Yanlış
binary_score = Field(description="...")

# Doğru
binary_score: str = Field(description="...")
```

### ❌ Dict Tip Annotation
```python
# Yanlış
def node(state) -> Dict[str:Any]:

# Doğru - virgül kullan
def node(state) -> Dict[str, Any]:
```

### ❌ Eski Import Yolları
```python
# Yanlış (LangChain v0.1)
from langchain.schema import Document

# Doğru (LangChain v0.2+)
from langchain_core.documents import Document
```

### ❌ Çift Entry Point
```python
# Yanlış - ikisini birden kullanma
workflow.set_conditional_entry_point(...)
workflow.set_entry_point(RETRIEVE)

# Doğru - birini seç
workflow.set_conditional_entry_point(route_question, {...})
# VEYA
workflow.set_entry_point(RETRIEVE)
```

### ❌ Structured Output Model Uyumsuzluğu
```python
# gpt-3.5-turbo structured output desteklemez
llm = ChatOpenAI(model="gpt-3.5-turbo")  # Hata verir

# Doğru
llm = ChatOpenAI(model="gpt-4o-mini")  # veya gpt-4o
```

---

## 📚 Kaynaklar

- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [LangChain Docs](https://python.langchain.com/)
- [LangSmith Hub](https://smith.langchain.com/hub)
- [Pydantic Docs](https://docs.pydantic.dev/)
