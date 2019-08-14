<p align="center"><img width="60%" src="docs/icon.png" /></p>

# negspacy: negation for spaCy

[![Built with spaCy](https://img.shields.io/badge/made%20with%20❤%20and-spaCy-09a3d5.svg)](https://spacy.io)

spaCy pipeline object for negating concepts in text. Based on the NegEx algorithm.

*NegEx - A Simple Algorithm for Identifying Negated Findings and Diseasesin Discharge Summaries
Chapman, Bridewell, Hanbury, Cooper, Buchanan*

## Installation and usage
Install the library
```bash
pip install negspacy
```

Import library
```python
from negspacy.negation import NegEx
```

Add negspacy pipeline object. Filtering on entity types is optional.
```python
negex = Negex(nlp)
nlp.add_pipe(negex, last=True, ent_types=["ENTITY"])
```

View negations
```python
for e in doc.ents:
	print(e.text, e._.negex)
```

## Contributing
[contributing](https://github.com/jenojp/negspacy/blob/master/CONTRIBUTING.md)

## Authors
* Jeno Pizarro

## License
[license](https://github.com/jenojp/negspacy/blob/master/LICENSE.md)