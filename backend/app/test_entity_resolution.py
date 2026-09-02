from entity_resolution import similarity_score, are_similar


names = [
    ("Ravi Kumar", "ravi kumar"),
    ("Ravi Kumar", "Ravi K"),
    ("Ravi Kumar", "Suresh Kumar"),
    ("Arun Kumar", "Arun Kumar")
]


for name1, name2 in names:

    score = similarity_score(name1, name2)

    print(
        f"{name1} <-> {name2} = {score:.2f}"
    )

    print(
        "Potential match:",
        are_similar(name1, name2)
    )

    print("-" * 40)