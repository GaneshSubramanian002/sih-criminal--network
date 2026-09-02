from .graph import graph_store


result = graph_store.add_entity(
    "Arun Kumr",
    "PERSON"
)

print("Final result:")
print(result)

graph_store.close()