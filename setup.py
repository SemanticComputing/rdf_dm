import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="rdf_dm",
    version="0.1.0",
    author="Mikko Koho",
    author_email="mikko.koho@iki.fi",
    description="Tools for data mining tasks with RDF datasets",
    license="MIT",
    keywords="rdf",
    url="",
    long_description=read('README'),
    install_requires=[
        'python-slugify >= 1.1.3',
        'rdflib >= 4.2.0',
        'SPARQLWrapper >= 1.6.4',
    ],
)
