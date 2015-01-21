from ppp_datamodel import Missing, Triple, Resource, Sentence
from ppp_datamodel.communication import Request, TraceItem, Response
from ppp_libmodule.tests import PPPTestCase
from ppp_oeis import app

class TestDefinition(PPPTestCase(app)):
    config_var = 'PPP_OEIS'
    config = ''
    def testBasics(self):
        q = Request('1', 'en', Triple(Resource('1 2 4 8'), Resource('definition'), Missing()), {}, [])
        r = self.request(q)
        self.assertGreater(len(r), 1, r)
        self.assertEqual(r[0].tree.value, 'Powers of 2: a(n) = 2^n.')
        self.assertEqual(r[0].tree.graph['name'], 'Powers of 2: a(n) = 2^n.')
        self.assertEqual(r[0].tree.graph['@id'], 'http://oeis.org/A000079')
        self.assertEqual(r[0].tree.graph['url'], '//oeis.org/A000079')

    def testNoAnswer(self):
        q = Request('1', 'en', Triple(Resource('1 2'), Resource('definition'), Missing()), {}, [])
        r = self.request(q)
        self.assertEqual(r, [])

    def testSentence(self):
        q = Request('1', 'en', Sentence('1, 2, 4, 8'), {}, [])
        r = self.request(q)
        self.assertGreater(len(r), 1, r)
        self.assertEqual(r[0].tree.value, 'Powers of 2: a(n) = 2^n.')

        q = Request('1', 'en', Sentence('1, 2, 4, 8?'), {}, [])
        r = self.request(q)
        self.assertGreater(len(r), 1, r)
        self.assertEqual(r[0].tree.value, 'Powers of 2: a(n) = 2^n.')
