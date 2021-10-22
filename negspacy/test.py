import pytest
import spacy
import copy
import negation
from termsets import termset
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
                ("smoking", True),
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

    # docs.append(
    #     (
    #         "There was no headache for this patient.",
    #         [("no headache", True), ("patient", True)],
    #     )
    # )
    return docs


def test():
    nlp = spacy.load("en_core_web_sm")
    nlp.add_pipe("negex", last=True)
    docs = build_docs()
    for d in docs:
        doc = nlp(d[0])
        for i, e in enumerate(doc.ents):
            print(e.text, e._.negex)
            assert (e.text, e._.negex) == d[1][i]


def test_en():
    nlp = spacy.load("en_core_web_sm")
    ts = termset("en")
    nlp.add_pipe("negex", config={"neg_termset": ts.get_patterns()}, last=True)
    docs = build_docs()
    for d in docs:
        doc = nlp(d[0])
        for i, e in enumerate(doc.ents):
            print(e.text, e._.negex)
            assert (e.text, e._.negex) == d[1][i]


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
    # negex = Negex(
    #     nlp, language="en_clinical", ent_types=["ENTITY"], chunk_prefix=["no"]
    # )
    # nlp.add_pipe("negex", last=True)
    docs = build_med_docs()
    for d in docs:
        doc = nlp(d[0])
        print(doc.ents)
        for i, e in enumerate(doc.ents):
            print(e.text, e._.negex)
            assert (e.text, e._.negex) == d[1][i]


def __test_umls2():
    nlp = spacy.load("en_core_sci_sm")
    # negex = Negex(
    #     nlp, language="en_clinical_sensitive", ent_types=["ENTITY"], chunk_prefix=["no"]
    # )
    # nlp.add_pipe("negex", last=True)
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
    nlp.add_pipe(
        "negex",
        config={
            "neg_termset": {
                "pseudo_negations": [""],
                "preceding_negations": ["not"],
                "following_negations": [],
                "termination": ["whatever"],
            }
        },
        last=True,
    )
    doc = nlp("He does not like Steve Jobs whatever he says about Barack Obama.")
    assert doc.ents[1]._.negex == False


def test_issue7():
    nlp = spacy.load("en_core_web_sm")
    nlp.add_pipe("negex", last=True)
    ruler = EntityRuler(nlp)
    patterns = [{"label": "SOFTWARE", "pattern": "spacy"}]
    doc = nlp("fgfgdghgdh")


def test_get_patterns():
    # nlp = spacy.load("en_core_web_sm")
    # negex = Negex(nlp)
    # patterns = negex.get_patterns()
    ts = termset("en")
    patterns = ts.get_patterns()
    assert type(patterns) == dict
    assert len(patterns) == 4


def test_add_remove_patterns():
    ts = termset("en_clinical")
    patterns = copy.deepcopy(ts.get_patterns())
    ts.add_patterns(
        {
            "pseudo_negations": ["my favorite pattern"],
            "termination": ["these are", "great patterns", "but"],
            "preceding_negations": ["wow a negation"],
            "following_negations": ["extra negation"],
        }
    )
    patterns_after = ts.get_patterns()

    assert len(patterns_after["pseudo_negations"]) - 1 == len(
        patterns["pseudo_negations"]
    )
    assert len(patterns_after["termination"]) - 2 == len(patterns["termination"])
    assert len(patterns_after["preceding_negations"]) - 1 == len(
        patterns["preceding_negations"]
    )
    assert len(patterns_after["following_negations"]) - 1 == len(
        patterns["following_negations"]
    )

    ts.remove_patterns(
        {
            "termination": ["these are", "great patterns"],
            "pseudo_negations": ["my favorite pattern"],
            "preceding_negations": ["denied", "wow a negation"],
            "following_negations": ["unlikely", "extra negation"],
        }
    )
    patterns_after = ts.get_patterns()
    assert len(patterns_after["termination"]) == len(patterns["termination"])
    assert (
        len(patterns_after["following_negations"])
        == len(patterns["following_negations"]) - 1
    )
    assert (
        len(patterns_after["preceding_negations"])
        == len(patterns["preceding_negations"]) - 1
    )
    assert len(patterns_after["pseudo_negations"]) == len(patterns["pseudo_negations"])


def test_issue_14():
    nlp = spacy.load("en_core_sci_sm")
    # negex = Negex(nlp, language="en_clinical", chunk_prefix=["no", "cancer free"])
    # negex.remove_patterns(following_negations="free")
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
    expected = [False, True]
    for i, e in enumerate(doc.ents):
        print(e.text, e._.negex)
        assert e._.negex == expected[i]

    nlp.remove_pipe("negex")
    # negex = Negex(nlp, language="en_clinical", chunk_prefix=["no", "free"])
    # nlp.add_pipe("negex", last=True)
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
    for i, e in enumerate(doc.ents):
        print(e.text, e._.negex)
        assert e._.negex == expected[i]


if __name__ == "__main__":
    test()
    test_umls()
    test_umls2()
    test_en()
    test_bad_beharor()
    test_own_terminology()
    test_get_patterns()
    test_issue7()
    test_add_remove_patterns()
    test_issue_14()
