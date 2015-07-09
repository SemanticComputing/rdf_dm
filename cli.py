"""Command line interface for analysis"""

import argparse


parser = argparse.ArgumentParser(description='Analyse RDF dataset')
parser.add_argument('input', help='RDF input source', type=float)
parser.add_argument('var2', help='variable 2', type=float)
args = parser.parse_args()

for model in prediction_models:
    #print 'Model %s' % (model.model)
    value_tuple = input_scaler.transform((args.var1, args.var2, args.var3, args.var4))
    prediction = model.predict(value_tuple)
    print('Model %s: %s' % (model.name, prediction))
