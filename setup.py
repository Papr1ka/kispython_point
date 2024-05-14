from setuptools import setup, find_packages
from os import path
from sphinx.application import Sphinx

Sphinx()

with open("./requirements.txt", encoding='utf-8') as file:
    requirements = file.readlines()


setup(
    name="kispython_point",
    version="0.0.1",
    install_requires=requirements,
    packages=find_packages(),
)
