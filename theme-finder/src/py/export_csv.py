import test
import pickle
import csv

result = pickle.load(open('results_20131214231244'))
results = result['results']

#roch_type: "rocchio" or "pseudo"
def getCols(results, roch_type):
    dec = []
    reg = []
    roc = []
    percentages = results.keys()
    percentages.sort()
    for percent in percentages:
        dec_rate = results[percent]['ide_dec']['recall']
        reg_rate = results[percent]['ide_regular']['recall']
        roc_rate = results[percent][roch_type]['recall']
        dec += [dec_rate]
        reg += [reg_rate]
        roc += [roc_rate]
    return [dec, reg, roc]
    
ide_dec, ide_regular, rocchio = getCols(results, 'rocchio')
percentage = results.keys()
percentage.sort()
rows = zip(percentage, ide_dec, ide_regular, rocchio)

with open('result_table.csv', "wb") as f:
    writer = csv.writer(f)
    for row in rows:
        writer.writerow(row)


#pseudo_result = pickle.load(open('results_20131215001225'))
pseudo_result = pickle.load(open('results_20131215011249'))
pseudo_results = pseudo_result['results']
ide_dec, ide_regular, pseudo_roch = getCols(pseudo_results, 'pseudo')
percentage = pseudo_results.keys()
percentage.sort()

rows = zip(percentage, ide_dec, ide_regular, pseudo_roch)

with open('result_pseudo_table.csv', "wb") as f:
    writer = csv.writer(f)
    for row in rows:
        writer.writerow(row)
