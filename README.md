<p align="center"><img width="40%" src="docs/icon.png" /></p>

# negspacy: negation for spaCy

[![Build Status](https://travis-ci.org/jenojp/negspacy.svg?branch=master)](https://travis-ci.org/jenojp/negspacy) [![Build Status](https://dev.azure.com/jenopizzaro/negspacy/_apis/build/status/jenojp.negspacy?branchName=master)](https://dev.azure.com/jenopizzaro/negspacy/_build/latest?definitionId=2&branchName=master) [![Built with spaCy](https://img.shields.io/badge/made%20with%20❤%20and-spaCy-09a3d5.svg)](https://spacy.io) [![pypi Version](https://img.shields.io/pypi/v/negspacy.svg?style=flat-square)](https://pypi.org/project/negspacy/) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/ambv/black)

spaCy pipeline object for negating concepts in text. Based on the NegEx algorithm.

*NegEx - A Simple Algorithm for Identifying Negated Findings and Diseasesin Discharge Summaries
Chapman, Bridewell, Hanbury, Cooper, Buchanan*

## Installation and usage
Install the library.
```bash
pip install negspacy
```

Import library and spaCy.
```python
import spacy
from negspacy.negation import Negex
```

Load spacy language model. Add negspacy pipeline object. Filtering on entity types is optional.
```python
nlp = spacy.load("en_core_web_sm")
negex = Negex(nlp, ent_types=["PERSON","ORG"])
nlp.add_pipe(negex, last=True)
```

View negations.
```python
doc = nlp("She does not like Steve Jobs but likes Apple products.")

for e in doc.ents:
	print(e.text, e._.negex)
```

```console
Steve Jobs True
Apple False
```

Consider pairing with [scispacy](https://allenai.github.io/scispacy/) to find UMLS concepts in text and process negations.

## NegEx Patterns

* **psuedo_negations** - phrases that are false triggers, ambiguous negations, or double negatives
* **preceding_negations** - negation phrases that preceed an entity
* **following_negations** - negation phrases that follow an entity
* **termination** - phrases that cut a sentence in parts, for purposes of negation detection (.e.g., "but")

## Additional Functionality

### Use own patterns or view patterns in use

Use own patterns
```python
nlp = spacy.load("en_core_web_sm")
negex = Negex(nlp, termination=["but", "however", "nevertheless", "except"])
```

View patterns in use
```python
patterns_dict = negex.get_patterns
```

### Negations in noun chunks

Depending on the Named Entity Recognition model you are using, you may have negations "chunked together" with nouns. For example when using scispacy:
```python
nlp = spacy.load("en_core_sci_sm")
doc = nlp("There is no headache.")
for e in doc.ents:
    print(e.text)

# no headache
```
This would cause the Negex algorithm to miss the preceding negation. To account for this, you can add a ```chunk_prefix```:

```python
nlp = spacy.load("en_core_sci_sm")
negex = Negex(nlp, chunk_prefix = ["no"])
nlp.add_pipe(negex)
doc = nlp("There is no headache.")
for e in doc.ents:
    print(e.text, e._.negex)

# no headache True
```


## Contributing
[contributing](https://github.com/jenojp/negspacy/blob/master/CONTRIBUTING.md)

## Authors
* Jeno Pizarro

## License
[license](https://github.com/jenojp/negspacy/blob/master/LICENSE)

## API Documentation
[Docs](https://jenojp.github.io/negspacy/)