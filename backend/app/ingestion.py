from datetime import datetime
import pandas as pd
from sqlalchemy.orm import Session
from .models import Entity, Record, Transaction,CDR
from .nlp import extract_entities, extract_relationships
from .graph import graph_store

def ingest_text(db: Session, source: str, text: str):
    db.add(Record(source=source, record_type="TEXT", raw_text=text))
    entities = extract_entities(text)

    for item in entities:
        existing = db.query(Entity).filter(
            Entity.name == item["name"],
            Entity.entity_type == item["entity_type"]
        ).first()

        if not existing:
            db.add(Entity(
                name=item["name"],
                entity_type=item["entity_type"],
                source=source,
                confidence=item["confidence"]
            ))

        graph_store.add_entity(item["name"], item["entity_type"])

    relationships = extract_relationships(text,entities)
    for rel in relationships:
        graph_store.add_relationship(
            rel["source"], rel["source_type"],
            rel["target"], rel["target_type"],
            rel["relationship"]
        )

    db.commit()
    return {"source": source, "entities": entities, "relationships": relationships}

def ingest_transactions_csv(db: Session, file_path: str):
    df = pd.read_csv(file_path)
    required = {"source", "from_entity", "to_entity", "amount"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing CSV columns: {sorted(missing)}")

    count = 0
    for _, row in df.iterrows():
        timestamp = None
        if "timestamp" in df.columns and pd.notna(row["timestamp"]):
            timestamp = datetime.fromisoformat(str(row["timestamp"]))

        from_name = str(row["from_entity"])
        to_name = str(row["to_entity"])

        db.add(Transaction(
            source=str(row["source"]),
            from_entity=from_name,
            to_entity=to_name,
            amount=float(row["amount"]),
            timestamp=timestamp
        ))

        graph_store.add_entity(from_name, "UNKNOWN")
        graph_store.add_entity(to_name, "UNKNOWN")
        graph_store.add_relationship(
            from_name, "UNKNOWN", to_name, "UNKNOWN", "TRANSACTION"
        )
        count += 1

    db.commit()
    return count
def ingest_cdr_csv(db: Session, file_path: str):
    df = pd.read_csv(file_path)

    required = {
        "source",
        "caller",
        "receiver",
        "duration_seconds"
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing CSV columns: {sorted(missing)}"
        )

    count = 0

    for _, row in df.iterrows():
        timestamp = None

        if "timestamp" in df.columns and pd.notna(row["timestamp"]):
            timestamp = datetime.fromisoformat(
                str(row["timestamp"])
            )

        caller = str(row["caller"])
        receiver = str(row["receiver"])

        db.add(
            CDR(
                source=str(row["source"]),
                caller=caller,
                receiver=receiver,
                duration_seconds=int(row["duration_seconds"]),
                timestamp=timestamp
            )
        )

        # Add the phone entities to Neo4j
        graph_store.add_entity(caller, "PHONE")
        graph_store.add_entity(receiver, "PHONE")

        # Add the communication relationship
        graph_store.add_relationship(
            caller,
            "PHONE",
            receiver,
            "PHONE",
            "CALLED"
        )

        count += 1

    db.commit()

    return count