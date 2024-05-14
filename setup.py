from setuptools import setup, find_packages, Command
from setuptools.command.build_ext import build_ext
from os import path
from docs.builddoc import BuildDoc


with open("./requirements.txt", encoding='utf-8') as file:
    requirements = file.readlines()

cmdclass = {'build_sphinx': BuildDoc}

name = "kispython_point"
version = "0.0.1"

setup(
    name=name,
    version=version,
    install_requires=requirements,
    packages=find_packages(),
    command_options={
        'build_sphinx': {
            'project': ('setup.py', name),
            'version': ('setup.py', version),
            'release': ('setup.py', version),
            'source_dir': ('setup.py', 'docs/source'),
        },
    },
    cmdclass=cmdclass
)
