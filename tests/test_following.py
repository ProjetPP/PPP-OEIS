from ppp_datamodel import Missing, Triple, Resource
from ppp_datamodel.communication import Request, TraceItem, Response
from ppp_libmodule.tests import PPPTestCase
from ppp_oeis import app

class TestFollowing(PPPTestCase(app)):
    config_var = 'PPP_OEIS'
    config = ''
    def testBasics(self):
        q = Request('1', 'en', Triple(Resource('1 2 4 8'), Resource('following'), Missing()), {}, [])
        r = self.request(q)
        self.assertGreater(len(r), 1, r)
        self.assertTrue(r[0].tree.value.startswith('16, 32, 64'), r[0])
