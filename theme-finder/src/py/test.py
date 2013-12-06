from __future__ import print_function


from pprint import pprint
from json import loads
import urllib2
import urllib
import random
import math
import copy
from collections import defaultdict
import pylab
import testsets as ts




HEADERS = {'User-Agent': ['Twisted Web Client'],
                 'Origin': ['http://localhost'],
                 'Accept-Language': ['en-US','en'],
                 'Content-Type': ['application/x-www-form-urlencoded'],
                 'Accept': ['*/*'],
                 'Referer': ['http://localhost/theme-finder/'],
                 'X-Requested-With': ['XMLHttpRequest'],
                 'Connection': ['keep-alive']}

def sendQuery(**kwargs):
    data = urllib.urlencode(kwargs)
    req = urllib2.Request('http://localhost/theme-finder/src/php/similarsentences/similarsentences.php', data)
    response = urllib2.urlopen(req)
    for line in response:
        try:
            return loads(line)
        except:
            print('Derped on {}'.format(line))


def sendStringQuery(string, instance="shakespeare"):
    return sendQuery(query=string,
                     instance=instance,
                     string_query='true',
                     vector_query='false')



def sendVectorQuery(query={'relevant': [],
                           'irrelevant': [],
                           'features': []},
                    vector_function='rocchio',
                    instance="shakespeare",
                    relevant=[],
                    irrelevant=[]):
    print('Calling vector query')
    return sendQuery(query=query,
                     vector_function=vector_function,
                     relevant=relevant,
                     irrelevant=irrelevant,
                     instance=instance,
                     string_query='false',
                     vector_query='true')

def sendFeatureQuery(instance="shakespeare", relevant=[], irrelevant=[]):
    print('Calling feature query')
    return sendQuery(relevant=relevant,
                     irrelevant=irrelevant,
                     instance=instance,
                     string_query='false',
                     vector_query='true')

VEC_ADJ_FNS = ['rocchio', 'ide_dec', 'ide_regular']

def test(testset=ts.TEST_3):
    instance = testset['instance']
    relevant = testset['relevant']
    irrelevant = testset['irrelevant']
    percentages = map(lambda i: i * .1, range(1,5))
    results = [0] * len(percentages)
    for index, percent in enumerate(percentages):
        results[index] = {}
        for fn in VEC_ADJ_FNS:
            results[index][fn] = {'recalls': []}
        for _ in range(5):
            # sample percent of subset for running fns against
            relevant_sample = random.sample(relevant, int(math.ceil(len(relevant) * percent)))
            irrelevant_sample = random.sample(irrelevant, int(math.ceil(len(irrelevant) * percent)))
            for fn in VEC_ADJ_FNS:
                response = sendVectorQuery(vector_function=fn,
                                           relevant=relevant_sample,
                                           irrelevant=irrelevant_sample,
                                           instance=instance)
                relevant_start = copy.copy(relevant_sample)
                for sentence in response['sentences']:
                    sentence_id = int(sentence['id'])
                    if sentence_id in relevant and sentence_id not in relevant_start:
                        relevant_start.append(sentence_id)
                to_find = set(relevant).difference(set(relevant_sample))
                found_not_in_start = set(relevant_start).difference(relevant_sample)


                results[index][fn]['recalls'].append(float(len(found_not_in_start))/len(to_find))
            
        for fn in VEC_ADJ_FNS:
            recalls = results[index][fn]['recalls']
            results[index][fn]['recall'] = float(sum(recalls))/len(recalls)

    pprint(results)

    x_list = [percentages, percentages, percentages]
    y_list = []
    label_list = []
    offset = 0
    for fn in VEC_ADJ_FNS:
        t = []
        for index in range(len(percentages)):
            t.append(results[index][fn]['recall'] + offset)
        y_list.append(tuple(t))
        label_list.append(fn)
        offset += .001
    print(zip(y_list, label_list))
    graph(x_list, y_list, label_list)


def graph(x_list, y_list, label_list):
    for x, y, label in zip(x_list, y_list, label_list):
        pylab.plot(x, y, label=label)
    pylab.legend()
    pylab.show()


if __name__ == "__main__":
    #sendStringQuery("test")
    #print(sendQuery(vector_query='true', instance='shakespeare', relevant=[19498]))
    test()