"""Helper functions for rdftools"""

from rdflib import Graph, RDF

def classes(graph):
    """
    Get all classes that have instances.

    :param graph:
    :return:
    """
    return graph.objects(None, RDF.type)

def classes_instances(graph, verbose=True):
    """
    Get number of instances per class.

    :type graph: rdflib.Graph
    """

    for cl in sorted(set(classes(graph))):
        instances = graph.subjects(RDF.type, cl)
        if verbose:
            print("Class {cl}, instances: {num}".format(cl=cl, num=len(list(instances))))

    return True

