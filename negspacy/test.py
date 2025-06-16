import spacy
import copy
from negspacy.termsets import termset
from spacy.pipeline import EntityRuler
from spacy.language import Language


def build_docs():
    """
    Builds a list of tuples with text and expected negation results.
    Each tuple contains a string and a list of tuples with entity text and its negation status.
    """
    docs = list()
    docs.append(
        (
            "She does not like Steve Jobs but likes Apple products.",
            [("Steve Jobs", True), ("Apple", False)],
        )
    )
    docs.append(
        (
            "Patient denies December 31, 2020 but has January 1, 2021. He likes USA.",
            [("December 31, 2020", True), ("January 1, 2021", False), ("USA", False)],
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


def test():
    """
    Test the negex component with the default English model.
    """
    nlp = spacy.load("en_core_web_sm")
    nlp.add_pipe("negex", last=True)
    docs = build_docs()
    for d in docs:
        doc = nlp(d[0])
        for i, e in enumerate(doc.ents):
            print(e.text, e._.negex)
            assert (e.text, e._.negex) == d[1][i]


def test_en():
    """
    Test the negex component with the English termset.
    """
    nlp = spacy.load("en_core_web_sm")
    ts = termset("en")
    nlp.add_pipe("negex", config={"neg_termset": ts.get_patterns()}, last=True)
    docs = build_docs()
    for d in docs:
        doc = nlp(d[0])
        for i, e in enumerate(doc.ents):
            print(e.text, e._.negex)
            assert (e.text, e._.negex) == d[1][i]


def test_own_terminology():
    """
    Test the negex component with a custom termset.
    """
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
    assert not doc.ents[1]._.negex


def test_issue7():
    """
    Test for issue #7 where the negex component was not working with EntityRuler."""
    nlp = spacy.load("en_core_web_sm")
    nlp.add_pipe("negex", last=True)
    ruler = EntityRuler(nlp)  # noqa
    patterns = [{"label": "SOFTWARE", "pattern": "spacy"}]  # noqa
    doc = nlp("fgfgdghgdh")  # noqa


def test_get_patterns():
    """
    Test the get_patterns method of the termset class."""
    # nlp = spacy.load("en_core_web_sm")
    # negex = Negex(nlp)
    # patterns = negex.get_patterns()
    ts = termset("en")
    patterns = ts.get_patterns()
    assert isinstance(patterns, dict)
    assert len(patterns) == 4


def test_add_remove_patterns():
    """
    Test adding and removing patterns in the termset."""
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


def ents_to_spans(doc):
    """Converts entities to spans"""
    spans = []
    for ent in doc.ents:
        span = doc.char_span(ent.start_char, ent.end_char, label=ent.label_)
        if span:
            spans.append(span)
    doc.spans["ent_spans"] = spans
    return doc


@Language.component("ents_to_spans")
def convert_ents_to_spans(doc):
    """Convert the doc.ents to spans"""
    new_spans = []
    for ent in doc.ents:
        temp_span = doc[ent.start : ent.end]
        temp_span.label_ = ent.label_
        new_spans.append(temp_span)
    doc.spans["ent_spans"] = new_spans
    return doc


def test_spans():
    """
    Test the negex component with spans instead of entities."""
    nlp = spacy.load("en_core_web_sm")
    nlp.add_pipe("ents_to_spans", last=True)
    nlp.add_pipe("negex", last=True, config={"span_keys": ["ent_spans"]})

    docs = build_docs()
    for d in docs:
        doc = nlp(d[0])
        for i, e in enumerate(doc.spans["ent_spans"]):
            print(e.text, e._.negex)
            assert (e.text, e._.negex) == d[1][i]


if __name__ == "__main__":
    test()
    test_en()
    test_own_terminology()
    test_get_patterns()
    test_issue7()
    test_add_remove_patterns()
    test_spans()
