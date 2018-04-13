"""Helper functions for rdf_dm"""

import logging
from itertools import chain
from time import sleep
from urllib.parse import urlparse

from rdflib import Graph, RDF, URIRef, Literal, RDFS

log = logging.getLogger(__name__)


def is_uri(uri):
    """
    Return True if given string seems like a valid URI.
    """
    return bool(urlparse(uri).scheme)


def read_graph_from_sparql(endpoint, graph_name=None, retry=10):
    """
    Read all triples from a SPARQL endpoint to an rdflib Graph.

    :param retry: number of retries
    :param graph_name: Graph URI
    :param endpoint: SPARQL endpoint
    :return: A new rdflib graph
    """
    from SPARQLWrapper import SPARQLWrapper, JSON

    sparql = SPARQLWrapper(endpoint)
    if graph_name:
        sparql.setQuery('SELECT * FROM <%s> WHERE { ?s ?p ?o  }' % (graph_name,))
    else:
        sparql.setQuery('SELECT * WHERE { ?s ?p ?o  }')
    sparql.setReturnFormat(JSON)

    results = {}
    while retry:
        try:
            results = sparql.query().convert()
            retry = 0
        except ValueError:
            retry -= 1
            if retry:
                log.error('SPARQL query result cannot be parsed, waiting before retrying...')
                sleep(2)
            else:
                raise

    graph = Graph()

    for result in results["results"]["bindings"]:
        s = URIRef(result['s']['value'])
        p = URIRef(result['p']['value'])
        o = result['o']

        if o['type'] in ['uri', 'bnode']:
            rdf_o = URIRef(o['value'])
        elif o['type'] in ['literal', 'typed-literal']:
            lang = o.get('xml:lang')
            datatype = o.get('datatype')
            rdf_o = Literal(o['value'], lang=lang, datatype=datatype)
        else:
            raise ValueError('Unknown RDF node type: {}'.format(o['type']))

        graph.add((s, p, rdf_o))

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
    Get subject nodes that are not used as predicates or objects in graph

    :param graph:
    :return:
    """

    links = set(o for o in graph.objects() if type(o) != Literal)
    preds = set(p for p in graph.predicates())

    used_uris = links | preds

    return list(set(s for s in graph.subjects() if s not in used_uris))

def get_instance_subgraphs(graph, cl):
    """
    Get subgraphs of each instance of a given class.

    :param cl:
    :param graph:
    :return:
    """
    instances = get_class_instances(graph, cl)
    subgraphs = []

    for instance in instances:
        subg = Graph()
        subg.add(graph[instance::])

        # TODO: Traverse links (until reaches another instance) and add statements

        subgraphs.append(subg)

    return subgraphs

