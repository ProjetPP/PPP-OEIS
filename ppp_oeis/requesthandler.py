"""Request handler of the module."""

import re
import logging
import requests
import functools
from io import StringIO

from ppp_libmodule.exceptions import ClientError
from ppp_datamodel import Triple, Resource, Sentence, Missing, JsonldResource
from ppp_datamodel import Response, TraceItem

from .oeis import OEISEntry, ParseError

logger = logging.Logger('ppp_oeis')

sequence_re = re.compile('[0-9]+[, ]+[0-9]+[, ]+[0-9, ]+')

@functools.lru_cache(1024)
def query(logger, q):
    s = requests.get('http://oeis.org/search',
                     params={'fmt': 'text', 'q': q}).text
    return OEISEntry.query(logger=logger, fd=StringIO(s))

def graph_for_entry(entry):
    url = '//oeis.org/%s' % entry['id']
    graph = {'@context': 'http://schema.org',
             '@id': 'http:' + url,
             'type': 'Thing',
             'name': entry['name'],
             'description': [
                 {'language': 'en', '@value': x}
                 for x in entry['comments']
                 ],
             'potentialAction': {
                 '@type': 'ViewAction',
                 'image': '//oeis.org/favicon.ico',
                 'target': url,
                 'name': [
                     {'@language': 'en',
                      '@value': 'View on OEIS'},
                     {'@language': 'fr',
                      '@value': 'Voir sur OEIS'},
                     ]
                 },
           }
    return graph

def sequence_to_resource(entry, cut=''):
    value = ', '.join(map(str, entry['sequence'])).split(cut, 1)[1]
    graph = graph_for_entry(entry)
    return JsonldResource(value, graph=graph)
def name_to_resource(entry, cut=''):
    graph = graph_for_entry(entry)
    return JsonldResource(entry['name'], graph=graph)

class RequestHandler:
    def __init__(self, request):
        self.request = request

    def answer(self):
        if isinstance(self.request.tree, Triple) and \
                isinstance(self.request.tree.subject, Resource) and \
                isinstance(self.request.tree.object, Missing):
            # TODO: actually traverse the tree (+ less ugly code)
            for predicate in self.request.tree.predicate_set:
                method = getattr(self, 'on_' + predicate.value, None)
                if method is not None:
                    break
            value = self.request.tree.subject.value
        elif isinstance(self.request.tree, Sentence):
            method = self.on_definition
            value = self.request.tree.value.strip('?')
        else:
            return []
        if not method:
            return []
        l = method(value)

        meas = {'relevance': 1, 'accuracy': 1}
        responses = map(lambda tree:Response('en', tree, meas,
                        self.request.trace + [TraceItem('OEIS', tree, meas)]),
                        l)
        return responses

    def on_following(self, v):
        if not sequence_re.match(v):
            return []
        q = v.replace(' ', ',')
        cut = v.replace(' ', ', ') + ', '
        (_, l) = query(logger, q)
        return map(lambda x:sequence_to_resource(x, cut), l)

    def on_definition(self, v):
        if not sequence_re.match(v):
            return []
        q = v.replace(' ', ',')
        cut = v.replace(' ', ', ') + ', '
        (_, l) = query(logger, q)
        return map(lambda x:name_to_resource(x, cut), l)

