"""Request handler of the module."""

import re
import logging
import requests
import functools
from io import StringIO

from ppp_libmodule.exceptions import ClientError
from ppp_datamodel import Triple, Resource, Sentence, Missing
from ppp_datamodel import Response, TraceItem

from .oeis import OEISEntry, ParseError

logger = logging.Logger('ppp_oeis')

sequence_re = re.compile('[0-9]+[, ]+[0-9]+[, ]+[0-9, ]+')

@functools.lru_cache(1024)
def query(logger, q):
    s = requests.get('http://oeis.org/search',
                     params={'fmt': 'text', 'q': q}).text
    return OEISEntry.query(logger=logger, fd=StringIO(s))

def sequence_to_resource(entry, cut=''):
    return Resource(', '.join(map(str, entry['sequence'])).split(cut, 1)[1])
def name_to_resource(entry, cut=''):
    return Resource(entry['name'])

class RequestHandler:
    def __init__(self, request):
        self.request = request

    def answer(self):
        if isinstance(self.request.tree, Triple) and \
                isinstance(self.request.tree.subject, Resource) and \
                isinstance(self.request.tree.predicate, Resource) and \
                isinstance(self.request.tree.object, Missing):
            method = getattr(self, 'on_' + self.request.tree.predicate.value, None)
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

