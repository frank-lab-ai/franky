import unittest
# import _context
import json
import uuid
import time
from frank.alist import Alist
from frank.alist import Attributes as tt
from frank import explain
from frank.cache import neo4j
import frank.cache.logger as clogger


class TestCaching(unittest.TestCase):

    # def test_temporal(self):
    #     alists = explain.Explanation().read_blanket_nodes('b10d4984066b4991ad551afd8022d9fa', 0, 2)
    #     self.assertTrue(len(alists) > 0,
    #                     "should have more than one element")

    # def test_generate_explanation(self):
    #     n_star_id = 21014
    #     blanket_len = 2
    #     session_id = 'be3aa30df83d42968be5e7d9d7b8b6fb'
    #     alists = explain.Explanation().read_blanket_nodes(session_id, n_star_id, blanket_len)
    #     explanation = explain.Explanation().generateExplanation(node_id=n_star_id, graphAlists=alists, blanket_len=blanket_len)
    #     print(json.dumps(explanation, indent=2))
    #     self.assertTrue(len(explanation["all"]) > 0, "explanation should not be empty")

    # def test_get_graph(self):
    #     graph = cache.neo4j.get_graph(sessionId="10043")
    #     self.assertTrue(len(graph > 0, "must be a non-empty graph"))

    # def test_get_node(self):
    #     node = cache.neo4j.get_node('j6ggh72dvs48lw5cst1zn','101')
    #     self.assertTrue(node.id == "101", "node id does not match")

    # def test_search_cache(self):
    #     alistToInstantiate = Alist(**{tt.SUBJECT: 'France', tt.PROPERTY: 'population',
    #                      tt.OBJECT: '?x', tt.TIME: '2026', tt.OPVAR: '?x', tt.COST: 1})
    #     results = cache.neo4j.search_cache(alist_to_instantiate=alistToInstantiate,
    #                                                   attribute_to_instantiate=tt.OBJECT,
    #                                                   search_attributes=[tt.SUBJECT, tt.PROPERTY, tt.TIME])
    #     self.assertTrue(results[0], "must be True")

    def test_save_neo4j(self):
        a = Alist(**{tt.ID: '1', tt.OPVAR: '$x $y',
                     '$x': '?x1', '$y': '?y1', '?_lte_': ''})
        b = Alist(**{tt.ID: '2', tt.OPVAR: '?x1', '?x1': 30})

        a.link_child(b)
        sessionId = "TEST" + uuid.uuid4().hex
        clogger.Logging().log(('neo4j', a, None, None, sessionId))
        clogger.Logging().log(('neo4j', b, a, "temporal", sessionId))
        # sleep to allow graph store threads to finish
        time.sleep(2)
        c = neo4j.get_node(sessionId, b.id)
        c = Alist(**c)

        self.assertEqual(b.id, c.id, msg=f'{sessionId}, {b}, {c}')


if __name__ == "__main__":
    unittest.main()
