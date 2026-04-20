import pytest

pytest.importorskip("scispacy")

import spacy

from negspacy.termsets import termset


def build_med_docs():
    docs = list()
    docs.append(
        (
            "Patient denies cardiovascular disease but has headaches."
            " No history of smoking. Alcoholism unlikely. Smoking not ruled out.",
            [
                ("Patient denies", False),
                ("cardiovascular disease", True),
                ("headaches", False),
                ("No history of", True),
                # ("smoking", True),
                ("Alcoholism", True),
                ("unlikely", False),
                ("Smoking", False),
            ],
        )
    )
    docs.append(
        (
            "No history of headaches, prbc, smoking, acid reflux, or GERD.",
            [
                ("No history", True),
                ("headaches", True),
                ("prbc", True),
                ("smoking", True),
                ("acid reflux", True),
                ("GERD", True),
            ],
        )
    )

    docs.append(
        (
            "Alcoholism was not the cause of liver disease.",
            [("Alcoholism", True), ("liver disease", False)],
        )
    )

    return docs


def test_umls():
    nlp = spacy.load("en_core_sci_sm")
    ts = termset("en_clinical")
    nlp.add_pipe(
        "negex",
        config={
            "neg_termset": ts.get_patterns(),
            "ent_types": ["ENTITY"],
            "chunk_prefix": ["no"],
        },
        last=True,
    )
    docs = build_med_docs()
    for d in docs:
        doc = nlp(d[0])
        print(doc.ents)
        for i, e in enumerate(doc.ents):
            print(e.text, e._.negex)
            assert (e.text, e._.negex) == d[1][i]


def test_issue_14():
    nlp = spacy.load("en_core_sci_sm")
    ts = termset("en_clinical")
    ts.remove_patterns({"following_negations": ["free"]})
    print(ts.get_patterns())
    nlp.add_pipe(
        "negex",
        config={
            "neg_termset": ts.get_patterns(),
            "chunk_prefix": ["no", "cancer free"],
        },
        last=True,
    )

    doc = nlp("The patient has a cancer free diagnosis")
    print(doc.ents)
    expected = [False, True]
    for i, e in enumerate(doc.ents[:2]):
        print(e.text, e._.negex)
        assert e._.negex == expected[i]

    nlp.remove_pipe("negex")
    ts = termset("en_clinical")
    nlp.add_pipe(
        "negex",
        config={
            "neg_termset": ts.get_patterns(),
            "chunk_prefix": ["no", "free"],
        },
        last=True,
    )
    doc = nlp("The patient has a cancer free diagnosis")
    expected = [False, False]
    for i, e in enumerate(doc.ents[:2]):
        print(e.text, e._.negex)
        assert e._.negex == expected[i]
