from rapidfuzz import fuzz


def normalize_name(name: str) -> str:
    """
    Convert a name into a standard format.
    """

    name = name.lower().strip()

    # Remove extra spaces
    name = " ".join(name.split())

    return name


def similarity_score(name1: str, name2: str) -> float:
    """
    Calculate similarity between two names.
    Returns a value between 0 and 1.
    """

    name1 = normalize_name(name1)
    name2 = normalize_name(name2)

    score = fuzz.ratio(name1, name2)

    return score / 100


def are_similar(name1: str, name2: str, threshold: float = 0.85) -> bool:
    """
    Determine whether two names are similar enough
    to be considered potential matches.
    """

    score = similarity_score(name1, name2)

    return score >= threshold