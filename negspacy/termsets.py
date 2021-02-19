"""
Default termsets for various languages
"""

LANGUAGES = dict()

# english termset dictionary
en = dict()
pseudo = [
    "no further",
    "not able to be",
    "not certain if",
    "not certain whether",
    "not necessarily",
    "without any further",
    "without difficulty",
    "without further",
    "might not",
    "not only",
    "no increase",
    "no significant change",
    "no change",
    "no definite change",
    "not extend",
    "not cause",
]
en["pseudo_negations"] = pseudo

preceding = [
    "absence of",
    "declined",
    "denied",
    "denies",
    "denying",
    "no sign of",
    "no signs of",
    "not",
    "not demonstrate",
    "symptoms atypical",
    "doubt",
    "negative for",
    "no",
    "versus",
    "without",
    "doesn't",
    "doesnt",
    "don't",
    "dont",
    "didn't",
    "didnt",
    "wasn't",
    "wasnt",
    "weren't",
    "werent",
    "isn't",
    "isnt",
    "aren't",
    "arent",
    "cannot",
    "can't",
    "cant",
    "couldn't",
    "couldnt",
    "never",
]
en["preceding_negations"] = preceding

following = [
    "declined",
    "unlikely",
    "was not",
    "were not",
    "wasn't",
    "wasnt",
    "weren't",
    "werent",
]
en["following_negations"] = following

termination = [
    "although",
    "apart from",
    "as there are",
    "aside from",
    "but",
    "except",
    "however",
    "involving",
    "nevertheless",
    "still",
    "though",
    "which",
    "yet",
]
en["termination"] = termination

LANGUAGES["en"] = en

# en_clinical builds upon en
en_clinical = dict()
pseudo_clinical = pseudo + [
    "gram negative",
    "not rule out",
    "not ruled out",
    "not been ruled out",
    "not drain",
    "no suspicious change",
    "no interval change",
    "no significant interval change",
]
en_clinical["pseudo_negations"] = pseudo_clinical

preceding_clinical = preceding + [
    "patient was not",
    "without indication of",
    "without sign of",
    "without signs of",
    "without any reactions or signs of",
    "no complaints of",
    "no evidence of",
    "no cause of",
    "evaluate for",
    "fails to reveal",
    "free of",
    "never developed",
    "never had",
    "did not exhibit",
    "rules out",
    "rule out",
    "rule him out",
    "rule her out",
    "rule patient out",
    "rule the patient out",
    "ruled out",
    "ruled him out",
    "ruled her out",
    "ruled patient out",
    "ruled the patient out",
    "r/o",
    "ro",
]
en_clinical["preceding_negations"] = preceding_clinical

following_clinical = following + ["was ruled out", "were ruled out", "free"]
en_clinical["following_negations"] = following_clinical

termination_clinical = termination + [
    "cause for",
    "cause of",
    "causes for",
    "causes of",
    "etiology for",
    "etiology of",
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
    "trigger event for",
]
en_clinical["termination"] = termination_clinical
LANGUAGES["en_clinical"] = en_clinical

en_clinical_sensitive = dict()

preceding_clinical_sensitive = preceding_clinical + [
    "concern for",
    "supposed",
    "which causes",
    "leads to",
    "h/o",
    "history of",
    "instead of",
    "if you experience",
    "if you get",
    "teaching the patient",
    "taught the patient",
    "teach the patient",
    "educated the patient",
    "educate the patient",
    "educating the patient",
    "monitored for",
    "monitor for",
    "test for",
    "tested for",
]
en_clinical_sensitive["pseudo_negations"] = pseudo_clinical
en_clinical_sensitive["preceding_negations"] = preceding_clinical_sensitive
en_clinical_sensitive["following_negations"] = following_clinical
en_clinical_sensitive["termination"] = termination_clinical

LANGUAGES["en_clinical_sensitive"] = en_clinical_sensitive


class termset:
    def __init__(self, termset_lang):
        self.pattern_types = [
            "pseudo_negations",
            "preceding_negations",
            "following_negations",
            "termination",
        ]
        self.terms = LANGUAGES[termset_lang]

    def get_patterns(self):
        return self.terms

    def remove_patterns(self, pattern_dict):
        for key, value in pattern_dict.items():
            if key in self.pattern_types:
                self.terms[key] = [i for i in self.terms[key] if i not in value]
            else:
                raise ValueError(f"Unexpected key: {key} not in {self.pattern_types}")

    def add_patterns(self, pattern_dict):
        for key, value in pattern_dict.items():
            if key in self.pattern_types:
                self.terms[key] = list(set(self.terms[key] + value))
            else:
                raise ValueError(f"Unexpected key: {key} not in {self.pattern_types}")
