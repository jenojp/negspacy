from setuptools import setup, find_packages

setup(
    name = 'negspacy',
    version = 'v0.1.0-alpha',
    url = 'https://github.com/jenojp/negspacy',
    author = 'Jeno Pizarro',
    author_email = 'jenopizzaro@gmail.com',
    description = 'A spaCy pipeline object for negation.',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    keywords = ["nlp spacy SpaCy negation"],
    classifiers=[
        'Intended Audience :: Science/Research',
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
    ],
    packages = find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    license="MIT",
    install_requires=[
        "spacy==2.1.8",
        ],
    tests_require=[
        "pytest",
        ],
    python_requires='>=3.6.0',
)