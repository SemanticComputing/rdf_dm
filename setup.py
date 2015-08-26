import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="rdf_dm",
    version="0.1.1",
    author="Mikko Koho",
    author_email="mikko.koho@iki.fi",
    description="Tools for data mining RDF datasets",
    license="MIT",
    keywords="rdf",
    url="",
    long_description=read('README'),
    packages=['rdf_dm'],
    install_requires=[
        'python-slugify >= 1.1.3',
        'rdflib >= 4.2.0',
        'SPARQLWrapper >= 1.6.4',
    ],
)
