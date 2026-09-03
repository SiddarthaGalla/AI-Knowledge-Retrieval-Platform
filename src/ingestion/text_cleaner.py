import re
import unicodedata

def clean_text(text: str) -> str:
    """
    Normalizes and cleans raw text extracted from documents.
    """
    if not text:
        return ""
    
    # Normalize unicode characters (NFC form)
    text = unicodedata.normalize("NFC", text)
    
    # Replace non-breaking spaces and special whitespace
    text = text.replace("\u00a0", " ").replace("\r\n", "\n").replace("\r", "\n")
    
    # Replace weird quotes and bullet symbols
    text = text.replace("“", '"').replace("”", '"').replace("’", "'").replace("‘", "'")
    text = text.replace("•", "- ").replace("▪", "- ").replace("►", "- ")
    
    # Replace multiple horizontal spaces with a single space
    text = re.sub(r"[ \t]+", " ", text)
    
    # Replace 3 or more consecutive newlines with 2 newlines
    text = re.sub(r"\n{3,}", "\n\n", text)
    
    return text.strip()


def format_csv_row(row_dict: dict, row_idx: int) -> str:
    """
    Formats a single CSV record into structured semantic text for chunking.
    """
    items = []
    for k, v in row_dict.items():
        if v is not None and str(v).strip() != "" and str(v).strip().lower() != "nan":
            items.append(f"{k}: {str(v).strip()}")
    return f"Record {row_idx + 1}: " + " | ".join(items)
