from neo4j import GraphDatabase
from .config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
from .entity_resolution import similarity_score


class GraphStore:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USER, NEO4J_PASSWORD)
        )

    def close(self):
        self.driver.close()

    def add_entity(self, name, entity_type):
        # First check whether a similar entity already exists
        similar = find_similar_entity(
            self.driver,
            name,
            entity_type
        )

        if similar:
            print(
                f"Entity resolution: '{name}' "
                f"matched with '{similar['match']}' "
                f"(score={similar['score']:.2f})"
            )
            return similar["match"]

        # No similar entity found, so create a new entity
        query = """
        MERGE (e:Entity {name: $name, entity_type: $entity_type})
        """

        with self.driver.session() as session:
            session.run(
                query,
                name=name,
                entity_type=entity_type
            )

        print(f"Created new entity: '{name}' ({entity_type})")
        return name

    def add_relationship(
        self,
        source,
        source_type,
        target,
        target_type,
        relationship
    ):
        query = """
        MERGE (a:Entity {
            name: $source,
            entity_type: $source_type
        })
        MERGE (b:Entity {
            name: $target,
            entity_type: $target_type
        })
        MERGE (a)-[:CONNECTED_BY {kind: $relationship}]->(b)
        """

        with self.driver.session() as session:
            session.run(
                query,
                source=source,
                source_type=source_type,
                target=target,
                target_type=target_type,
                relationship=relationship
            )

    def neighbors(self, entity_name):
        query = """
        MATCH (e:Entity {name: $name})-[r]-(n:Entity)
        RETURN
            n.name AS name,
            n.entity_type AS entity_type,
            type(r) AS relationship
        LIMIT 100
        """

        with self.driver.session() as session:
            return [
                dict(row)
                for row in session.run(
                    query,
                    name=entity_name
                )
            ]

    def get_full_graph(self):
        query = """
        MATCH (a:Entity)-[r]->(b:Entity)
        RETURN
            a.name AS source,
            a.entity_type AS source_type,
            b.name AS target,
            b.entity_type AS target_type,
            r.kind AS relationship
        """

        with self.driver.session() as session:
            records = session.run(query)

            nodes = {}
            edges = []

            for record in records:
                source = record["source"]
                target = record["target"]

                nodes[source] = {
                    "name": source,
                    "entity_type": record["source_type"]
                }

                nodes[target] = {
                    "name": target,
                    "entity_type": record["target_type"]
                }

                edges.append({
                    "source": source,
                    "target": target,
                    "relationship": record["relationship"]
                })

            return {
                "nodes": list(nodes.values()),
                "edges": edges
            }

    def run_query(self, query):
        with self.driver.session() as session:
            return [
                dict(record)
                for record in session.run(query)
            ]


def find_similar_entity(
    driver,
    name: str,
    entity_type: str,
    threshold: float = 0.85
):
    """
    Search Neo4j for an existing entity with a similar name.
    Returns the best potential match.
    """

    query = """
    MATCH (n:Entity {entity_type: $entity_type})
    RETURN n.name AS name
    """

    with driver.session() as session:
        result = session.run(
            query,
            entity_type=entity_type
        )

        best_match = None
        best_score = 0

        for record in result:
            existing_name = record["name"]

            score = similarity_score(
                name,
                existing_name
            )

            if score > best_score:
                best_score = score
                best_match = existing_name

        if best_score >= threshold:
            return {
                "match": best_match,
                "score": best_score
            }

    return None


graph_store = GraphStore()