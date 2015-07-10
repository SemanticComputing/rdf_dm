"""Helper functions for rdftools"""
from itertools import chain
from urllib.parse import urlparse

from rdflib import Graph, RDF, URIRef, Literal, RDFS


def is_uri(uri):
    """
    Return True if uri seems like a valid URI.
    """
    return bool(urlparse(uri).scheme)


def read_graph_from_sparql(endpoint="http://dbpedia.org/sparql"):
    """
    Read all triples from SPARQL endpoint to an rdflib Graph.

    :param endpoint:
    :return: A brand new graph
    """
    from SPARQLWrapper import SPARQLWrapper, JSON, TURTLE

    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery('SELECT * WHERE { ?s ?p ?o  }')
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    graph = Graph()

    for result in results["results"]["bindings"]:
        s = URIRef(result['s']['value'])
        p = URIRef(result['p']['value'])
        if result['o']['type'] in ['uri', 'bnode']:
            o = URIRef(result['o']['value'])
        elif result['o']['type'] in ['literal', 'typed-literal']:
            o = Literal(result['o']['value'])
        else:
            raise Exception('foo')

        graph.add((s, p, o))

    return graph


def get_classes(graph):
    """
    Get all distinct classes that have instances.

    :param graph:
    :return:
    """
    return sorted(set(graph.objects(None, RDF.type)))


def get_subclasses(graph, cl):
    return graph.transitive_subjects(RDFS.subClassOf, cl)


def get_class_instances(graph, cl, use_subclasses=True):
    """
    Get class instances

    :param graph:
    :param clas:
    :param use_subclasses:
    :return:
    """
    if use_subclasses:
        subclasses = list(get_subclasses(graph, cl))
        instances = chain(*(graph.subjects(RDF.type, subclass) for subclass in subclasses))
    else:
        instances = graph.subjects(RDF.type, cl)

    return instances


def classes_instances(graph, verbose=True, use_subclasses=True):
    """
    Print number of instances per class.

    :type graph: rdflib.Graph
    """

    class_data = {}

    for cl in get_classes(graph):

        instances = list(get_class_instances(graph, cl, use_subclasses=use_subclasses))
        subclasses = list(get_subclasses(graph, cl))

        if verbose:
            print("Class {cl}, instances: {num}".format(cl=cl, num=len(list(instances))))
            if subclasses and len(subclasses) > 1:
                print("\t with subclasses {subs}".format(subs=', '.join([str(sub) for sub in subclasses])))

        class_data[cl] = (instances, subclasses)

    return class_data
