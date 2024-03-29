from setuptools import setup, find_packages

setup(
    name="python_files",
    version="1.0.0",
    author="rshanker779",
    author_email="rshanker779@gmail.com",
    description="Variety of python projects",
    license="MIT",
    python_requires=">=3.5",
    install_requires=[
        "black",
        "nltk",
        "lxml",
        "matplotlib",
        "pandas",
        "pre-commit",
        "praw",
        "psaw",
        "psycopg2",
        "requests",
        "rshanker779_common",
        "spacy",
        "sqlalchemy",
        "tqdm",
        "coverage",
    ],
    packages=find_packages(),
    entry_points={},
    test_suite="tests",
    dependency_links=[
        "git+https://rshanker779@github.com/rshanker779/rshanker779_common.git#egg=rshanker779_common"
    ],
)
print(
    "Note spacy model must also be downloaded with the command 'python -m spacy download en_core_web_sm'"
)
