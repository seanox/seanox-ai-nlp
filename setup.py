# setup.py

from setuptools import setup, find_packages

setup(
    name="seanox_ai_nlp",
    version="0.0.0",
    packages=find_packages(),
    author="Seanox Software Solutions",
    description=(
        "Modular project designed to support Natural Language Processing (NLP)."
        " It comprises various packages and modules, each of which extends or"
        " simplifies specific aspects of language processing"
    ),
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/seanox/seanox-ai-nlp",
    license="Apache-2.0",
    python_requires=">=3.9",
)
