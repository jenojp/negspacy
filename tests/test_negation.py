import pytest
from spacy.language import Language

import negspacy.negation  # noqa: F401
from negspacy.negation import Negex
from negspacy.termsets import termset


def build_docs():
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


def test(nlp):
    nlp.add_pipe("negex", last=True)
    docs = build_docs()
    for d in docs:
        doc = nlp(d[0])
        for i, e in enumerate(doc.ents):
            print(e.text, e._.negex)
            assert (e.text, e._.negex) == d[1][i]


def test_en(nlp):
    ts = termset("en")
    nlp.add_pipe("negex", config={"neg_termset": ts.get_patterns()}, last=True)
    docs = build_docs()
    for d in docs:
        doc = nlp(d[0])
        for i, e in enumerate(doc.ents):
            print(e.text, e._.negex)
            assert (e.text, e._.negex) == d[1][i]


def test_own_terminology(nlp):
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


def test_no_entities(nlp):
    """Negex does not crash when the doc contains no recognized entities."""
    nlp.add_pipe("negex", last=True)
    doc = nlp("fgfgdghgdh")
    assert len(doc.ents) == 0


def test_ent_types(nlp):
    """Only entities whose label is in ent_types are negated; others are skipped."""
    nlp.add_pipe("negex", config={"ent_types": ["PERSON"]}, last=True)

    # GPE entities inside a negation scope must NOT be negated when filter is active
    doc = nlp("No history of USA, Germany, Italy, Canada, or Brazil")
    for ent in doc.ents:
        assert not ent._.negex, f"{ent.text} ({ent.label_}) should not be negated"

    # PERSON entity inside a negation scope must be negated
    doc2 = nlp("She does not like Steve Jobs.")
    person_ents = [e for e in doc2.ents if e.label_ == "PERSON"]
    assert len(person_ents) > 0, "expected at least one PERSON entity"
    assert any(e._.negex for e in person_ents)


def test_chunk_prefix(nlp):
    """Entities whose text starts with a chunk_prefix value are marked negated."""
    ruler = nlp.add_pipe("entity_ruler", last=True)
    ruler.add_patterns([{"label": "SYMPTOM", "pattern": "no headache"}])
    nlp.add_pipe("negex", config={"chunk_prefix": ["no"]}, last=True)
    doc = nlp("There is no headache.")
    symptoms = [e for e in doc.ents if e.label_ == "SYMPTOM"]
    assert len(symptoms) == 1
    assert symptoms[0]._.negex


def test_extension_name(nlp):
    """Two Negex instances with different extension_name values work in parallel."""
    nlp.add_pipe("negex", name="negex_default", last=True)
    nlp.add_pipe(
        "negex",
        name="negex_custom",
        config={"extension_name": "custom_negex"},
        last=True,
    )
    doc = nlp("She does not like Steve Jobs.")
    steve = next(e for e in doc.ents if "Jobs" in e.text)
    assert steve._.negex
    assert steve._.custom_negex


def test_invalid_neg_termset(nlp):
    """Passing a neg_termset with unexpected keys raises KeyError."""
    with pytest.raises(KeyError):
        Negex(
            nlp,
            name="negex",
            neg_termset={
                "bad_key": [],
                "preceding_negations": [],
                "following_negations": [],
                "termination": [],
            },
        )


def test_spans_missing_key(nlp):
    """A span_key absent from doc.spans is silently ignored — no crash."""
    nlp.add_pipe("negex", config={"span_keys": ["nonexistent"]}, last=True)
    doc = nlp("She does not like Steve Jobs.")
    # span_keys mode skips doc.ents; no crash despite the missing key
    assert all(not e._.negex for e in doc.ents)


def test_termination_boundaries(nlp):
    """'but' creates a termination boundary, splitting negation scope."""
    nlp.add_pipe("negex", last=True)
    negex_pipe = nlp.get_pipe("negex")
    doc = nlp("She does not like Steve Jobs but likes Apple products.")
    _, _, terminating = negex_pipe.process_negations(doc)
    boundaries = negex_pipe.termination_boundaries(doc, terminating)
    assert len(boundaries) >= 2


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


def test_spans(nlp):
    nlp.add_pipe("ents_to_spans", last=True)
    nlp.add_pipe("negex", last=True, config={"span_keys": ["ent_spans"]})

    docs = build_docs()
    for d in docs:
        doc = nlp(d[0])
        for i, e in enumerate(doc.spans["ent_spans"]):
            print(e.text, e._.negex)
            assert (e.text, e._.negex) == d[1][i]
