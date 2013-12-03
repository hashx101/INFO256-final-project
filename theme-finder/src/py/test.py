from __future__ import print_function


from pprint import pprint
from json import loads
import urllib2
import urllib
import random
import math
import copy
from collections import defaultdict

# life is a stage
TEST_1 = [4779, 19498, 30066, 32111, 32715, 43494, 48981, 54363, 68009, 93470]


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

def test(testset=TEST_1):
    results = {}
    for percent in map(lambda i: i * .1, range(2,10)):
        results[str(percent)] = {}
        for fn in VEC_ADJ_FNS:
            results[str(percent)][fn] = {'recalls': []}
        for _ in range(5):
            # sample percent of subset for running fns against
            startset = random.sample(testset, int(math.ceil(len(testset) * percent)))
            for fn in VEC_ADJ_FNS:
                print('testing {}'.format(fn))
                response = sendVectorQuery(vector_function=fn,
                                           relevant=startset)
                relevant = copy.copy(startset)
                for sentence in response['sentences']:
                    sentence_id = int(sentence['id'])
                    if sentence_id in testset and sentence_id not in relevant:
                        relevant.append(sentence_id)
                to_find = set(testset).difference(set(startset))
                found_not_in_start = set(relevant).difference(startset)


                results[str(percent)][fn]['recalls'].append(float(len(found_not_in_start))/len(to_find))

                print(testset)
                print(startset)
                print(relevant)
            
        for fn in VEC_ADJ_FNS:
            recalls = results[str(percent)][fn]['recalls']
            results[str(percent)][fn]['recall'] = float(sum(recalls))/len(recalls)

    pprint(results)


if __name__ == "__main__":
    #sendStringQuery("test")
    #print(sendQuery(vector_query='true', instance='shakespeare', relevant=[19498]))
    test()