import os
import io
import logging
try:
    import chardet
except ImportError:
    chardet = None
import csv
try:
    import pandas as pd
except ImportError:
    pd = None
from typing import List, Dict, Any, Tuple
from src.ingestion.text_cleaner import clean_text, format_csv_row

logger = logging.getLogger(__name__)

class DocumentParser:
    """
    Unified multi-format document parser supporting PDF, DOCX, TXT, and CSV formats.
    Returns structured page/section level blocks with metadata.
    """
    
    @staticmethod
    def parse_file(file_path: str, filename: str = None, domain: str = "General") -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Parses a file based on its extension.
        Returns:
            - List of content blocks: [{'content': str, 'page_number': int, 'section': str}]
            - Document-level metadata: {'file_name': str, 'file_type': str, 'file_size': int, 'domain': str}
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        file_name = filename or os.path.basename(file_path)
        ext = os.path.splitext(file_name)[1].lower()
        file_size = os.path.getsize(file_path)
        
        doc_metadata = {
            "file_name": file_name,
            "file_type": ext.lstrip("."),
            "file_size_bytes": file_size,
            "domain": domain
        }
        
        if ext == ".pdf":
            blocks = DocumentParser._parse_pdf(file_path)
        elif ext == ".docx":
            blocks = DocumentParser._parse_docx(file_path)
        elif ext == ".txt":
            blocks = DocumentParser._parse_txt(file_path)
        elif ext == ".csv":
            blocks = DocumentParser._parse_csv(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}. Supported formats are .pdf, .docx, .txt, .csv")
            
        return blocks, doc_metadata

    @staticmethod
    def _parse_pdf(file_path: str) -> List[Dict[str, Any]]:
        blocks = []
        # Attempt pdfplumber first for high quality text extraction
        try:
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text() or ""
                    cleaned = clean_text(text)
                    if cleaned:
                        blocks.append({
                            "content": cleaned,
                            "page_number": page_num,
                            "section": f"Page {page_num}"
                        })
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed for {file_path}: {e}. Falling back to pypdf.")
            try:
                from pypdf import PdfReader
                reader = PdfReader(file_path)
                for page_num, page in enumerate(reader.pages, start=1):
                    text = page.extract_text() or ""
                    cleaned = clean_text(text)
                    if cleaned:
                        blocks.append({
                            "content": cleaned,
                            "page_number": page_num,
                            "section": f"Page {page_num}"
                        })
            except Exception as e2:
                logger.error(f"pypdf extraction failed for {file_path}: {e2}")
                raise e2
                
        return blocks

    @staticmethod
    def _parse_docx(file_path: str) -> List[Dict[str, Any]]:
        blocks = []
        try:
            import docx
            doc = docx.Document(file_path)
            current_section = "General"
            current_text_lines = []
            section_page = 1
            
            for para in doc.paragraphs:
                text = para.text.strip()
                if not text:
                    continue
                if para.style and "heading" in para.style.name.lower():
                    if current_text_lines:
                        full_section_text = clean_text("\n".join(current_text_lines))
                        if full_section_text:
                            blocks.append({
                                "content": full_section_text,
                                "page_number": section_page,
                                "section": current_section
                            })
                            current_text_lines = []
                            section_page += 1
                    current_section = text
                else:
                    current_text_lines.append(text)
                    
            if current_text_lines:
                full_section_text = clean_text("\n".join(current_text_lines))
                if full_section_text:
                    blocks.append({
                        "content": full_section_text,
                        "page_number": section_page,
                        "section": current_section
                    })
        except Exception as e:
            logger.error(f"DOCX parsing failed for {file_path}: {e}")
            raise e
            
        return blocks

    @staticmethod
    def _parse_txt(file_path: str) -> List[Dict[str, Any]]:
        blocks = []
        with open(file_path, "rb") as f:
            raw_bytes = f.read()
            
        encoding = "utf-8"
        if chardet is not None:
            detected = chardet.detect(raw_bytes)
            encoding = detected.get("encoding") or "utf-8"
        
        try:
            text = raw_bytes.decode(encoding)
        except Exception:
            text = raw_bytes.decode("utf-8", errors="ignore")
            
        cleaned = clean_text(text)
        # Split into logical sections by double newlines or headers
        paragraphs = cleaned.split("\n\n")
        
        section_idx = 1
        current_chunk_lines = []
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            current_chunk_lines.append(para)
            if len("\n".join(current_chunk_lines)) >= 800:
                blocks.append({
                    "content": "\n\n".join(current_chunk_lines),
                    "page_number": section_idx,
                    "section": f"Section {section_idx}"
                })
                current_chunk_lines = []
                section_idx += 1
                
        if current_chunk_lines:
            blocks.append({
                "content": "\n\n".join(current_chunk_lines),
                "page_number": section_idx,
                "section": f"Section {section_idx}"
            })
            
        return blocks

    @staticmethod
    def _parse_csv(file_path: str) -> List[Dict[str, Any]]:
        blocks = []
        try:
            records = []
            if pd is not None:
                df = pd.read_csv(file_path)
                records = df.to_dict(orient="records")
            else:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    reader = csv.DictReader(f)
                    records = [dict(row) for row in reader]
                    
            group_size = 5
            for i in range(0, len(records), group_size):
                group = records[i:i+group_size]
                formatted_rows = [format_csv_row(row, i + idx) for idx, row in enumerate(group)]
                combined_text = "\n".join(formatted_rows)
                
                blocks.append({
                    "content": clean_text(combined_text),
                    "page_number": (i // group_size) + 1,
                    "section": f"Rows {i+1} to {i+len(group)}"
                })
        except Exception as e:
            logger.error(f"CSV parsing failed for {file_path}: {e}")
            raise e
            
        return blocks
