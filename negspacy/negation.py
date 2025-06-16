from spacy.language import Language
from spacy.tokens import Span
from spacy.matcher import PhraseMatcher
import logging
from typing import List, Dict, Tuple, Set, Optional, Any

from negspacy.termsets import termset

default_ts = termset("en_clinical").get_patterns()


def _safe_get_spans(doc, span_key):
    """Safely get spans from doc.spans, return empty list if key not present."""
    return doc.spans.get(span_key, [])


@Language.factory(
    "negex",
    default_config={
        "neg_termset": default_ts,
        "ent_types": None,
        "extension_name": "negex",
        "chunk_prefix": None,
        "span_keys": None,
    },
)
class Negex:
    """
    A spaCy pipeline component which identifies negated tokens in text.

    Based on: NegEx - A Simple Algorithm for Identifying Negated Findings
    and Diseasesin Discharge Summaries
    Chapman, Bridewell, Hanbury, Cooper, Buchanan

    Parameters
    ----------
    nlp: object
        spaCy language object
    ent_types: list
        list of entity types to negate
    termset_lang: str
        language code, if using default termsets (e.g. "en" for english)
    extension_name: str
        defaults to "negex"; whether entity is negated is then available as ent._.negex or span._.negex
    pseudo_negations: list
        list of phrases that cancel out a negation, if empty, defaults are used
    preceding_negations: list
        negations that appear before an entity, if empty, defaults are used
    following_negations: list
        negations that appear after an entity, if empty, defaults are used
    termination: list
        phrases that "terminate" a sentence for processing purposes such as "but". If empty, defaults are used
    span_keys: list
        list of keys to use for spans, defaults to ["sc"]

    """

    def __init__(
        self,
        nlp: Language,
        name: str,
        neg_termset: Dict[str, List[str]],
        ent_types: Optional[List[str]] = None,
        extension_name: str = "negex",
        chunk_prefix: Optional[List[str]] = None,
        span_keys: Optional[List[str]] = None,
    ):
        if not Span.has_extension(extension_name):
            Span.set_extension(extension_name, default=False, force=True)

        ts = neg_termset
        expected_keys = [
            "pseudo_negations",
            "preceding_negations",
            "following_negations",
            "termination",
        ]
        if set(ts.keys()) != set(expected_keys):
            raise KeyError(
                f"Unexpected or missing keys in 'neg_termset', expected: {expected_keys}, instead got: {list(ts.keys())}"
            )

        self.pseudo_negations: List[str] = ts["pseudo_negations"]
        self.preceding_negations: List[str] = ts["preceding_negations"]
        self.following_negations: List[str] = ts["following_negations"]
        self.termination: List[str] = ts["termination"]

        self.nlp = nlp
        self.ent_types: Set[str] = set(ent_types) if ent_types else set()
        self.extension_name = extension_name
        self.build_patterns()
        self.chunk_prefix: Set[str] = set(chunk_prefix) if chunk_prefix else set()
        self.span_keys: Set[str] = set(span_keys) if span_keys else set()

    def build_patterns(self) -> None:
        """
        Build patterns for negation detection.
        Uses PhraseMatcher to efficiently match phrases in the text.
        """
        self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")

        self.pseudo_patterns = list(self.nlp.tokenizer.pipe(self.pseudo_negations))
        self.matcher.add("pseudo", None, *self.pseudo_patterns)

        self.preceding_patterns = list(
            self.nlp.tokenizer.pipe(self.preceding_negations)
        )
        self.matcher.add("Preceding", None, *self.preceding_patterns)

        self.following_patterns = list(
            self.nlp.tokenizer.pipe(self.following_negations)
        )
        self.matcher.add("Following", None, *self.following_patterns)

        self.termination_patterns = list(self.nlp.tokenizer.pipe(self.termination))
        self.matcher.add("Termination", None, *self.termination_patterns)

    def process_negations(self, doc) -> Tuple[List[Tuple[int, int, int]], List[Tuple[int, int, int]], List[Tuple[int, int, int]]]:
        """
        Find negations in doc and clean candidate negations to remove pseudo negations

        Parameters
        ----------
        doc: object
            spaCy Doc object

        Returns
        -------
        preceding: list
            list of tuples for preceding negations
        following: list
            list of tuples for following negations
        terminating: list
            list of tuples of terminating phrases

        """

        preceding = []
        following = []
        terminating = []

        matches = self.matcher(doc)
        pseudo = [
            (match_id, start, end)
            for match_id, start, end in matches
            if self.nlp.vocab.strings[match_id] == "pseudo"
        ]

        for match_id, start, end in matches:
            match_type = self.nlp.vocab.strings[match_id]
            if match_type == "pseudo":
                continue
            pseudo_flag = False
            for p in pseudo:
                if start >= p[1] and start <= p[2]:
                    pseudo_flag = True
                    break
            if not pseudo_flag:
                if match_type == "Preceding":
                    preceding.append((match_id, start, end))
                elif match_type == "Following":
                    following.append((match_id, start, end))
                elif match_type == "Termination":
                    terminating.append((match_id, start, end))
                else:
                    logging.warning(
                        f"phrase {doc[start:end].text} not in one of the expected matcher types."
                    )
        return preceding, following, terminating

    def termination_boundaries(self, doc, terminating: List[Tuple[int, int, int]]) -> List[Tuple[int, int]]:
        """
        Create sub sentences based on terminations found in text.

        Parameters
        ----------
        doc: object
            spaCy Doc object
        terminating: list
            list of tuples with (match_id, start, end)

        returns
        -------
        boundaries: list
            list of tuples with (start, end) of spans

        """
        sent_starts = [sent.start for sent in doc.sents]
        terminating_starts = [t[1] for t in terminating]
        starts = sent_starts + terminating_starts + [len(doc)]
        starts.sort()
        boundaries = []
        index = 0
        for i, start in enumerate(starts):
            if i != 0:
                boundaries.append((index, start))
            index = start
        return boundaries

    @staticmethod
    def yield_spans_within_boundary(doc, boundary: Tuple[int, int], span_keys: Set[str]):
        """
        Yield spans that start and end within a boundary
        """
        start, end = boundary
        for span_key in span_keys:
            for span in _safe_get_spans(doc, span_key):
                if start <= span.start < end and start < span.end <= end:
                    yield span

    def negex(self, doc) -> Any:
        """
        Negates entities of interest

        Parameters
        ----------
        doc: object
            spaCy Doc object

        """
        preceding, following, terminating = self.process_negations(doc)
        boundaries = self.termination_boundaries(doc, terminating)
        for boundary in boundaries:
            sub_preceding = [i for i in preceding if boundary[0] <= i[1] < boundary[1]]
            sub_following = [i for i in following if boundary[0] <= i[1] < boundary[1]]

            def process_span(span):
                if self.ent_types:
                    if span.label_ not in self.ent_types:
                        return
                if any(pre < span.start for pre in [i[1] for i in sub_preceding]):
                    span._.set(self.extension_name, True)
                    return
                if any(fol > span.end for fol in [i[2] for i in sub_following]):
                    span._.set(self.extension_name, True)
                    return
                if self.chunk_prefix:
                    if any(
                        span.text.lower().startswith(c.lower())
                        for c in self.chunk_prefix
                    ):
                        span._.set(self.extension_name, True)
                return span

            if self.span_keys:
                for span in self.yield_spans_within_boundary(doc, boundary, self.span_keys):
                    process_span(span)
            else:
                for e in doc[boundary[0]: boundary[1]].ents:
                    process_span(e)
        return doc

    def __call__(self, doc) -> Any:
        return self.negex(doc)
