import negspacy.negation  # noqa: F401
from negspacy.termsets import termset
from spacy.language import Language
from spacy.pipeline import EntityRuler


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
    assert doc.ents[1]._.negex == False


def test_issue7(nlp):
    nlp.add_pipe("negex", last=True)
    ruler = EntityRuler(nlp)
    patterns = [{"label": "SOFTWARE", "pattern": "spacy"}]
    doc = nlp("fgfgdghgdh")


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
