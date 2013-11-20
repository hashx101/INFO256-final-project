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
        self.remaining = 1024 * 10

    def dataReceived(self, bytes):
        if self.remaining:
            display = bytes[:self.remaining]
            print('Response body:')
            pprint(loads(display))
            self.remaining -= len(display)

    def connectionLost(self, reason):
        print('Finished receiving body:', reason.getErrorMessage())


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
    d = agent.request(
        'POST',
        'http://localhost/theme-finder/src/php/similarsentences/similarsentences.php',
        HEADERS,
        body)    
    d.addBoth(printRequest)


def sendStringQuery(string, instance="shakespeare"):
    sendQuery(query=string,
              instance=instance,
              string_query='true',
              vector_query='false')


def sendVectorQuery(vector, instance="shakespeare", relevant=[], irrelevant=[]):
    sendQuery(query=vector,
              relevant=relevant,
              irrelevant=irrelevant,
              instance=instance,
              string_query='false',
              vector_query='true')


if __name__ == "__main__":
    agent = Agent(reactor)
    sendStringQuery("test")
    reactor.run()
