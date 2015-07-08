from collections import defaultdict
from rdflib import Graph
import subprocess


def create_itemsets(graph):
    # g = Graph()
    # g.parse('/home/mikko/HALIAS/JavaOutput/halias_taxon_ontology.ttl', format="turtle")

    # triple_items = ["{s} - {p} - {o}".format(s=str(s), p=str(p), o=str(o)) for (s, p, o) in g]
    po_items = defaultdict(list)

    for s, p, o in graph:
        po_items[s].append("{p} {o}".format(s=str(s), p=str(p), o=str(o)))

    with open('./rdf.basket', encoding='UTF-8', mode='w') as f:
        for s, po in po_items.items():
            f.write(', '.join(po) + "\n")


def analyse_itemsets():
    '''
    Analyse itemsets using command line implementation of FP-growth algorithm from FIM package.

    :return:
    '''

    return_code = subprocess.call("fpgrowth -ts -s30 rdf.basket rdf.basket.freq_itemsets", shell=True)

    if return_code:
        print(return_code)
        raise Exception('FP-growth from FIM package not found.')

    return_code = subprocess.call("fpgrowth -tr -s20 -c95 -el -d200 rdf.basket rdf.basket.freq_rules", shell=True)

    # TODO: Get lift to output

    if return_code:
        print(return_code)


