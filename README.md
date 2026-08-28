# AI-Based Knowledge Retrieval Platform

## Overview

This project is being developed as part of my internship. The main goal is to build a platform that can store information from different documents and help users find answers by asking questions in natural language.

The system will support documents such as PDF, DOCX, TXT, and CSV files. After a document is uploaded, its content will be extracted, divided into smaller chunks, converted into embeddings, and stored in a vector database.

When a user asks a question, the system searches the knowledge base for relevant information and uses a RAG-based approach to generate a response.

The project also includes a multi-agent query resolution approach, where different agents handle tasks such as understanding the query, retrieving information, generating responses, asking for clarification, and maintaining conversation context.

---

## Project Flow

### Knowledge Base Ingestion

```text
Upload Document
      ↓
Text Extraction
      ↓
Text Cleaning
      ↓
Chunking
      ↓
Embedding Generation
      ↓
Vector Database
```

### Query Resolution

```text
User Query
      ↓
Query Understanding
      ↓
Check Query Context / Clarity
      ↓
Semantic Search
      ↓
Retrieve Relevant Chunks
      ↓
Generate Response
      ↓
Answer with Source Information
```

---

## Main Components

### 1. Knowledge Base Ingestion

This module is responsible for processing uploaded documents.

Supported formats:

* PDF
* DOCX
* TXT
* CSV

The documents will go through text extraction, cleaning, chunking, embedding generation, and indexing.

### 2. RAG Retrieval Pipeline

The retrieval pipeline searches the indexed knowledge base based on the user's query.

The basic process is:

1. Receive the user query.
2. Convert the query into an embedding.
3. Perform semantic similarity search.
4. Retrieve the most relevant chunks.
5. Use the retrieved content as context for response generation.

### 3. Multi-Agent Query Resolution

The system is planned around the following agents:

* **Query Understanding Agent** – understands the user query and identifies the intent.
* **Retrieval Agent** – searches the vector database for relevant information.
* **Response Generation Agent** – generates the final response using retrieved context.
* **Clarification Agent** – handles incomplete or unclear queries.
* **Conversation Memory Agent** – maintains context from previous interactions.

A central orchestrator manages the flow between these agents.

### 4. Voice Interaction

The project also includes planned support for voice interaction using the Web Speech API.

This includes:

* Speech-to-text for voice queries.
* Text-to-speech for reading responses.

---

## System Architecture

```text
                         USER
                           │
                           ▼
                 ┌─────────────────┐
                 │  User Interface │
                 │ Chat / Upload   │
                 │ Voice Input     │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │  Backend / API  │
                 └────────┬────────┘
                          │
          ┌───────────────┴────────────────┐
          │                                │
          ▼                                ▼
 ┌───────────────────┐          ┌──────────────────────┐
 │ Knowledge Base    │          │ Multi-Agent          │
 │ Ingestion         │          │ Orchestrator         │
 └─────────┬─────────┘          └──────────┬───────────┘
           │                               │
           ▼                               ▼
 ┌───────────────────┐          ┌──────────────────────┐
 │ Document Upload   │          │ Conversation Memory  │
 │ PDF/DOCX/TXT/CSV  │          │ Agent                │
 └─────────┬─────────┘          └──────────┬───────────┘
           │                               │
           ▼                               ▼
 ┌───────────────────┐          ┌──────────────────────┐
 │ Text Extraction   │          │ Query Understanding  │
 │ and Cleaning      │          │ Agent                │
 └─────────┬─────────┘          └──────────┬───────────┘
           │                               │
           ▼                               ▼
 ┌───────────────────┐          ┌──────────────────────┐
 │ Chunking          │          │ Clarification Agent  │
 │ and Metadata      │          └──────────┬───────────┘
 └─────────┬─────────┘                     │
           │                               ▼
           ▼                    ┌──────────────────────┐
 ┌───────────────────┐          │ Retrieval Agent      │
 │ Embedding Model   │─────────►│                      │
 └─────────┬─────────┘          └──────────┬───────────┘
           │                               │
           ▼                               ▼
 ┌───────────────────┐          ┌──────────────────────┐
 │ Vector Database   │◄────────►│ Semantic Search      │
 └───────────────────┘          └──────────┬───────────┘
                                           │
                                           ▼
                                ┌──────────────────────┐
                                │ Response Generation  │
                                │ Agent + LLM          │
                                └──────────┬───────────┘
                                           │
                                           ▼
                                ┌──────────────────────┐
                                │ Response + Sources   │
                                └──────────────────────┘
```

---

## Tech Stack

| Area                   | Technology                       |
| ---------------------- | -------------------------------- |
| Frontend               | React.js                         |
| Backend                | Python, FastAPI                  |
| Retrieval Architecture | RAG                              |
| Agent Workflow         | LangGraph / Custom Orchestration |
| Embeddings             | Sentence Transformers            |
| Vector Store           | ChromaDB                         |
| Metadata Storage       | SQLite                           |
| PDF Processing         | PyPDF                            |
| DOCX Processing        | python-docx                      |
| CSV Processing         | Pandas                           |
| Voice Input            | Web Speech API                   |
| Voice Output           | Web Speech API                   |
| Testing                | Pytest                           |
| Version Control        | Git and GitHub                   |

The technology choices may be updated as the project progresses.

---

## Repository Structure

```text
AI-Knowledge-Retrieval-Platform/
│
├── frontend/
│   └── README.md
│
├── backend/
│   ├── agents/
│   │   ├── query_understanding_agent.py
│   │   ├── retrieval_agent.py
│   │   ├── response_generation_agent.py
│   │   ├── clarification_agent.py
│   │   └── conversation_memory_agent.py
│   │
│   ├── ingestion/
│   │   ├── document_loader.py
│   │   ├── text_extraction.py
│   │   ├── chunking.py
│   │   └── embeddings.py
│   │
│   ├── vector_store/
│   │   └── vector_database.py
│   │
│   └── main.py
│
├── knowledge_base/
│   ├── domain_1/
│   └── domain_2/
│
├── tests/
│   └── retrieval_tests.py
│
├── docs/
│   ├── architecture.md
│   └── tech_stack.md
│
├── README.md
└── requirements.txt
```

---

## Milestone 1

The current milestone focuses on building the foundation of the project.

### Work planned for this milestone

* Study RAG architecture and retrieval pipelines.
* Study embeddings, chunking, semantic similarity, and vector search.
* Understand multi-agent query resolution patterns.
* Design the overall system architecture.
* Define the responsibilities of the different agents.
* Build the document ingestion module.
* Support PDF, DOCX, TXT, and CSV files.
* Generate embeddings and store them in a vector database.
* Build a basic semantic retrieval pipeline.
* Test retrieval performance using knowledge bases from two different domains.
* Evaluate Top-1, Top-3, and Top-5 retrieval accuracy.

---

## Current Status

The project is currently in the initial development stage.

The first phase focuses on:

* Project setup
* Architecture design
* Technology selection
* Research on RAG and multi-agent systems
* Knowledge base ingestion
* Vector indexing
* Retrieval pipeline development

More features and improvements will be added in the upcoming milestones.

---

## Future Work

The project will be expanded in later milestones with features such as:

* Improved multi-agent orchestration
* Better query clarification
* Conversation memory
* Hybrid search
* Response confidence scoring
* Source citations and retrieval transparency
* Query analytics
* Knowledge gap detection
* Knowledge base updates
* Voice-based interaction

---

## Author

**Siddartha Galla**

Internship Project – AI-Based Knowledge Retrieval Platform with Query Resolution System
