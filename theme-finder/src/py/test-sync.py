from __future__ import print_function


from pprint import pprint
from json import loads
import urllib2
import urllib
import random
import math
import copy


TEST_1 = [4779, 12922, 19498, 30066, 32111, 32715, 43494, 48981, 54363, 68009, 93470]



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
    the_page = response.read()
    try:
        return loads(the_page)
    except:
        return the_page


def sendStringQuery(string, instance="shakespeare"):
    return sendQuery(query=string,
                     instance=instance,
                     string_query='true',
                     vector_query='false')



def sendVectorQuery(features=None, instance="shakespeare", relevant=[], irrelevant=[]):
    print('Calling vector query')
    return sendQuery(vector={'relevant': relevant,
                             'irrelevant': irrelevant,
                             'features': features},
                    relevant=relevant,
                    irrelevant=irrelevant,
                    instance=instance,
                    string_query='false',
                    vector_query='true')

def test(testset=TEST_1):
    startset = testset[:len(testset) / 2]
    response = sendVectorQuery(instance='shakespeare',
                               features=[],
                               relevant=startset,
                               irrelevant=[])
    relevant = copy.copy(startset)
    for sentence in response['sentences']:
        sentence_id = int(sentence['id'])
        if sentence_id in testset and sentence_id not in relevant:
            relevant.append(sentence_id)

    print(testset)
    print(startset)
    print(relevant)
    


if __name__ == "__main__":
    #sendStringQuery("test")
    #sendVectorQuery({"relevant":["12922","32715","37320"],"irrelevant":[]}, relevant=["12922","32715","37320"], irrelevant=[])
    #sendFeatureQuery(relevant=[12922,32715,37320]).addCallback(printRequest)
    test()