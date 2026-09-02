import re
import spacy

nlp = spacy.load("en_core_web_sm")

PHONE_RE = re.compile(r"\b(?:\+91[-\s]?)?[6-9]\d{9}\b")
VEHICLE_RE = re.compile(r"\b[A-Z]{2}\d{1,2}[A-Z]{1,3}\d{3,4}\b")

def extract_entities(text: str):
    doc = nlp(text)
    entities = []

    mapping = {
        "PERSON": "PERSON",
        "GPE": "LOCATION",
        "LOC": "LOCATION",
        "FAC": "LOCATION",
        "ORG": "ORGANIZATION",
    }

    for ent in doc.ents:
        if ent.label_ in mapping:
            entities.append({
                "name": ent.text.strip(),
                "entity_type": mapping[ent.label_],
                "confidence": 0.80,
            })

    for match in PHONE_RE.findall(text):
        entities.append({"name": match, "entity_type": "PHONE", "confidence": 0.95})

    for match in VEHICLE_RE.findall(text.upper()):
        entities.append({"name": match, "entity_type": "VEHICLE", "confidence": 0.95})

    unique = {}
    for item in entities:
        unique[(item["name"].lower(), item["entity_type"])] = item
    return list(unique.values())

def build_cooccurrence_relationships(entities):
    relationships = []
    for i in range(len(entities)):
        for j in range(i + 1, len(entities)):
            relationships.append({
                "source": entities[i]["name"],
                "source_type": entities[i]["entity_type"],
                "target": entities[j]["name"],
                "target_type": entities[j]["entity_type"],
                "relationship": "CO_OCCURS_WITH",
            })
    return relationships
def extract_relationships(text:str,entities):
    relationships=[]
    people=[
        e for e in entities if e["entity_type"]=="PERSON"
    ]
    phones=[
        e for e in entities if e["entity_type"]=="PHONE"
    ]
    vehicles =[
        e for e in entities if e["entity_type"]=="VEHICLE"
    ]
    locations=[
        e  for e in entities if e["entity_type"]=="LOCATION"
    ]
    organization=[
        e for e in entities if e["entity_type"]=="ORGANIZATION"
    ]
    for person in people:
        for phone in phones:
            relationships.append({
                "source": person["name"],
                "source_type":"PERSON",
                "target":vehicle["name"],
                "target_type":"VEHICLE",
                "relationship":"USED"
            })
    for person in people:
        for location in locations:
            relationships.append({
                "source": person["name"],
                "source_type": "PERSON",
                "target": location["name"],
                "target_type": "LOCATION",
                "relationship": "LOCATED_AT"
            })
    for person in people:
        for organization in organization:
            relationships.append({
                 "source": person["name"],
                "source_type": "PERSON",
                "target": organization["name"],
                "target_type": "ORGANIZATION",
                "relationship": "ASSOCIATED_WITH"
            })
    return relationships