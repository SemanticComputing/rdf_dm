"""Helper functions for rdf_dm"""

from itertools import chain
from urllib.parse import urlparse

from rdflib import Graph, RDF, URIRef, Literal, RDFS


def is_uri(uri):
    """
    Return True if given string seems like a valid URI.
    """
    return bool(urlparse(uri).scheme)


def read_graph_from_sparql(endpoint):
    """
    Read all triples from a SPARQL endpoint to an rdflib Graph.

    :param endpoint: A SPARQL endpoing
    :return: A new rdflib graph
    >>> read_graph_from_sparql("http://dbpedia.org/sparql")
    """
    # TODO: allow to specify graph name also

    from SPARQLWrapper import SPARQLWrapper, JSON

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

    :param graph: An RDF graph
    :type graph: rdflib.Graph
    """
    return sorted(set(graph.objects(None, RDF.type)))


def get_subclasses(graph, cl):
    return graph.transitive_subjects(RDFS.subClassOf, cl)


def get_class_instances(graph, cl, use_subclasses=True):
    """
    Get all instances of a class

    :param graph: An RDF graph
    :param cl: The class to get instances of
    :param use_subclasses: Also get instances of subclasses
    :type graph: rdflib.Graph
    """
    if use_subclasses:
        subclasses = list(get_subclasses(graph, cl))
        instances = chain(*(graph.subjects(RDF.type, subclass) for subclass in subclasses))
    else:
        instances = graph.subjects(RDF.type, cl)

    return instances


def classes_instances(graph, verbose=True, use_subclasses=True):
    """
    Get the number of instances per class, and print them if verbose=True.

    :param graph: An RDF graph
    :param verbose: print results
    :param use_subclasses: Also get instances of subclasses
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

def get_unknown_links(graph, precise=False):
    """
    Get URI references in graphs that are not in classes or class instances (or all subjects with precise=True).

    :param graphs: An RDF graph or list of graphs
    :param precise: Get all subjects, not only classes and their instances
    :return: List of URI references
    """
    if precise:
        known_uris = list(set(s for s in graph.subjects()))
    else:
        known_uris = list(set(get_classes(graph)) | set(list(get_class_instances(graph, None))))

    links = set(o for o in graph.objects() if type(o) != Literal)

    return list(set([o for o in links if o not in known_uris]))

def get_unlinked_uris(graph):
    """
    Get subject nodes that are not used as objects in graph

    :param graph:
    :return:
    """

    links = set(o for o in graph.objects() if type(o) != Literal)

    return set(list(s for s in graph.subjects() if s not in links))
