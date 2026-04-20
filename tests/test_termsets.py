import copy

import pytest

from negspacy.termsets import termset

EXPECTED_KEYS = {"pseudo_negations", "preceding_negations", "following_negations", "termination"}


def test_get_patterns():
    ts = termset("en")
    patterns = ts.get_patterns()
    assert isinstance(patterns, dict)
    assert set(patterns.keys()) == EXPECTED_KEYS


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


def test_add_remove_patterns_content():
    """Added patterns appear in the list; removed patterns are absent."""
    ts = termset("en")
    ts.add_patterns({"pseudo_negations": ["test phrase xyz"]})
    assert "test phrase xyz" in ts.get_patterns()["pseudo_negations"]

    ts.remove_patterns({"pseudo_negations": ["test phrase xyz"]})
    assert "test phrase xyz" not in ts.get_patterns()["pseudo_negations"]


def test_add_patterns_invalid_key():
    """add_patterns raises ValueError for an unrecognised pattern key."""
    ts = termset("en")
    with pytest.raises(ValueError, match="bad_key"):
        ts.add_patterns({"bad_key": ["foo"]})


def test_remove_patterns_invalid_key():
    """remove_patterns raises ValueError for an unrecognised pattern key."""
    ts = termset("en")
    with pytest.raises(ValueError, match="bad_key"):
        ts.remove_patterns({"bad_key": ["foo"]})


def test_en_clinical_sensitive():
    """en_clinical_sensitive has the four required keys and extends en_clinical."""
    ts = termset("en_clinical_sensitive")
    patterns = ts.get_patterns()
    assert isinstance(patterns, dict)
    assert set(patterns.keys()) == EXPECTED_KEYS

    clinical = termset("en_clinical").get_patterns()
    assert len(patterns["preceding_negations"]) > len(clinical["preceding_negations"])


def test_es_clinical():
    """es_clinical loads and contains non-empty pattern lists."""
    ts = termset("es_clinical")
    patterns = ts.get_patterns()
    assert isinstance(patterns, dict)
    assert set(patterns.keys()) == EXPECTED_KEYS
    assert len(patterns["preceding_negations"]) > 0
    assert len(patterns["pseudo_negations"]) > 0
