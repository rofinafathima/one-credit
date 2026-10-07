from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.database import SessionLocal, DigestRecord, ClaimRecord, VerificationRun
from app.utils.logging import get_logger

logger = get_logger(__name__)

def save_digest_tool(date: str, topic: str, digest: str, verified_claims: List[str]) -> str:
    """Save a generated digest to the database."""
    db = SessionLocal()
    try:
        record = DigestRecord(
            date=date,
            topic=topic,
            content=digest
        )
        db.add(record)
        db.commit()
        return f"Successfully saved digest for {date} on topic {topic}."
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to save digest: {e}")
        return f"Error saving digest: {e}"
    finally:
        db.close()

def get_saved_claims_tool(start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[dict]:
    """Retrieve previously checked claims, optionally filtered by date."""
    db = SessionLocal()
    try:
        query = db.query(ClaimRecord)
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date)
                query = query.filter(ClaimRecord.checked_at >= start_dt)
            except ValueError:
                pass
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date)
                query = query.filter(ClaimRecord.checked_at <= end_dt)
            except ValueError:
                pass
                
        claims = query.all()
        results = []
        for c in claims:
            results.append({
                "id": c.id,
                "claim": c.claim_text,
                "verdict": c.verdict,
                "confidence": c.confidence,
                "date": c.checked_at.isoformat() if c.checked_at else None
            })
        return results
    finally:
        db.close()

def export_markdown_tool(report_type: str, content: str, filename: str) -> str:
    """Export the report as a markdown file to the exports directory."""
    import os
    from pathlib import Path
    
    # Simple path traversal protection
    safe_filename = "".join([c for c in filename if c.isalpha() or c.isdigit() or c in (' ', '.', '-', '_')]).rstrip()
    if not safe_filename.endswith(".md"):
        safe_filename += ".md"
        
    export_dir = Path("data/exports")
    export_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = export_dir / safe_filename
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully exported {report_type} to {file_path}"
    except Exception as e:
        logger.error(f"Export failed: {e}")
        return f"Failed to export: {e}"
