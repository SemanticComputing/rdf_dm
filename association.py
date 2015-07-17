import os
import re
from rdflib import Graph, namespace
import subprocess

from slugify import slugify

_pwd = os.path.dirname(os.path.realpath(__file__))

_itemset_separator = '|'
_predicate_object_separator = '-->'

_namespace_prefixes = dict(((str(uri), prefix + ':') for prefix, uri in namespace.NamespaceManager(Graph()).namespaces()))
    # list(namespace.NamespaceManager(Graph()).namespaces()) + \
_namespace_prefixes.update({'http://ldf.fi/schema/narc-menehtyneet1939-45/': 'sss:',
                            'http://ldf.fi/narc-menehtyneet1939-45/': 'ss:',
                            'http://xmlns.com/foaf/0.1/': 'foaf:',
                   })

import rdftools.helpers as h


def freq_items_by_class(graph, cl, ns_prefixes=_namespace_prefixes, minsup1=50, minsup2=25, minconf=90, minlift=200):
    """
    Get frequent items by class. Uses FIM package's implementation of fpgrowth algorithm.

    :type graph: rdflib.Graph
    :param cl: class resource
    """

    po_items = []  # list of lists

    if ns_prefixes:
        pattern = re.compile(r'\b(' + '|'.join(ns_prefixes.keys()) + r')\b')

    instances = h.get_class_instances(graph, cl)
    for i in instances:
        pos = []
        for (p, o) in graph.predicate_objects(i):
            if ns_prefixes:
                p = pattern.sub(lambda x: ns_prefixes[x.group()], p)
                o = pattern.sub(lambda x: ns_prefixes[x.group()], o)
            pos.append("{p}{sep}{o}".format(p=str(p), o=str(o), sep=_predicate_object_separator))
        po_items.append(pos)

    basket_file = '{pwd}/itemsets/rdf.{slug}.basket'.format(pwd=_pwd, slug=slugify(cl))

    # Write itemsets file
    with open(basket_file, encoding='UTF-8', mode='w+') as f:
        for po in po_items:
            if any(_itemset_separator in item for item in po):
                raise Exception('Separator symbol | found in items')
            f.write(_itemset_separator.join(po) + "\n")

    # Generate frequent itemsets
    return_code = subprocess.call("fpgrowth -ts -f\"|\" -s{sup} -v\" %s\" {file} {file}.freq_itemsets".
                                  format(sup=minsup1, file=basket_file), shell=True)

    if return_code:
        print(return_code)
        raise Exception('Error while running fpgrowth.')

    # Generate frequent association rules
    return_code = subprocess.call("fpgrowth -tr -f\"|\" -m2 -v\" %s,%c,%e\" -s{sup} -c{conf} -el -d{lift} {file} {file}.freq_rules".
                                  format(sup=minsup2, conf=minconf, lift=minlift, file=basket_file), shell=True)

    if return_code:
        print(return_code)

    # Parse frequent itemsets
    with open("{file}.freq_itemsets".format(file=basket_file), encoding='UTF-8', mode='r') as f:
        freq_itemsets = []
        for row in f.readlines():
            pred_objs = [po.split(sep=_predicate_object_separator) for po in row.split()[:-1]]
            support = float(row.split()[-1])
            freq_itemsets += [(pred_objs, support)]

    # Parse frequent rules
    with open("{file}.freq_rules".format(file=basket_file), encoding='UTF-8', mode='r') as f:
        freq_rules = []
        for row in f.readlines():
            row_parts = row.split()
            supp, conf, lift = (float(part) for part in row_parts[-1].split(','))
            consequents_string, antecedents_string = ' '.join(row_parts[:-1]).split(' <- ')
            ante = [po.split(_predicate_object_separator) for po in antecedents_string.split()]
            cons = [po.split(_predicate_object_separator) for po in consequents_string.split()]
            # freq_rules += [(ante, cons, supp, conf, lift)]
            freq_rules += [{'antecedents': ante,
                            'consequents': cons,
                            'support': supp,
                            'confidence': conf,
                            'lift': lift,
                            }]

    return freq_itemsets, freq_rules
