import unittest

from externals.dictionary.letter_node import LetterNode

class TestLetterNode(unittest.TestCase):
    def test_each_word(self):
        root = LetterNode("A")
        self.assertTrue(root.add("MAUL"))
        self.assertTrue(root.add("MEAT"))
        self.assertTrue(root.add("EATS"))
        self.assertTrue(root.add("ATE"))
        words = []
        root.each_word("", words.append)
        self.assertEqual(words, ["ATE", "EATS", "MAUL", "MEAT"])

    def test_each_node(self):
        root = LetterNode("A")
        self.assertTrue(root.add("AST"))
        self.assertTrue(root.add("AAR"))
        words = []
        root.each_word("", words.append)
        self.assertEqual(words, ["AAR", "AST"])

        # Check callback returning False stops traversal
        result = []
        root.each_node(lambda n: result.append(n.letter) or False)
        self.assertEqual(result, ["A"])

        # Scan until reaching the first "T"
        result = []
        root.each_node(lambda n: result.append(n.letter) or n.letter != "T")
        self.assertEqual(result, ["A", "A", "R", "S", "T"])

    def test_each_long_word(self):
        root = LetterNode("A")
        self.assertTrue(root.add("A"))
        self.assertTrue(root.add("ANT"))
        self.assertTrue(root.add("TAN"))
        self.assertTrue(root.add("TA"))
        self.assertTrue(root.add("RANT"))
        self.assertTrue(root.add("AN"))
        words = []
        root.each_long_word("", words.append)
        self.assertEqual(words, ["ANT", "RANT", "TAN"])

    def test_match(self):
        root = LetterNode("A")
        self.assertTrue(root.add("A"))
        self.assertTrue(root.add("ANT"))
        self.assertTrue(root.add("TAN"))
        self.assertTrue(root.add("TA"))
        self.assertTrue(root.add("TEA"))
        self.assertTrue(root.add("RANT"))
        self.assertTrue(root.add("AN"))
        found = root.match("TA", 0)
        self.assertIsNotNone(found)
        self.assertEqual(found.letter, "A")

    def test_build_lists(self):
        root = LetterNode("A")
        self.assertTrue(root.add("TAN"))
        self.assertTrue(root.add("TA"))
        self.assertTrue(root.add("TEA"))
        self.assertTrue(root.add("TAT"))
        root.build_lists()
        found = root.match("TA", 0)
        self.assertEqual(len(found.preNodes), 1)
        self.assertEqual(found.preNodes[0].letter, "T")
        self.assertEqual(len(found.postNodes), 2)
        self.assertEqual(found.postNodes[0].letter, "N")
        self.assertEqual(found.postNodes[1].letter, "T")

    def test_find_words_that_use(self):
        root = LetterNode("A")
        self.assertTrue(root.add("MAUL"))
        self.assertTrue(root.add("MEAT"))
        self.assertTrue(root.add("EATS"))
        self.assertTrue(root.add("ATE"))
        found = {}
        root.find_words_that_use(["A"], "", "", found)
        self.assertEqual(found, {})
        root.find_words_that_use(["A", "T"], "", "", found)
        self.assertEqual(found, {})
        root.find_words_that_use(["A", "T", "E"], "", "", found)
        self.assertEqual(found, {"ATE": "ATE"})

    def test_decode(self):
        numb = (66 << LetterNode.CHILD_INDEX_SHIFT) | LetterNode.END_OF_WORD_BIT_MASK
        node = LetterNode("X")
        node.decode(99, numb)
        self.assertTrue(node.isEndOfWord)
        self.assertEqual(node.letter, "X")
        self.assertEqual(node.next, 100)
        self.assertEqual(node.child, 66)

        node = LetterNode("X")
        numb = (666 << LetterNode.CHILD_INDEX_SHIFT) | LetterNode.END_OF_LIST_BIT_MASK
        node.decode(99, numb)
        self.assertEqual(node.child, 666)
        self.assertIsNone(node.next)

if __name__ == "__main__":
    unittest.main()