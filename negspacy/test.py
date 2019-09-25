import pytest
import spacy
from negation import Negex
from spacy.pipeline import EntityRuler


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
            "Patient denies cardiovascular disease but has headaches. No history of smoking. Alcoholism unlikely. Smoking not ruled out.",
            [
                ("Patient", False),
                ("denies", False),
                ("cardiovascular disease", True),
                ("headaches", False),
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
                ("No history", False),
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


# blocked by spacy 2.1.8 issue. Adding back after spacy 2.2.
# def test_no_ner():
#     nlp = spacy.load("en_core_web_sm", disable=["ner"])
#     negex = Negex(nlp)
#     nlp.add_pipe(negex, last=True)
#     with pytest.raises(ValueError):
#         doc = nlp("this doc has not been NERed")


def test_own_terminology():
    nlp = spacy.load("en_core_web_sm")
    negex = Negex(nlp, termination=["whatever"])
    nlp.add_pipe(negex, last=True)
    doc = nlp("He does not like Steve Jobs whatever he says about Barack Obama.")
    assert doc.ents[1]._.negex == False


def test_get_patterns():
    nlp = spacy.load("en_core_web_sm")
    negex = Negex(nlp)
    patterns = negex.get_patterns()
    assert type(patterns) == dict
    assert len(patterns) == 4


def issue7():
    nlp = spacy.load("en_core_web_sm")
    negex = Negex(nlp)
    nlp.add_pipe(negex, last=True)
    ruler = EntityRuler(nlp)
    patterns = [{"label": "SOFTWARE", "pattern": "spacy"}]
    doc = nlp("fgfgdghgdh")


if __name__ == "__main__":
    test()
    test_umls()
    test_bad_beharor()
    test_own_terminology()
    test_get_patterns()
