from __future__ import print_function

from StringIO import StringIO

from twisted.internet import reactor
from twisted.internet.protocol import Protocol
from twisted.internet.defer import Deferred
from twisted.web.client import Agent
from twisted.web.client import FileBodyProducer
from twisted.web.http_headers import Headers

from pprint import pprint
from json import loads

import urllib
import random


TEST_1 = [4779, 12922, 19498, 30066, 32111, 32715, 43494, 48981, 54363, 68009, 93470]


HEADERS = Headers({'User-Agent': ['Twisted Web Client'],
                 'Origin': ['http://localhost'],
                 'Accept-Language': ['en-US','en'],
                 'Content-Type': ['application/x-www-form-urlencoded'],
                 'Accept': ['*/*'],
                 'Referer': ['http://localhost/theme-finder/'],
                 'X-Requested-With': ['XMLHttpRequest'],
                 'Connection': ['keep-alive']})


class BeginningPrinter(Protocol):
    def __init__(self, finished):
        self.finished = finished

    def dataReceived(self, bytes):
        display = bytes
        print('Response body:')
        pprint(loads(display))

    def connectionLost(self, reason):
        print('Finished receiving body:', reason.getErrorMessage())
        reason.printTraceback()


def printRequest(response):
    print('Response version:', response.version)
    print('Response code:', response.code)
    print('Response phrase:', response.phrase)
    print('Response headers:')
    print(list(response.headers.getAllRawHeaders()))
    finished = Deferred()
    response.deliverBody(BeginningPrinter(finished))
    return finished


def sendQuery(**kwargs):
    body = FileBodyProducer(StringIO(urllib.urlencode(kwargs)))  
    d = agent.request('POST',
                      'http://localhost/theme-finder/src/php/similarsentences/similarsentences.php',
                      HEADERS,
                      body)    
    return d
    


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

def sendFeatureQuery(instance="shakespeare", relevant=[], query={}):
    print('Calling feature query')
    return sendQuery(relevant=relevant,
                     query=query,
                     instance=instance,
                     string_query='false',
                     vector_query='false',
                     feature_query='true')  

def sendSimilar(relevant=[], instance="shakespeare"):
    d = sendFeatureQuery(instance, relevant)
    d.addCallback(lambda features: sendVectorQuery(features=features, instance=instance, relevant=relevant, irrelevant=[]))
    d.addCallback(printRequest)

    return d

def test(testset=TEST_1):
    startset = random.sample(testset, len(testset) / 2)
    d = sendSimilar(startset)
    d.addCallback(lambda vec: d.chainDeferred(sendVectorQuery(features=vec, relevant=startset)))


if __name__ == "__main__":
    agent = Agent(reactor)
    #sendStringQuery("test")
    #sendVectorQuery({"relevant":["12922","32715","37320"],"irrelevant":[]}, relevant=["12922","32715","37320"], irrelevant=[])
    #sendFeatureQuery(relevant=[12922,32715,37320]).addCallback(printRequest)
    #sendSimilar(relevant=[12922,32715,37320])
    test()
    reactor.run()
