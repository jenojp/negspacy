from setuptools import setup, find_packages
import io

setup(
    name = 'negspacy',
    version = 'v1.0.4',
    url = 'https://github.com/jenojp/negspacy',
    author = 'Jeno Pizarro',
    author_email = 'jenopizzaro@gmail.com',
    description = 'A spaCy pipeline object for negation.',
    long_description=io.open("README.md", encoding="utf8").read(),
    long_description_content_type="text/markdown",
    keywords = ["nlp spacy SpaCy negation"],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Scientific/Engineering'
    ],
    packages = find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    license="MIT",
    install_requires=[
        "spacy>=3.0.1,<4.0.0",
        ],
    tests_require=[
        "pytest",
        ],
    python_requires='>=3.6.0',
)