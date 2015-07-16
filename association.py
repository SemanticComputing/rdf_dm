from collections import defaultdict
import os
from rdflib import Graph, RDF
import subprocess

from slugify import slugify

_pwd = os.path.dirname(os.path.realpath(__file__))

_itemset_separator = '|'
_predicate_object_separator = '-->'


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


def freq_items_by_class(graph, cl, minsup1=50, minsup2=25, minconf=90, minlift=200):
    """
    Get frequent items by class. Uses FIM package's implementation of fpgrowth algorithm.

    :type graph: rdflib.Graph
    :param cl: class resource
    """

    po_items = []  # list of lists

    instances = h.get_class_instances(graph, cl)
    for i in instances:
        po_items.append(["{p}{sep}{o}".format(p=str(p), o=str(o), sep=_predicate_object_separator)
                        for (p, o) in graph.predicate_objects(i)])

    # return po_items

    basket_file = '{pwd}/itemsets/rdf.{slug}.basket'.format(pwd=_pwd, slug=slugify(cl))

    with open(basket_file, encoding='UTF-8', mode='w+') as f:
        for po in po_items:
            if any(_itemset_separator in item for item in po):
                raise Exception('Separator symbol | found in items')
            f.write(_itemset_separator.join(po) + "\n")

    return_code = subprocess.call("fpgrowth -ts -f\"|\" -s{sup} -v\" %s\" {file} {file}.freq_itemsets".
                                  format(sup=minsup1, file=basket_file), shell=True)

    if return_code:
        print(return_code)
        raise Exception('Error while running fpgrowth.')

    return_code = subprocess.call("fpgrowth -tr -f\"|\" -m2 -v\" %s,%c,%e\" -s{sup} -c{conf} -el -d{lift} {file} {file}.freq_rules".
                                  format(sup=minsup2, conf=minconf, lift=minlift, file=basket_file), shell=True)

    if return_code:
        print(return_code)

    with open("{file}.freq_itemsets".format(file=basket_file), encoding='UTF-8', mode='r') as f:
        freq_itemsets = []
        for row in f.readlines():
            pred_objs = [po.split(sep=_predicate_object_separator) for po in row.split()[:-1]]
            support = float(row.split()[-1])
            freq_itemsets += [(pred_objs, support)]

    with open("{file}.freq_rules".format(file=basket_file), encoding='UTF-8', mode='r') as f:
        freq_rules = []
        for row in f.readlines():
            row_parts = row.split()
            supp, conf, lift = (float(part) for part in row_parts[-1].split(','))
            ante, cons = (part.split(_predicate_object_separator) for part in ' '.join(row_parts[:-1]).split(' <- '))
            print('Ante: %s, \t Cons: %s' % (ante, cons))
            freq_rules += [(ante, cons, supp, conf, lift)]


    return freq_itemsets, freq_rules
