from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from app.config import settings
import datetime

Base = declarative_base()
engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class VerificationRun(Base):
    __tablename__ = "verification_runs"
    id = Column(String, primary_key=True, index=True)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    claims = relationship("ClaimRecord", back_populates="run")

class ClaimRecord(Base):
    __tablename__ = "claims"
    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, ForeignKey("verification_runs.id"))
    claim_text = Column(Text)
    verdict = Column(String)
    confidence = Column(String)
    summary = Column(Text)
    reasoning = Column(Text)
    checked_at = Column(DateTime)
    
    run = relationship("VerificationRun", back_populates="claims")
    evidence = relationship("EvidenceRecord", back_populates="claim")

class EvidenceRecord(Base):
    __tablename__ = "evidence"
    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer, ForeignKey("claims.id"))
    source_title = Column(String, nullable=True)
    source_url = Column(String, nullable=True)
    publisher = Column(String, nullable=True)
    snippet = Column(Text, nullable=True)
    evidence_type = Column(String) # SUPPORTING or CONTRADICTING
    
    claim = relationship("ClaimRecord", back_populates="evidence")

class DigestRecord(Base):
    __tablename__ = "digests"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String)
    topic = Column(String)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables
Base.metadata.create_all(bind=engine)
