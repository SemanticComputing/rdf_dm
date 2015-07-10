from collections import defaultdict
import os
from rdflib import Graph, RDF
import subprocess

from slugify import slugify

_pwd = os.path.dirname(os.path.realpath(__file__))


import rdftools.helpers as h

# def create_itemsets(graph):
    # g = Graph()
    # g.parse('/home/mikko/HALIAS/JavaOutput/halias_taxon_ontology.ttl', format="turtle")

    # triple_items = ["{s} - {p} - {o}".format(s=str(s), p=str(p), o=str(o)) for (s, p, o) in g]

def frequent_items(graph):
    '''
    Analyse itemsets using command line implementation of FP-growth algorithm from FIM package.

    :return:
    '''

    po_items = defaultdict(list)

    for s, p, o in graph:
        po_items[s].append("{p} {o}".format(s=str(s), p=str(p), o=str(o)))

    with open('{pwd}/itemsets/rdf.basket'.format(pwd=_pwd), encoding='UTF-8', mode='w+') as f:
        for s, po in po_items.items():
            f.write(','.join(po) + "\n")

    return_code = subprocess.call("fpgrowth -ts -f\",\" -s30 rdf.basket rdf.basket.freq_itemsets", shell=True)

    if return_code:
        print(return_code)
        raise Exception('FP-growth from FIM package not found.')

    return_code = subprocess.call("fpgrowth -tr -f\",\" -s20 -c95 -el -d200 rdf.basket rdf.basket.freq_rules", shell=True)

    # TODO: Get lift to output

    if return_code:
        print(return_code)


def freq_items_by_class(graph, cl, minsup1=50, minsup2=25, minconf=90):
    """

    :type graph: rdflib.Graph
    :param cl: class resource
    """

    po_items = []  # list of lists

    instances = h.get_class_instances(graph, cl)
    for i in instances:
        po_items.append(["{p}-->{o}".format(p=str(p), o=str(o)) for (p, o) in graph.predicate_objects(i)])

    # return po_items

    basket_file = '{pwd}/itemsets/rdf.{slug}.basket'.format(pwd=_pwd, slug=slugify(cl))

    with open(basket_file, encoding='UTF-8', mode='w+') as f:
        for po in po_items:
            f.write(','.join(po) + "\n")

    return_code = subprocess.call("fpgrowth -ts -f\",\" -s{sup} {file} {file}.freq_itemsets".
                                  format(sup=minsup1, file=basket_file), shell=True)

    if return_code:
        print(return_code)
        raise Exception('FP-growth from FIM package not found.')

    return_code = subprocess.call("fpgrowth -tr -f\",\" -s{sup} -c{conf} -el -d200 {file} {file}.freq_rules".
                                  format(sup=minsup2, conf=minconf, file=basket_file), shell=True)

    # TODO: Get lift to output

    if return_code:
        print(return_code)
