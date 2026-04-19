import copy

from negspacy.termsets import termset


def test_get_patterns():
    ts = termset("en")
    patterns = ts.get_patterns()
    assert isinstance(patterns, dict)
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

    assert len(patterns_after["pseudo_negations"]) - 1 == len(patterns["pseudo_negations"])
    assert len(patterns_after["termination"]) - 2 == len(patterns["termination"])
    assert len(patterns_after["preceding_negations"]) - 1 == len(patterns["preceding_negations"])
    assert len(patterns_after["following_negations"]) - 1 == len(patterns["following_negations"])

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
    assert len(patterns_after["following_negations"]) == len(patterns["following_negations"]) - 1
    assert len(patterns_after["preceding_negations"]) == len(patterns["preceding_negations"]) - 1
    assert len(patterns_after["pseudo_negations"]) == len(patterns["pseudo_negations"])
