import copy
from typing import List, Callable, Optional

class LetterNode:
    """
    @class LetterNode
    @description Letter node in a Dictionary. Each node has multiple links and helpers
    that trade off space for performance during word searches.
    Each LetterNode participates in two linked lists; the `next` pointer
    points to the next alternative to this letter when composing a word,
    while the `child` pointer points to the first in a chain of possible
    child nodes. For example, in a dictionary where we have the two words
    `NO`, `SO` and `SAD`:
    ```
      N -next-> S -next->
      |         |
    child     child
      |         |
      `-> O(e)  `-> A -next-> O(e)
                    |
                  child
                    |
                    D(e)
    ```
    where (e) indicates a node that is a valid end-of-word.
    The example is a tree; however the DAWG compressor will
    collapse letter sequences that are common to several words,
    to create a more optimal DAG.
    
    Once a Dictionary has been created and fully populated, it can be
    processed using `buildLists` to generate lists that support rapid
    navigation through the DAG without needing to traverse the node
    chains.
    """

    # Bit masks and constants
    END_OF_WORD_BIT_MASK = 0x1          # Bit mask for end-of-word marker
    END_OF_LIST_BIT_MASK = 0x2          # Bit mask for end-of-list marker
    CHILD_INDEX_SHIFT = 2               # Shift to create space for masks
    CHILD_INDEX_BIT_MASK = 0x3FFFFFFF   # Mask for child index, exclusing above bit masks

    def __init__(self, letter: str):
        # The letter at this node
        self.letter = letter
        self.next: 'LetterNode' = None              # Pointer to the next (alternative) node in this peer chain
        self.child: 'LetterNode' = None             # Pointer to the head of the child chain
        self.isEndOfWord = False                    # Is this the end of a valid word?
        self.preNodes: List['LetterNode'] = []      # List of nodes that link forward to this node
        self.preLetters: List['str'] = []           # List of letters that are in the nodes listed in preNodes
        self.postNodes: List['LetterNode'] = []     # List of nodes that are linked to from this node
        self.postLetters: List['str'] = []          # List of letters that are in the nodes listed in postNodes

    def each_word(self, s: str, cb: callable) -> None:
        """
        @brief Enumerate each word in the dictionary. Calls cb on each word.
        
        @param s: the word constructed so far
        @param cb: the callback
        """
        node: LetterNode = self
        while node:
            if node.isEndOfWord:
                cb(s + node.letter)
            if node.child:
                node.child.each_word(s + node.letter, cb)
            node = node.next

    def each_long_word(self, s: str, cb: callable) -> None:
        """
        @brief Enumerate each LONG word in the dictionary. A long word is one
        that has no child nodes i.e. cannot be extended by adding more
        letters to create a new word. Calls cb on each word.
        Caution this is NOT the same as dawg/TrieNode.eachWord.

        @param s: the word constructed so far
        @param cb: the callback
        """
        node: LetterNode  = self
        while node:
            if node.child:
                node.child.each_long_word(s + node.letter, cb)
            elif node.isEndOfWord:
                cb(s + node.letter, node)
            node = node.next

    def each_node(self, cb: callable) -> bool:
        """
        @brief Enumerate each node in the dictionary.
        Calls cb on each node, stops if cb returns false.
        
        @param cb: the callback
        @return: false if cb stops
        """
        node: LetterNode = self
        while node:
            if not cb(node):
                return False
            if node.child and not node.child.each_node(cb):
                return False
            node = node.next
        return True

    def add(self, word: str) -> bool:
        """
        @brief Add a letter sequence to this node. This is used to add
        whitelist nodes to a DAG.
        
        @param word: word being added
        @return: true if the word was added, false if it was already there
        """
        node = self
        added = False

        while node:
            if node.letter == word[0]:
                if len(word) == 1:
                    if not node.isEndOfWord:
                        added = True
                        node.isEndOfWord = True
                    return added
                word = word[1:]
                if node.child is None or node.child.letter > word[0]:
                    t = node.child
                    node.child = LetterNode(word[0])
                    added = True
                    node.child.next = t
                node = node.child
            elif not node.next or node.next.letter > word[0]:
                t = node.next
                node.next = LetterNode(word[0])
                added = True
                node.next.next = t
            else:
                node = node.next
                
        return added

    def build_lists(self, nodeBefore: 'LetterNode | None' = None) -> None:
        """
        Build forward and backward lists to allow us to navigate
        in both directions - forward through words, and backwards too.
        This has to be done from the root of the DAG, and has to be
        re-done if the DAG is modified.
        """
        node: LetterNode = self
        while node is not None:
            node.preNodes = []
            node.preLetters = []
            node.postNodes = []
            node.postLetters = []
            if nodeBefore is not None:
                node.preNodes.append(nodeBefore)
                node.preLetters.append(nodeBefore.letter)
                nodeBefore.postNodes.append(node)
                nodeBefore.postLetters.append(node.letter)
            
            if node.child is not None:
                node.child.build_lists(node)
            node = node.next

    def match(self, chars: str, index: int) -> Optional['LetterNode']:
        """
        @brief Find the letter node at the end of the subtree that matches
        the last character in chars, even if it"s not isEndOfWord
        
        @param chars: a string of characters that may
        be the root of a word
        @param index: index into chars
        @return: node found, or undefined
        """
        node: LetterNode = self
        while node is not None:
            if node.letter == chars[index]:
                if index == len(chars) - 1:
                    return node
                if node.child is not None:
                    return node.child.match(chars, index + 1)
            node = node.next
        return None

    def hangmen(self, chars: str, index: int, word: str, word_list: Optional[List[str]] = None) -> None:
            """
            @brief Find all words below this node that match the character sequence
            passed from a given point in the sequence.
            " " acts as a wildcard.
            
            @param chars: the character sequence to match
            @param index: index into chars
            @param word: word asembled so far
            @param list: list of words found
            """
            node = self
            ci = chars[index]
            while node:
                if ci == " " or node.letter == ci:
                    if node.isEndOfWord and index == len(chars) - 1:
                        word_list.append(word + node.letter)
                    if index < len(chars) - 1 and node.child:
                        node.child.hangmen(chars, index + 1, word + node.letter, word_list)
                node = node.next

    def find_words_that_use(self, chars: List[str], real_word: str, blanked_word: str, found_words: List[str]) -> dict[str, str]:
        """
        @brief Find words that can be made from a sorted set of letters.

        @param chars: The available set of characters.
        @param real_word: The string built so far in this recursion.
        @param blanked_word: The string built using spaces for blanks (if they are used).
        @return: A dictionary of found words, with the real word as the key
                 and the word with blanks as the value.
        """
        node: LetterNode = self

        chars_ = copy.deepcopy(chars)

        while node:
            # is this character available from chars?
            # Only use blank if no other choice
            i = -1
            try:
                i = chars_.index(node.letter)
            except ValueError:
                pass  # character not found, try blank space

            if i < 0:
                try:
                    i = chars_.index(" ")
                except ValueError:
                    pass  # blank space also not found, continue

            if i >= 0:
                match = chars_[i]

                # The char is available from chars.
                # Is this then a word?
                if node.isEndOfWord:
                    # A word is found
                    found_words[real_word + node.letter] = blanked_word + match

                if len(chars_) > 1:
                    # Cut the matched letter out of chars and recurse
                    # over our child node chain
                    chars_.pop(i)
                    child = node.child
                    while child:
                        child.find_words_that_use(
                            chars_,
                            real_word + node.letter,
                            blanked_word + match,
                            found_words)
                        child = child.next
                    chars_.insert(i, match)

            node = node.next

    def decode(self, i: int, numb: int) -> 'LetterNode':
        """
        @brief Decode node information encoded in an integer in a
        serialised Dictionary.

        @param i: index of node in node list
        @param numb: encoded node
        @return: this
        """
        if (numb & LetterNode.END_OF_WORD_BIT_MASK) != 0:
            self.isEndOfWord = True
        if (numb & LetterNode.END_OF_LIST_BIT_MASK) == 0:
            self.next = i + 1
        if ((numb >> LetterNode.CHILD_INDEX_SHIFT) & LetterNode.CHILD_INDEX_BIT_MASK) > 0:
            self.child = (numb >> LetterNode.CHILD_INDEX_SHIFT) & LetterNode.CHILD_INDEX_BIT_MASK
        return self
