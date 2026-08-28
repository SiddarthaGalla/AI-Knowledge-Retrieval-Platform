# Technology Stack & Architectural Rationale

![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-green.svg)
![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-purple.svg)
![Vector DB](https://img.shields.io/badge/VectorDB-ChromaDB%20%7C%20FAISS-orange.svg)
![Speech API](https://img.shields.io/badge/Web%20Speech-STT%20%26%20TTS-brightgreen.svg)

---

## 📌 Overview

This document outlines the complete technology stack, design rationale, component responsibilities, and architectural trade-offs for the **AI-Based Knowledge Retrieval Platform with Query Resolution System** (Milestone 1).

---

## 🛠️ Technology Stack Breakdown

### 🌐 1. Frontend & Voice Interface Layer

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **User Interface** | HTML5, CSS3, JavaScript (React / Vanilla JS) | Provides a responsive, fast-loading, dynamic web interface for document uploads, chat interaction, and retrieval transparency dashboards. |
| **Speech-to-Text (STT)** | Web Speech API (`SpeechRecognition` / `webkitSpeechRecognition`) | Enables native browser-based voice input processing without third-party speech API costs or external latency. |
| **Text-to-Speech (TTS)** | Web Speech API (`SpeechSynthesis`) | Provides browser-native voice synthesis to read generated AI answers back to the user seamlessly. |

---

### ⚡ 2. Backend API & Gateway Layer

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **Language Runtime** | Python 3.10+ | Standard ecosystem for AI/ML development, vector store integrations, and data processing libraries. |
| **Web Framework** | FastAPI (v0.110+) | High-performance asynchronous REST & WebSocket framework with native type checking and automatic OpenAPI/Swagger documentation. |
| **ASGI Server** | Uvicorn | Lightweight, lightning-fast asynchronous web server implementation for Python. |
| **Data Validation** | Pydantic (v2) | Strict schema validation, automatic data parsing, and serialization for request payloads and agent data structures. |

---

### 🤖 3. Multi-Agent Orchestration & LLM Layer

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **Multi-Agent Orchestrator** | LangGraph | State machine engine designed for complex multi-agent workflows, state persistence, conditional branching, and agent coordination. |
| **LLM Framework** | LangChain Core & Community | Standardized abstractions for tools, prompt templates, document loaders, and vector store retriever chains. |
| **Foundation Models** | OpenAI (`gpt-4o` / `gpt-4o-mini`) or Google (`gemini-1.5-flash`) | State-of-the-art reasoning capability for intent extraction, response synthesis, and clarification generation. |

#### 5-Agent Architecture Breakdown:
1. **Query Understanding Agent**: Extracts query intent, identifies key entities, and performs query expansion (HyDE).
2. **Retrieval Agent**: Coordinates dense vector similarity search and sparse metadata filtering.
3. **Response Generation Agent**: Synthesizes grounded answers strictly using retrieved chunks and generates exact citations.
4. **Clarification Agent**: Evaluates retrieval confidence; triggers follow-up queries if similarity score is below threshold (<0.65).
5. **Conversation Memory Agent**: Manages multi-turn conversation context, resolves coreferences, and maintains chat history.

---

### 📄 4. Knowledge Base Ingestion & Processing Module

| Component | Format | Parser / Tool | Purpose |
| :--- | :--- | :--- | :--- |
| **PDF Parser** | `.pdf` | `pypdf` / `pdfplumber` | Extracts structured text, layout, and page-level attribution metadata. |
| **DOCX Parser** | `.docx` | `python-docx` | Parses Word document headings, paragraphs, and lists. |
| **CSV / Tabular Parser** | `.csv` | `pandas` + `openpyxl` | Converts structured spreadsheet data into semantically indexed text chunks. |
| **TXT Parser** | `.txt` | `chardet` + native file readers | Handles plain text ingestion with automatic character encoding detection. |
| **Chunking Engine** | All Formats | `RecursiveCharacterTextSplitter` | Partitions document text into 500-token chunks with 100-token overlap to maintain semantic continuity. |

---

### 🗄️ 5. Embedding & Vector Database Layer

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **Embedding Generator** | OpenAI `text-embedding-3-small` / HuggingFace `all-MiniLM-L6-v2` | Transforms textual chunks into 1536-dimensional or 384-dimensional dense semantic vectors. |
| **Primary Vector DB** | ChromaDB | Lightweight, open-source vector store supporting local persistence, metadata filtering, and HNSW indexing. |
| **In-Memory Index** | FAISS (Facebook AI Similarity Search) | High-speed vector similarity search engine for rapid evaluation benchmarks. |
| **Similarity Metric** | Cosine Similarity / Dot Product | Standard distance metrics for ranking semantic vector proximity. |

---

### 📊 6. RAG Retrieval Evaluation & Analytics Layer

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **RAG Evaluation Suite** | Ragas | Framework for evaluating RAG pipelines across Context Precision, Context Recall, Faithfulness, and Answer Relevance. |
| **Statistical Metrics** | Scikit-Learn + NumPy | Computes Top-1, Top-3, Top-5 retrieval accuracy, Mean Reciprocal Rank (MRR), and similarity score distributions. |
| **Citation Engine** | Custom Citation & Confidence Module | Ensures answer traceability by linking response sentences to source document ID, page number, and chunk ID. |

---

## 📋 Comprehensive Technology Summary Table

```
+-------------------------------------------------------------------------------+
|                        PROJECT TECHNOLOGY STACK MATRIX                        |
+----------------------+--------------------------------------------------------+
| Layer                | Selected Technologies                                  |
+----------------------+--------------------------------------------------------+
| User Interface       | HTML5, CSS3, JavaScript, Web Speech API (STT & TTS)    |
| API & Gateway        | Python 3.10+, FastAPI, Uvicorn, Pydantic v2            |
| Agent Orchestration  | LangGraph, LangChain Core & Community                  |
| LLM Foundation Models| OpenAI GPT-4o / GPT-4o-mini / Google Gemini 1.5       |
| Ingestion & Extraction| pypdf, pdfplumber, python-docx, pandas, chardet        |
| Text Chunking        | RecursiveCharacterTextSplitter (Size: 500, Overlap: 100)|
| Embeddings           | OpenAI text-embedding-3-small / HuggingFace MiniLM     |
| Vector Database      | ChromaDB, FAISS                                        |
| Evaluation & Testing | Ragas, Scikit-Learn, NumPy, Datasets                   |
+----------------------+--------------------------------------------------------+
```

---

## 🔗 Dependency Mapping

All required libraries are defined in [`requirements.txt`](../requirements.txt):

```text
fastapi>=0.110.0
uvicorn[standard]>=0.28.0
pydantic>=2.6.0
langchain>=0.1.14
langgraph>=0.0.30
chromadb>=0.4.24
faiss-cpu>=1.8.0
sentence-transformers>=2.6.1
pypdf>=4.1.0
pdfplumber>=0.11.0
python-docx>=1.1.0
pandas>=2.2.1
ragas>=0.1.7
```
