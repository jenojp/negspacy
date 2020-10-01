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

    docs.append(("That might not be Barack Obama.", [("Barack Obama", False)]))

    return docs


def build_med_docs():
    docs = list()
    docs.append(
        (
            "Patient denies cardiovascular disease but has headaches. No history of smoking. Alcoholism unlikely. Smoking not ruled out.",
            [
                ("Patient denies", False),
                ("cardiovascular disease", True),
                ("headaches", False),
                ("No history", True),
                ("smoking", True),
                ("Alcoholism", True),
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
            [("Alcoholism", True), ("cause", False), ("liver disease", False)],
        )
    )

    docs.append(
        (
            "There was no headache for this patient.",
            [("no headache", True), ("patient", True)],
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
            print(e.text, e._.negex)
            assert (e.text, e._.negex) == d[1][i]


def test_en():
    nlp = spacy.load("en_core_web_sm")
    negex = Negex(nlp, language="en")
    nlp.add_pipe(negex, last=True)
    docs = build_docs()
    for d in docs:
        doc = nlp(d[0])
        for i, e in enumerate(doc.ents):
            print(e.text, e._.negex)
            assert (e.text, e._.negex) == d[1][i]


def test_umls():
    nlp = spacy.load("en_core_sci_sm")
    negex = Negex(
        nlp, language="en_clinical", ent_types=["ENTITY"], chunk_prefix=["no"]
    )
    nlp.add_pipe(negex, last=True)
    docs = build_med_docs()
    for d in docs:
        doc = nlp(d[0])
        for i, e in enumerate(doc.ents):
            print(e.text, e._.negex)
            assert (e.text, e._.negex) == d[1][i]


def test_umls2():
    nlp = spacy.load("en_core_sci_sm")
    negex = Negex(
        nlp, language="en_clinical_sensitive", ent_types=["ENTITY"], chunk_prefix=["no"]
    )
    nlp.add_pipe(negex, last=True)
    docs = build_med_docs()
    for d in docs:
        doc = nlp(d[0])
        for i, e in enumerate(doc.ents):
            print(e.text, e._.negex)
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


def test_issue7():
    nlp = spacy.load("en_core_web_sm")
    negex = Negex(nlp)
    nlp.add_pipe(negex, last=True)
    ruler = EntityRuler(nlp)
    patterns = [{"label": "SOFTWARE", "pattern": "spacy"}]
    doc = nlp("fgfgdghgdh")


def test_add_remove_patterns():
    nlp = spacy.load("en_core_web_sm")
    negex = Negex(nlp)
    patterns = negex.get_patterns()
    negex.add_patterns(
        pseudo_negations=["my favorite pattern"],
        termination=["these are", "great patterns"],
        preceding_negations=["wow a negation"],
        following_negations=["extra negation"],
    )
    patterns_after = negex.get_patterns()
    print(patterns_after)
    print(len(patterns_after["pseudo_patterns"]))
    assert len(patterns_after["pseudo_patterns"]) - 1 == len(
        patterns["pseudo_patterns"]
    )
    assert len(patterns_after["termination_patterns"]) - 2 == len(
        patterns["termination_patterns"]
    )
    assert len(patterns_after["preceding_patterns"]) - 1 == len(
        patterns["preceding_patterns"]
    )
    assert len(patterns_after["following_patterns"]) - 1 == len(
        patterns["following_patterns"]
    )

    negex.remove_patterns(
        termination=["these are", "great patterns"],
        pseudo_negations=["my favorite pattern"],
        preceding_negations="denied",
        following_negations=["unlikely"],
    )
    negex.remove_patterns(termination="but")
    negex.remove_patterns(
        preceding_negations="wow a negation", following_negations=["extra negation"]
    )
    patterns_after = negex.get_patterns()
    assert (
        len(patterns_after["termination_patterns"])
        == len(patterns["termination_patterns"]) - 1
    )
    assert (
        len(patterns_after["following_patterns"])
        == len(patterns["following_patterns"]) - 1
    )
    assert (
        len(patterns_after["preceding_patterns"])
        == len(patterns["preceding_patterns"]) - 1
    )
    assert len(patterns_after["pseudo_patterns"]) == len(patterns["pseudo_patterns"])


if __name__ == "__main__":
    test()
    test_umls()
    test_bad_beharor()
    test_own_terminology()
    test_get_patterns()
    test_issue7()
    test_add_remove_patterns()
