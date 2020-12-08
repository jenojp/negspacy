<p align="center"><img width="40%" src="docs/icon.png" /></p>


# negspacy: negation for spaCy

[![Build Status](https://dev.azure.com/jenopizzaro/negspacy/_apis/build/status/jenojp.negspacy?branchName=master)](https://dev.azure.com/jenopizzaro/negspacy/_build/latest?definitionId=2&branchName=master) [![Built with spaCy](https://img.shields.io/badge/made%20with%20❤%20and-spaCy-09a3d5.svg)](https://spacy.io) [![pypi Version](https://img.shields.io/pypi/v/negspacy.svg?style=flat-square)](https://pypi.org/project/negspacy/) [![DOI](https://zenodo.org/badge/201071164.svg)](https://zenodo.org/badge/latestdoi/201071164) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/ambv/black)

spaCy pipeline object for negating concepts in text. Based on the NegEx algorithm.

***NegEx - A Simple Algorithm for Identifying Negated Findings and Diseases in Discharge Summaries
Chapman, Bridewell, Hanbury, Cooper, Buchanan***
[https://doi.org/10.1006/jbin.2001.1029](https://doi.org/10.1006/jbin.2001.1029)

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
* **preceding_negations** - negation phrases that precede an entity
* **following_negations** - negation phrases that follow an entity
* **termination** - phrases that cut a sentence in parts, for purposes of negation detection (.e.g., "but")

### Termsets

Designate termset to use, `en_clinical` is used by default.

`negex = Negex(nlp, language = "en_clinical")`

* `en` = phrases for general english language text
* `en_clinical` **DEFAULT** = adds phrases specific to clinical domain to general english
* `en_clinical_sensitive` = adds additional phrases to help rule out historical and possibly irrelevant entities

## Additional Functionality

### Change patterns or view patterns in use

Replace all patterns with your own set
```python
nlp = spacy.load("en_core_web_sm")
negex = Negex(nlp, termination=["but", "however", "nevertheless", "except"])
```

Add and remove individual patterns on the fly
```python
negex.add_patterns(
    pseudo_negations=["my favorite pattern"],
    termination=["these are", "great patterns"],
    preceding_negations=["more patterns"],
    following_negations=["even more patterns"],
)
negex.remove_patterns(
    pseudo_negations=["my favorite pattern"],
    termination=["these are", "great patterns"],
    preceding_negations="denied",
    following_negations=["unlikely"],
    )
```
Note: A list is required when adding any amount of patterns but only required when removing multiple patterns. 

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
negex = Negex(nlp, language = "en_clinical", chunk_prefix = ["no"])
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

## Other libraries

This library is featured in the [spaCy Universe](https://spacy.io/universe). Check it out for other useful libraries and inspiration.

If you're looking for a spaCy pipeline object to extract values that correspond to a named entity (e.g., birth dates, account numbers, or laboratory results) take a look at [extractacy](https://github.com/jenojp/extractacy).

<p align="left"><img width="40%" src="https://github.com/jenojp/extractacy/blob/master/docs/icon.png?raw=true" /></p>
