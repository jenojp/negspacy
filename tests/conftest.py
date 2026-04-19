import pytest
import spacy


@pytest.fixture(scope="session")
def _nlp_model():
    return spacy.load("en_core_web_sm")


@pytest.fixture
def nlp(_nlp_model):
    original_pipes = list(_nlp_model.pipe_names)
    yield _nlp_model
    for name in list(_nlp_model.pipe_names):
        if name not in original_pipes:
            _nlp_model.remove_pipe(name)
