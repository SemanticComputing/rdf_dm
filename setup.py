import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="rdf-tools",
    version="0.0.1",
    author="Mikko Koho",
    author_email="mikko.koho@iki.fi",
    description="Tools for usage and analysis of RDF datasets",
    license="MIT",
    keywords="rdf",
    url="",
    long_description=read('README'),
)
