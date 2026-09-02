from pathlib import Path
import tempfile
from fastapi import FastAPI, Depends, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware 
from sqlalchemy import select
from sqlalchemy.orm import Session
from .db import Base, engine, get_db
from .models import Entity
from .schemas import TextIn, EntityOut
from .ingestion import (
    ingest_text,
    ingest_transactions_csv,
    ingest_cdr_csv
)
from .graph import graph_store
from .analytics import (
    centrality_analysis,
    pagerank_analysis,
    transaction_anomalies,
    community_detection,
    graph_pattern_analysis,
    cdr_analysis,
    transaction_summary,
    timeline_analysis
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Crime/Intelligence Network Analysis API",
    version="0.1.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ingest/text")
def ingest_text_endpoint(payload: TextIn, db: Session = Depends(get_db)):
    return ingest_text(db, payload.source, payload.text)

@app.post("/ingest/transactions")
async def ingest_transactions(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Upload a CSV file.")

    contents = await file.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        count = ingest_transactions_csv(db, tmp_path)
        return {"inserted_transactions": count}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@app.get("/entities", response_model=list[EntityOut])
def list_entities(db: Session = Depends(get_db)):
    return db.scalars(select(Entity).limit(500)).all()

@app.get("/graph/{entity_name}")
def get_graph_neighbors(entity_name: str):
    return {"entity": entity_name, "neighbors": graph_store.neighbors(entity_name)}

@app.get("/graph")
def get_full_graph():
    return graph_store.get_full_graph()

@app.get("/analytics/centrality")
def get_centrality():
    return centrality_analysis(graph_store)

@app.get("/analytics/pagerank")
def get_pagerank():
    return pagerank_analysis(graph_store)

@app.get("/analytics/communities")
def get_communities():
    return community_detection(graph_store)

@app.get("/analytics/patterns")
def get_graph_patterns():
    return graph_pattern_analysis(graph_store)

@app.get("/analytics/cdr")
def get_cdr_analysis(db: Session = Depends(get_db)):
    return cdr_analysis(db)

@app.get("/analytics/transaction-anomalies")
def get_transaction_anomalies(db: Session = Depends(get_db)):
    return transaction_anomalies(db)

@app.get("/analytics/transaction-summary")
def get_transaction_summary(db: Session = Depends(get_db)):
    return transaction_summary(db)

@app.post("/ingest/cdr")
async def ingest_cdr(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Upload a CSV file."
        )

    contents = await file.read()

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".csv"
    ) as tmp:
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        # Get a database session
        from .db import SessionLocal

        db = SessionLocal()

        try:
            count = ingest_cdr_csv(db, tmp_path)
            return {"inserted_cdr_records": count}
        finally:
            db.close()

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )
@app.get("/analytics/timeline")
def get_timeline(db: Session = Depends(get_db)):
    return timeline_analysis(db)