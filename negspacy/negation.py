from spacy.tokens import Token, Doc, Span
from spacy.matcher import PhraseMatcher
import logging


class Negex:
    """
	A spaCy pipeline component which identifies negated tokens in text.

	Based on: NegEx - A Simple Algorithm for Identifying Negated Findings and Diseasesin Discharge Summaries
    Chapman, Bridewell, Hanbury, Cooper, Buchanan

    Parameters
    ----------
    nlp: object
        spaCy language object
    ent_types: list
        list of entity types to negate
    psuedo_negations: list
        list of phrases that cancel out a negation, if empty, defaults are used
    preceeding_negations: list
        negations that appear before an entity, if empty, defaults are used
    following_negations: list
        negations that appear after an entity, if empty, defaults are used
    termination: list
        phrases that "terminate" a sentence for processing purposes such as "but". If empty, defaults are used

	"""

    def __init__(
        self,
        nlp,
        ent_types=list(),
        psuedo_negations=list(),
        preceeding_negations=list(),
        following_negations=list(),
        termination=list(),
    ):
        if not Span.has_extension("negex"):
            Span.set_extension("negex", default=False, force=True)
        if not psuedo_negations:
            psuedo_negations = [
                "gram negative",
                "no further",
                "not able to be",
                "not certain if",
                "not certain whether",
                "not necessarily",
                "not rule out",
                "not ruled out",
                "not been ruled out",
                "without any further",
                "without difficulty",
                "without further",
            ]
        if not preceeding_negations:
            preceeding_negations = [
                "absence of",
                "declined",
                "denied",
                "denies",
                "denying",
                "did not exhibit",
                "no sign of",
                "no signs of",
                "not",
                "not demonstrate",
                "patient was not",
                "rules out",
                "doubt",
                "negative for",
                "no",
                "no cause of",
                "no complaints of",
                "no evidence of",
                "versus",
                "without",
                "without indication of",
                "without sign of",
                "without signs of",
                "ruled out",
            ]
        if not following_negations:
            following_negations = [
                "declined",
                "unlikely",
                "was ruled out",
                "were ruled out",
                "was not",
                "were not",
            ]
        if not termination:
            termination = [
                "although",
                "apart from",
                "as there are",
                "aside from",
                "but",
                "cause for",
                "cause of",
                "causes for",
                "causes of",
                "etiology for",
                "etiology of",
                "except",
                "however",
                "involving",
                "nevertheless",
                "origin for",
                "origin of",
                "origins for",
                "origins of",
                "other possibilities of",
                "reason for",
                "reason of",
                "reasons for",
                "reasons of",
                "secondary to",
                "source for",
                "source of",
                "sources for",
                "sources of",
                "still",
                "though",
                "trigger event for",
                "which",
                "yet",
            ]

        # efficiently build spaCy matcher patterns
        self.psuedo_patterns = list(nlp.tokenizer.pipe(psuedo_negations))
        self.preceeding_patterns = list(nlp.tokenizer.pipe(preceeding_negations))
        self.following_patterns = list(nlp.tokenizer.pipe(following_negations))
        self.termination_patterns = list(nlp.tokenizer.pipe(termination))

        self.matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
        self.matcher.add("Psuedo", None, *self.psuedo_patterns)
        self.matcher.add("Preceeding", None, *self.preceeding_patterns)
        self.matcher.add("Following", None, *self.following_patterns)
        self.matcher.add("Termination", None, *self.termination_patterns)
        self.keys = [k for k in self.matcher._docs.keys()]
        self.ent_types = ent_types

    def get_patterns(self):
        """
        returns phrase patterns used for various negation dictionaries
        
        Returns
        -------
        patterns: dict
            pattern_type: [patterns]

        """
        patterns = {
            "psuedo_patterns": self.psuedo_patterns,
            "preceeding_patterns": self.preceeding_patterns,
            "following_patterns": self.following_patterns,
            "termination_patterns": self.termination_patterns,
        }
        for pattern in patterns:
            logging.info(pattern)
        return patterns

    def process_negations(self, doc):
        """
        Find negations in doc and clean candidate negations to remove pseudo negations

        Parameters 
        ----------
        doc: object
            spaCy Doc object

        Returns
        -------
        preceeding: list
            list of tuples for preceeding negations
        following: list
            list of tuples for following negations
        terminating: list
            list of tuples of terminating phrases

        """
        if not doc.is_nered:
            raise ValueError(
                "Negations are evaluated for Named Entities found in text. "
                "Your SpaCy pipeline does not included Named Entity resolution. "
                "Please ensure it is enabled or choose a different language model that includes it."
            )
        preceeding = list()
        following = list()
        terminating = list()

        matches = self.matcher(doc)
        psuedo = [
            (match_id, start, end)
            for match_id, start, end in matches
            if match_id == self.keys[0]
        ]

        for match_id, start, end in matches:
            if match_id == self.keys[0]:
                continue
            psuedo_flag = False
            for p in psuedo:
                if start >= p[1] and start <= p[2]:
                    psuedo_flag == True
                    continue
            if not psuedo_flag:
                if match_id == self.keys[1]:
                    preceeding.append((match_id, start, end))
                elif match_id == self.keys[2]:
                    following.append((match_id, start, end))
                elif match_id == self.keys[3]:
                    terminating.append((match_id, start, end))
                else:
                    logging.warnings(
                        f"phrase {doc[start:end].text} not in one of the expected matcher types."
                    )
        return preceeding, following, terminating

    def termination_boundaries(self, doc, terminating):
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
        boundaries = list()
        index = 0
        for i, start in enumerate(starts):
            if not i == 0:
                boundaries.append((index, start))
            index = start
        return boundaries

    def negex(self, doc):
        """
        Negates entities of interest

        Parameters 
        ----------
        doc: object
            spaCy Doc object

        """
        preceeding, following, terminating = self.process_negations(doc)
        boundaries = self.termination_boundaries(doc, terminating)
        for b in boundaries:
            sub_preceeding = [i for i in preceeding if b[0] <= i[1] < b[1]]
            sub_following = [i for i in following if b[0] <= i[1] < b[1]]

            for e in doc[b[0] : b[1]].ents:
                if self.ent_types:
                    if e.label_ not in self.ent_types:
                        continue
                if any(pre < e.start for pre in [i[1] for i in sub_preceeding]):
                    e._.negex = True
                if any(fol > e.end for fol in [i[2] for i in sub_following]):
                    e._.negex = True
        return doc

    def __call__(self, doc):
        return self.negex(doc)
