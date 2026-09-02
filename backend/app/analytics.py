import statistics
import networkx as nx
from sqlalchemy import select
from .models import Transaction, CDR
def centrality_analysis(graph_store):
    """
    Calculate degree and betweenness centrality
    on the existing Neo4j criminal network.
    """

    query = """
    MATCH (n:Entity)
    OPTIONAL MATCH (n)-[r]-(m:Entity)
    RETURN n.name AS source,
           collect(m.name) AS neighbors
    """

    records = graph_store.run_query(query)

    G = nx.Graph()

    for record in records:
        source = record["source"]

        if not source:
            continue

        G.add_node(source)

        for neighbor in record["neighbors"]:
            if neighbor:
                G.add_edge(source, neighbor)

    if len(G) == 0:
        return []

    degree = nx.degree_centrality(G) if len(G) > 1 else {}
    betweenness = nx.betweenness_centrality(G) if len(G) > 1 else {}

    rows = []

    for node in G.nodes:
        rows.append({
            "entity": node,
            "degree_centrality": round(
                degree.get(node, 0), 4
            ),
            "betweenness_centrality": round(
                betweenness.get(node, 0), 4
            )
        })

    return sorted(
        rows,
        key=lambda x: (
            x["betweenness_centrality"],
            x["degree_centrality"]
        ),
        reverse=True
    )

def pagerank_analysis(graph_store):
    """
    Calculate PageRank on the existing Neo4j criminal network.
    """

    query = """
    MATCH (n)
    OPTIONAL MATCH (n)-[r]-(m)
    RETURN n.name AS source,
           collect(m.name) AS neighbors
    """

    records = graph_store.run_query(query)

    G = nx.Graph()

    for record in records:
        source = record["source"]

        if not source:
            continue

        G.add_node(source)

        for neighbor in record["neighbors"]:
            if neighbor:
                G.add_edge(source, neighbor)

    if len(G) == 0:
        return []

    scores = nx.pagerank(G)

    rows = []

    for node, score in scores.items():
        rows.append({
            "entity": node,
            "pagerank": round(score, 4)
        })

    return sorted(
        rows,
        key=lambda x: x["pagerank"],
        reverse=True
    )
def transaction_anomalies(db):
    transactions = db.scalars(select(Transaction)).all()
    amounts = [tx.amount for tx in transactions]

    if len(amounts) < 2:
        return []

    mean = statistics.mean(amounts)
    stdev = statistics.stdev(amounts)
    if stdev == 0:
        return []

    result = []
    for tx in transactions:
        z = (tx.amount - mean) / stdev
        if abs(z) >= 2:
            result.append({
                "transaction_id": tx.id,
                "from_entity": tx.from_entity,
                "to_entity": tx.to_entity,
                "amount": tx.amount,
                "z_score": round(z, 3),
            })
    return result
def community_detection(graph_store):
    """
    Detect communities in the existing Neo4j criminal network.
    """

    query = """
    MATCH (n:Entity)
    OPTIONAL MATCH (n)-[r]-(m:Entity)
    RETURN n.name AS source,
           collect(m.name) AS neighbors
    """

    records = graph_store.run_query(query)

    G = nx.Graph()

    for record in records:
        source = record["source"]

        if not source:
            continue

        G.add_node(source)

        for neighbor in record["neighbors"]:
            if neighbor:
                G.add_edge(source, neighbor)

    if len(G) == 0:
        return []

    communities = nx.community.greedy_modularity_communities(G)

    rows = []

    for community_id, community in enumerate(communities):
        for entity in community:
            rows.append({
                "entity": entity,
                "community": community_id
            })

    return sorted(
        rows,
        key=lambda x: (x["community"], x["entity"])
    )
def graph_pattern_analysis(graph_store, min_connections: int = 3):
    """
    Identify highly connected entities in the Neo4j network.
    """

    query = """
    MATCH (n:Entity)
    OPTIONAL MATCH (n)-[r]-(m:Entity)
    RETURN
        n.name AS entity,
        n.entity_type AS entity_type,
        count(m) AS connection_count
    ORDER BY connection_count DESC
    """

    records = graph_store.run_query(query)

    rows = []

    for record in records:
        connection_count = record["connection_count"]

        if connection_count >= min_connections:
            rows.append({
                "entity": record["entity"],
                "entity_type": record["entity_type"],
                "connection_count": connection_count,
                "pattern": "highly_connected"
            })

    return rows

def cdr_analysis(db):
    """
    Analyze synthetic CDR data and identify
    communication activity for each phone number.
    """

    records = db.scalars(select(CDR)).all()

    if not records:
        return []

    stats = {}

    for record in records:
        caller = record.caller
        receiver = record.receiver

        if caller not in stats:
            stats[caller] = {
                "phone": caller,
                "calls_made": 0,
                "calls_received": 0,
                "total_duration_seconds": 0
            }

        if receiver not in stats:
            stats[receiver] = {
                "phone": receiver,
                "calls_made": 0,
                "calls_received": 0,
                "total_duration_seconds": 0
            }

        stats[caller]["calls_made"] += 1
        stats[caller]["total_duration_seconds"] += (
            record.duration_seconds
        )

        stats[receiver]["calls_received"] += 1

    rows = list(stats.values())

    for row in rows:
        row["total_calls"] = (
            row["calls_made"] +
            row["calls_received"]
        )

    return sorted(
        rows,
        key=lambda x: x["total_calls"],
        reverse=True
    )

def transaction_summary(db):
    """
    Summarize synthetic financial transactions.
    """

    transactions = db.scalars(select(Transaction)).all()

    if not transactions:
        return {
            "total_transactions": 0,
            "total_amount": 0,
            "average_amount": 0,
            "highest_transaction": None
        }

    total_amount = sum(tx.amount for tx in transactions)
    average_amount = total_amount / len(transactions)

    highest = max(
        transactions,
        key=lambda tx: tx.amount
    )

    return {
        "total_transactions": len(transactions),
        "total_amount": round(total_amount, 2),
        "average_amount": round(average_amount, 2),
        "highest_transaction": {
            "transaction_id": highest.id,
            "from_entity": highest.from_entity,
            "to_entity": highest.to_entity,
            "amount": highest.amount,
            "timestamp": highest.timestamp
        }
    }
def timeline_analysis(db):
    """
    Combine synthetic CDR and financial transaction
    records into a chronological event timeline.
    """

    events = []

    cdr_records = db.scalars(select(CDR)).all()

    for record in cdr_records:
        if record.timestamp is None:
            continue

        events.append({
            "timestamp": record.timestamp,
            "event_type": "CALL",
            "source": record.caller,
            "target": record.receiver,
            "details": {
                "duration_seconds": record.duration_seconds
            }
        })

    transactions = db.scalars(select(Transaction)).all()

    for tx in transactions:
        if tx.timestamp is None:
            continue

        events.append({
            "timestamp": tx.timestamp,
            "event_type": "TRANSACTION",
            "source": tx.from_entity,
            "target": tx.to_entity,
            "details": {
                "amount": tx.amount,
                "transaction_id": tx.id
            }
        })

    return sorted(
        events,
        key=lambda x: x["timestamp"]
    )