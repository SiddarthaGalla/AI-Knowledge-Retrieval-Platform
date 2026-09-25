import os
import uuid
import logging
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.ingestion.document_parsers import DocumentParser
from src.ingestion.chunker import RecursiveChunker
from src.vectorstore.chroma_indexer import VectorStoreManager
from src.pipeline.rag_pipeline import RAGPipelineOrchestrator
from evaluation.evaluate_retrieval import RAGEvaluationRunner

# Logging Configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("main")

app = FastAPI(
    title="AI-Based Knowledge Retrieval Platform",
    description="Multi-Agent RAG Query Resolution Engine with Web Speech API & Multi-Domain Retrieval",
    version="1.0.0"
)

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Instances
vector_store = VectorStoreManager(persist_directory="./data/vector_store")
chunker = RecursiveChunker(chunk_size=500, chunk_overlap=100)
orchestrator = RAGPipelineOrchestrator(vector_store)
eval_runner = RAGEvaluationRunner(vector_store)

# Ensure uploaded files directory exists
UPLOAD_DIR = "./data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Pydantic Schemas
class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = "default_session"
    domain_filter: Optional[str] = "all"

@app.on_event("startup")
async def startup_event():
    logger.info("Initializing AI Knowledge Retrieval Platform Gateway...")
    # Pre-seed evaluation datasets if vector store is empty
    stats = vector_store.get_stats()
    if stats["total_documents"] == 0:
        logger.info("Vector store is empty. Pre-seeding Healthcare & Finance sample datasets...")
        try:
            eval_runner.prepare_sample_datasets()
        except Exception as e:
            logger.warning(f"Pre-seeding warning: {e}")

# Static directory setup
static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(static_path, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    index_file = os.path.join(static_path, "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>AI Knowledge Retrieval Platform API Running</h1><p>UI loading...</p>"

@app.get("/api/stats")
async def get_stats():
    """
    Returns total document, chunk, vector counts and domain breakdown.
    """
    stats = vector_store.get_stats()
    return {
        "status": "success",
        "data": stats
    }

@app.get("/api/documents")
async def get_documents():
    """
    Returns list of all indexed knowledge base documents.
    """
    docs = vector_store.get_documents()
    return {
        "status": "success",
        "documents": docs,
        "count": len(docs)
    }

@app.post("/api/ingest")
async def ingest_document(
    file: UploadFile = File(...),
    domain: str = Form("General"),
    chunk_size: int = Form(500),
    chunk_overlap: int = Form(100)
):
    """
    Uploads and ingests PDF, DOCX, TXT, or CSV document into vector store.
    """
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in [".pdf", ".docx", ".txt", ".csv"]:
        raise HTTPException(status_code=400, detail=f"Unsupported file format '{file_ext}'. Supported: .pdf, .docx, .txt, .csv")
        
    doc_id = f"doc_{uuid.uuid4().hex[:8]}"
    save_path = os.path.join(UPLOAD_DIR, f"{doc_id}_{file.filename}")
    
    try:
        contents = await file.read()
        with open(save_path, "wb") as f:
            f.write(contents)
            
        blocks, doc_meta = DocumentParser.parse_file(save_path, filename=file.filename, domain=domain)
        doc_meta["document_id"] = doc_id
        
        custom_chunker = RecursiveChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        chunks = custom_chunker.chunk_document(blocks, doc_id, doc_meta)
        
        doc_meta["total_chunks"] = len(chunks)
        doc_meta["status"] = "indexed"
        
        vector_store.add_document_and_chunks(doc_meta, chunks)
        
        return {
            "status": "success",
            "message": f"Successfully ingested {file.filename}",
            "document": doc_meta,
            "chunks_created": len(chunks)
        }
    except Exception as e:
        logger.error(f"Ingestion failed for {file.filename}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Document ingestion failed: {str(e)}")

@app.delete("/api/documents/{doc_id}")
async def delete_document(doc_id: str):
    success = vector_store.delete_document(doc_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found.")
    return {"status": "success", "message": f"Deleted document {doc_id}"}

class RefineQueryRequest(BaseModel):
    session_id: str
    clarification_response: str
    domain_filter: Optional[str] = "all"

@app.post("/api/query")
async def execute_query(payload: QueryRequest):
    """
    Executes query through the 5-Agent RAG Orchestration engine.
    """
    if not payload.query or not payload.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
        
    try:
        result = orchestrator.run_query(
            user_query=payload.query,
            session_id=payload.session_id,
            domain_filter=payload.domain_filter
        )
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"Query resolution error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Query execution failed: {str(e)}")

@app.post("/api/query/refine")
async def refine_query(payload: RefineQueryRequest):
    """
    Refines an ambiguous/multi-part query using clarification feedback (M3.1).
    """
    if not payload.clarification_response or not payload.clarification_response.strip():
        raise HTTPException(status_code=400, detail="Clarification response cannot be empty.")
        
    try:
        result = orchestrator.run_refinement(
            session_id=payload.session_id,
            clarification_response=payload.clarification_response,
            domain_filter=payload.domain_filter
        )
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"Query refinement error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Query refinement failed: {str(e)}")

@app.get("/api/session/{session_id}")
async def get_session_memory(session_id: str):
    """
    Returns session history logs and tracked entities (M3.2).
    """
    history = orchestrator.memory_agent.get_history(session_id)
    entities = orchestrator.memory_agent.session_entities.get(session_id, [])
    docs = orchestrator.memory_agent.session_docs.get(session_id, [])
    return {
        "status": "success",
        "session_id": session_id,
        "history": history,
        "tracked_entities": entities,
        "tracked_documents": docs
    }

@app.post("/api/evaluate")
async def run_evaluation_benchmark():
    """
    Triggers multi-domain retrieval accuracy validation test suite.
    """
    try:
        results = eval_runner.run_evaluation()
        return {
            "status": "success",
            "evaluation": results
        }
    except Exception as e:
        logger.error(f"Evaluation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
