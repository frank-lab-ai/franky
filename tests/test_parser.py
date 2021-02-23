import unittest
import frank.query_parser.parser


class TestParser(unittest.TestCase):
    def test_parse_x_of_y_in_year(self):
        query = "what is the population of France in 2020"
        parser = frank.query_parser.parser.Parser()
        output = parser.getNextSuggestion(query)
        print(output)
        self.assertEqual(output['template'], ['propclass', 'of', 'entity', 'in', 'datetime'])
    
    def test_parse_wh_X_of_y(self):
        query = "who is the president of Ghana"
        parser = frank.query_parser.parser.Parser()
        output = parser.getNextSuggestion(query)
        print(output)

        self.assertEqual(output['template'], ['propclass', 'of', 'entity'])
    
    def test_parse_X_of_y(self):
        query = "president of capital of Ghana"
        parser = frank.query_parser.parser.Parser()
        output = parser.getNextSuggestion(query)
        print(output)

        self.assertEqual(output['template'], ['propclass', 'of', 'propclass', 'of','entity'])

    def test_parse_wh_prop_obj(self):
        # query = "who is the president of Ghana"
        query = "who sang Infinite Things?"
        parser = frank.query_parser.parser.Parser()
        output = parser.getNextSuggestion(query)
        print(output)

        self.assertEqual(output['template'], ['verb', 'propclass'])

    def test_parse_entity_props(self):
        query = "sara bareilles songs"
        # query = "Ghana population"
        parser = frank.query_parser.parser.Parser()
        output = parser.getNextSuggestion(query)
        print(output)

        self.assertEqual(output['template'], ['entity', 'propclass'])

    def test_parse_x_of_y(self):
        query = "theme song of Friends"
        # query = "Ghana population"
        parser = frank.query_parser.parser.Parser()
        output = parser.getNextSuggestion(query)
        print(output)

        self.assertEqual(output['template'], ['propclass', 'of', 'propclass'])

    
    def test_parse_prop_xx_of_entity(self):
        query = "composed the national anthem of Ghana"
        # query = "Ghana population"
        parser = frank.query_parser.parser.Parser()
        output = parser.getNextSuggestion(query)
        print(output)

        self.assertEqual(output['template'], ['verb', 'propclass', 'of', 'entity'])

    
    def test_parse_prop_xx_of_y(self):
        query = "sang theme song of Friends"
        # query = "Ghana population"
        parser = frank.query_parser.parser.Parser()
        output = parser.getNextSuggestion(query)
        print(output)

        self.assertEqual(output['template'], ['verb', 'propclass', 'of', 'propclass'])

    def test_parse_nn_pp(self):
        query = "Friends theme song"
        # query = "Ghana population"
        parser = frank.query_parser.parser.Parser()
        output = parser.getNextSuggestion(query)
        print(output)

        self.assertEqual(output['template'], ['propclass', 'propclass'])

    def test_parse_nn_pps(self):
        query = "Friends theme songs"
        # query = "Ghana population"
        parser = frank.query_parser.parser.Parser()
        output = parser.getNextSuggestion(query)
        print(output)

        self.assertEqual(output['template'], ['propclass', 'propclass'])

    def test_parse_nn_pps2(self):
        query = "How many albums did the Beetles release"
        # query = "Ghana population"
        parser = frank.query_parser.parser.Parser()
        output = parser.getNextSuggestion(query)
        print(output)

        self.assertEqual(output['template'], ['propclass', 'propclass'])

    def test_parse_when(self):
        query = "When did Taylor Swift recorded Exile"
        # query = "Ghana population"
        parser = frank.query_parser.parser.Parser()
        output = parser.getNextSuggestion(query)
        print(output)

        self.assertEqual(output['template'], ['when', 'entity', 'propclass', 'entity'])
    
    def test_parse_when2(self):
        query = "When did Rembrandts sing the theme song of Friends"
        # query = "Ghana population"
        parser = frank.query_parser.parser.Parser()
        output = parser.getNextSuggestion(query)
        print(output)

        self.assertEqual(output['template'], ['when', 'entity', 'verb', 'propclass', 'of', 'propclass'])



if __name__ == '__main__':
    unittest.main()
