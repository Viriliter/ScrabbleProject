import os
import unittest
from io import BytesIO

from ..dictionary import Dictionary
from game.utils import get_absolute_path

class TestDictionary(unittest.TestCase):

    def test_loads_words(self):
        dic = Dictionary("test")
        self.assertTrue(dic.add_word('A'))
        self.assertTrue(dic.add_word('ANT'))
        self.assertTrue(dic.add_word('TAN'))
        self.assertFalse(dic.add_word('ANT'))

        s = []
        dic.each_word(lambda w: s.append(w))
        self.assertEqual(s, ['A', 'ANT', 'TAN'])

        dic.add_word('ANT')
        s = []
        dic.each_word(lambda w: s.append(w))
        self.assertEqual(s, ['A', 'ANT', 'TAN'])

        self.assertTrue(dic.has_word('ANT'))
        self.assertFalse(dic.has_word('TNA'))

        dic.add_word('TA')
        dic.add_word('RANT')

        anags = dic.find_anagrams("nat ")
        self.assertEqual(anags, {
            'A': 'A',
            'ANT': 'ANT',
            'TA': 'TA',
            'TAN': 'TAN',
            'RANT': " ANT"
        })

    def test_loads_a_dictionary(self):
        dict_path = get_absolute_path('externals/dictionary/test/data/dictionary.dict')
        with open(os.path.join(os.path.dirname(__file__), 'data', dict_path), 'rb') as f:
            data = f.read()
        dic = Dictionary("test")
        dic.load_dawg(BytesIO(data))

        self.assertTrue(dic.has_word('LAZY'))
        self.assertFalse(dic.match("AXE"))
        self.assertEqual(dic.match("LAZY").letter, 'Y')

    def test_extends_a_dictionary(self):
        dict_path = get_absolute_path('externals/dictionary/test/data/dictionary.dict')
        with open(os.path.join(os.path.dirname(__file__), 'data', dict_path), 'rb') as f:
            data = f.read()
        dic = Dictionary("test")
        dic.load_dawg(BytesIO(data))

        self.assertTrue(dic.has_word("QUICK"))
        self.assertFalse(dic.has_word("AARDVAARK"))
        self.assertFalse(dic.has_sequence("VAAR"))

        dic.add_word("AARDVAARK")
        self.assertTrue(dic.has_sequence("VAAR"))

        dic.add_word("BISON")
        dic.add_word("BISONIC")

        self.assertTrue(dic.has_word("BISON"))
        self.assertTrue(dic.has_word("BISONIC"))

        self.assertTrue(dic.has_sequence("VAAR"))

    def test_builds_links(self):
        dic = Dictionary("test")
        dic.add_word('A')
        dic.add_word('ANT')
        dic.add_word('TAN')

        dic.add_links()

        s = dic.get_sequence_roots('N')

        self.assertEqual(len(s), 2)
        self.assertEqual(s[0].preNodes[0].letter, 'A')
        self.assertEqual(s[0].preLetters, ['A'])
        self.assertEqual(s[0].postNodes[0].letter, 'T')
        self.assertEqual(s[0].postLetters, ['T'])

        self.assertEqual(s[1].preNodes[0].letter, 'A')
        self.assertEqual(s[1].preLetters, ['A'])
        self.assertEqual(len(s[1].postNodes), 0)
        self.assertEqual(len(s[1].postLetters), 0)

    def test_hangmen(self):
        dict_path = get_absolute_path('externals/dictionary/test/data/dictionary.dict')
        with open(os.path.join(os.path.dirname(__file__), 'data', dict_path), 'rb') as f:
            data = f.read()
        dic = Dictionary("test")
        dic.load_dawg(BytesIO(data))

        self.assertEqual(dic.find_hangmen("H NGM N"), ['HANGMAN', 'HANGMEN', 'HUNGMAN', 'HUNGMEN'])
        self.assertEqual(dic.find_hangmen("H NGMEN"), ['HANGMEN', 'HUNGMEN'])
        self.assertEqual(dic.find_hangmen("H NGMENS"), [])

if __name__ == '__main__':
    unittest.main()
