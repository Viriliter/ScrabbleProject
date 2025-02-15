from .letter_node import LetterNode

class TrieNode:
    node_ids = 0

    def __init__(self, letter, next_node=None, is_word_ending=False, starter_depth=0, is_first_child=False):
        self.letter = letter
        self.next = next_node
        self.is_end_of_word = is_word_ending
        self.max_child_depth = starter_depth
        self.is_first_child = is_first_child
        self.id = TrieNode.node_ids
        TrieNode.node_ids += 1
        self.child = None
        self.is_pruned = False
        self.number_of_children = 0
        self.index = -1

    def __str__(self, deeply=False):
        simpler = f"{{{self.id} {self.letter}}}"
        if self.is_end_of_word:
            simpler += "."
        if self.child:
            simpler += "+"
            if deeply:
                simpler += self.child.__str__(deeply)
        simpler += "}"
        if self.next:
            simpler += "-"
            if deeply:
                simpler += self.next.__str__(deeply)
        return simpler

    def prune(self):
        self.is_pruned = True
        result = 0
        if self.next:
            result += self.next.prune()
        if self.child:
            result += self.child.prune()
        return result + 1

    def each_word(self, nodes, cb):
        nodes.append(self)
        if self.is_end_of_word:
            cb(nodes)
        if self.child:
            self.child.each_word(nodes, cb)
        nodes.pop()
        if self.next:
            self.next.each_word(nodes, cb)

    def each_node(self, cb):
        cb(self)
        if self.next:
            self.next.each_node(cb)
        if self.child:
            self.child.each_node(cb)

    def find_child(self, this_letter):
        result = self.child
        while result:
            if result.letter == this_letter:
                return result
            if result.letter > this_letter:
                break
            result = result.next
        return None

    def insert_child(self, this_letter, word_ender, start_depth):
        self.number_of_children += 1
        if not self.child:
            self.child = TrieNode(this_letter, None, word_ender, start_depth, True)
            return
        if self.child.letter > this_letter:
            self.child.is_first_child = False
            self.child = TrieNode(this_letter, self.child, word_ender, start_depth, True)
            return
        child = self.child
        while child.next:
            if child.next.letter > this_letter:
                break
            child = child.next
        child.next = TrieNode(this_letter, child.next, word_ender, start_depth, False)

    def same_subtrie(self, other):
        if other == self:
            return True
        if not other or other.letter != self.letter or other.max_child_depth != self.max_child_depth or \
           other.number_of_children != self.number_of_children or other.is_end_of_word != self.is_end_of_word or \
           (not self.child and other.child) or (self.child and not other.child) or \
           (not self.next and other.next) or (self.next and not other.next):
            return False
        if self.child and not self.child.same_subtrie(other.child):
            return False
        if self.next and not self.next.same_subtrie(other.next):
            return False
        return True

    def find_same_subtrie(self, red):
        for x in range(len(red[self.max_child_depth])):
            if self.same_subtrie(red[self.max_child_depth][x]):
                break
        if red[self.max_child_depth][x].is_pruned:
            raise ValueError("Same subtrie equivalent is pruned!")
        return red[self.max_child_depth][x]

    def replace_redundant_nodes(self, red):
        if not self.next and not self.child:
            return 0
        trimmed = 0
        if self.child:
            if self.child.is_pruned:
                self.child = self.child.find_same_subtrie(red)
                trimmed += 1
            else:
                trimmed += self.child.replace_redundant_nodes(red)
        if self.next:
            trimmed += self.next.replace_redundant_nodes(red)
        return trimmed

    def encode(self):
        array = [ord(self.letter)]
        numb = 0
        if self.child:
            numb |= (self.child.index << LetterNode.CHILD_INDEX_SHIFT)
        if self.is_end_of_word:
            numb |= LetterNode.END_OF_WORD_BIT_MASK
        if not self.next:
            numb |= LetterNode.END_OF_LIST_BIT_MASK
        array.append(numb)
        return array
