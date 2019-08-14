import spacy
from negation import Negex


def build_docs():
    docs = list()
    docs.append(
        (
            "Patient denies Apple Computers but has Steve Jobs. He likes USA.",
            [("Apple Computers", True), ("Steve Jobs", False), ("USA", False)],
        )
    )
    docs.append(
        (
            "No history of USA, Germany, Italy, Canada, or Brazil",
            [
                ("USA", True),
                ("Germany", True),
                ("Italy", True),
                ("Canada", True),
                ("Brazil", True),
            ],
        )
    )

    return docs


def build_med_docs():
    docs = list()
    docs.append(
        (
            "Patient denies cardiovascular disease but has headaches. No history of smoking.",
            [
                ("Patient", False),
                ("denies", False),
                ("cardiovascular disease", True),
                ("headaches", False),
                ("smoking", True),
            ],
        )
    )
    docs.append(
        (
            "No history of headaches, prbc, smoking, acid reflux, or GERD.",
            [
                ("No history", False),
                ("headaches", True),
                ("prbc", True),
                ("smoking", True),
                ("acid reflux", True),
                ("GERD", True),
            ],
        )
    )
    return docs


def test():
    nlp = spacy.load("en_core_web_sm")
    negex = Negex(nlp)
    nlp.add_pipe(negex, last=True)
    docs = build_docs()
    for d in docs:
        doc = nlp(d[0])
        for i, e in enumerate(doc.ents):
            assert (e.text, e._.negex) == d[1][i]


def test_umls():
    nlp = spacy.load("en_core_sci_sm")
    negex = Negex(nlp, ent_types=["ENTITY"])
    nlp.add_pipe(negex, last=True)
    docs = build_med_docs()
    for d in docs:
        doc = nlp(d[0])
        for i, e in enumerate(doc.ents):
            assert (e.text, e._.negex) == d[1][i]


if __name__ == "__main__":
    test()
    test_umls()
