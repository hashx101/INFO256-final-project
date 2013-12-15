import test
import pickle
import csv

result = pickle.load(open('results_20131214231244'))
results = result['results']

def getCols(results):
    dec = []
    reg = []
    roc = []
    percentages = results.keys()
    percentages.sort()
    for percent in percentages:
        dec_rate = results[percent]['ide_dec']['recall']
        reg_rate = results[percent]['ide_regular']['recall']
        roc_rate = results[percent]['rocchio']['recall']
        dec += [dec_rate]
        reg += [reg_rate]
        roc += [roc_rate]
    return [dec, reg, roc]
    
ide_dec, ide_regular, rocchio = getCols(results)
percentage = results.keys()
percentage.sort()


rows = zip(percentage, ide_dec, ide_regular, rocchio)

with open('result_table.csv', "wb") as f:
    writer = csv.writer(f)
    for row in rows:
        writer.writerow(row)