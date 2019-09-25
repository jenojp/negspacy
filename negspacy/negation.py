from spacy.tokens import Token, Doc, Span
from spacy.matcher import PhraseMatcher
import logging

from negspacy.termsets import LANGUAGES


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
    language: str
        language code, if using default termsets (e.g. "en" for english)
    psuedo_negations: list
        list of phrases that cancel out a negation, if empty, defaults are used
    preceding_negations: list
        negations that appear before an entity, if empty, defaults are used
    following_negations: list
        negations that appear after an entity, if empty, defaults are used
    termination: list
        phrases that "terminate" a sentence for processing purposes such as "but". If empty, defaults are used

	"""

    def __init__(
        self,
        nlp,
        language="en",
        ent_types=list(),
        psuedo_negations=list(),
        preceding_negations=list(),
        following_negations=list(),
        termination=list(),
    ):
        if not language in LANGUAGES:
            raise KeyError(
                f"{language} not found in languages termset. "
                "Ensure this is a supported language or specify "
                "your own termsets when initializing Negex."
            )
        termsets = LANGUAGES[language]
        if not Span.has_extension("negex"):
            Span.set_extension("negex", default=False, force=True)

        if not psuedo_negations:
            if not "psuedo_negations" in termsets:
                raise KeyError("psuedo_negations not specified for this language.")
            psuedo_negations = termsets["psuedo_negations"]

        if not preceding_negations:
            if not "preceding_negations" in termsets:
                raise KeyError("preceding_negations not specified for this language.")
            preceding_negations = termsets["preceding_negations"]

        if not following_negations:
            if not "following_negations" in termsets:
                raise KeyError("following_negations not specified for this language.")
            following_negations = termsets["following_negations"]

        if not termination:
            if not "termination" in termsets:
                raise KeyError("termination not specified for this language.")
            termination = termsets["termination"]

        # efficiently build spaCy matcher patterns
        self.psuedo_patterns = list(nlp.tokenizer.pipe(psuedo_negations))
        self.preceding_patterns = list(nlp.tokenizer.pipe(preceding_negations))
        self.following_patterns = list(nlp.tokenizer.pipe(following_negations))
        self.termination_patterns = list(nlp.tokenizer.pipe(termination))

        self.matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
        self.matcher.add("Psuedo", None, *self.psuedo_patterns)
        self.matcher.add("Preceding", None, *self.preceding_patterns)
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
            "preceding_patterns": self.preceding_patterns,
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
        preceding: list
            list of tuples for preceding negations
        following: list
            list of tuples for following negations
        terminating: list
            list of tuples of terminating phrases

        """
        ###
        # does not work properly in spacy 2.1.8. Will incorporate after 2.2.
        # Relying on user to use NER in meantime
        # see https://github.com/jenojp/negspacy/issues/7
        ###
        # if not doc.is_nered:
        #     raise ValueError(
        #         "Negations are evaluated for Named Entities found in text. "
        #         "Your SpaCy pipeline does not included Named Entity resolution. "
        #         "Please ensure it is enabled or choose a different language model that includes it."
        #     )
        preceding = list()
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
                    preceding.append((match_id, start, end))
                elif match_id == self.keys[2]:
                    following.append((match_id, start, end))
                elif match_id == self.keys[3]:
                    terminating.append((match_id, start, end))
                else:
                    logging.warnings(
                        f"phrase {doc[start:end].text} not in one of the expected matcher types."
                    )
        return preceding, following, terminating

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
        preceding, following, terminating = self.process_negations(doc)
        boundaries = self.termination_boundaries(doc, terminating)
        for b in boundaries:
            sub_preceding = [i for i in preceding if b[0] <= i[1] < b[1]]
            sub_following = [i for i in following if b[0] <= i[1] < b[1]]

            for e in doc[b[0] : b[1]].ents:
                if self.ent_types:
                    if e.label_ not in self.ent_types:
                        continue
                if any(pre < e.start for pre in [i[1] for i in sub_preceding]):
                    e._.negex = True
                if any(fol > e.end for fol in [i[2] for i in sub_following]):
                    e._.negex = True
        return doc

    def __call__(self, doc):
        return self.negex(doc)
