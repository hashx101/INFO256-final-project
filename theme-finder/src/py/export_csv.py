# This file is to generate a table from the results
import test
import pickle
import csv
import numpy

result = pickle.load(open('results_20131215_141256'))
results = result['results']

#roch_type: "rocchio" or "pseudo"
def getCols(results, roch_type):
    dec = []
    reg = []
    roc = []
    pseu = []
    percentages = results.keys()
    percentages.sort()
    for percent in percentages:
        
        if(roch_type=='beta'):
            dec_rate = numpy.mean(results[percent]['ide_dec']['recalls'])
            reg_rate = numpy.mean(results[percent]['ide_regular']['recalls'])
            roc_rate = numpy.mean(results[percent]['rocchio']['recalls'])
            pseu_rate = numpy.mean(results[percent]['pseudo']['recalls'])
            pseu += [pseu_rate]
        else:
            dec_rate = results[percent]['ide_dec']['recall']
            reg_rate = results[percent]['ide_regular']['recall']
            roc_rate = results[percent]['rocchio']['recall']
            if(roch_type=='pseudo'):
                pseu_rate = results[percent]['pseudo']['recall']
                pseu += [pseu_rate]
        dec += [dec_rate]
        reg += [reg_rate]
        roc += [roc_rate]
    return {'ide_dec':dec, 'ide_reg':reg, 'rocchio':roc, 'pseudo':pseu}


#0.75
# results_20131215_141256
pseudo_result = pickle.load(open('results_20131215_141256'))
pseudo_results = pseudo_result['results']

dict_pseudo = getCols(pseudo_results, 'pseudo')
ide_dec = dict_pseudo['ide_dec']
ide_regular = dict_pseudo['ide_reg']
rocchio = dict_pseudo['rocchio']
pseudo = dict_pseudo['pseudo']


percentage = pseudo_results.keys()
percentage.sort()

rows = zip(percentage, ide_dec, ide_regular, rocchio, pseudo)

with open('result_pseudo_table_beta_075.csv', "wb") as f:
    writer = csv.writer(f)
    for row in rows:
        writer.writerow(row)


#0.5
#results_name_20131215_191213
pseudo_result = pickle.load(open('results_name_20131215_191213'))
pseudo_results = pseudo_result['results']

dict_pseudo = getCols(pseudo_results, 'beta')
ide_dec = dict_pseudo['ide_dec']
ide_regular = dict_pseudo['ide_reg']
rocchio = dict_pseudo['rocchio']
pseudo = dict_pseudo['pseudo']


percentage = pseudo_results.keys()
percentage.sort()

rows = zip(percentage, ide_dec, ide_regular, rocchio, pseudo)

with open('result_pseudo_table_beta05.csv', "wb") as f:
    writer = csv.writer(f)
    for row in rows:
        writer.writerow(row)

